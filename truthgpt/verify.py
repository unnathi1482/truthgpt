from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from truthgpt.search import Evidence

DEFAULT_NLI_MODEL = "MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli"

_tokenizer: Optional[AutoTokenizer] = None
_model: Optional[AutoModelForSequenceClassification] = None


@dataclass
class VerificationResult:
    claim: str
    verdict: str  # "verified" | "contradicted" | "unverified"
    confidence: float
    evidence: Optional[Evidence]
    scores: Dict[str, float]  # {"ENTAILMENT": x, "NEUTRAL": y, "CONTRADICTION": z}


def _get_nli(model_name: str = DEFAULT_NLI_MODEL) -> Tuple[AutoTokenizer, AutoModelForSequenceClassification]:
    global _tokenizer, _model
    if _tokenizer is None or _model is None:
        _tokenizer = AutoTokenizer.from_pretrained(model_name)
        _model = AutoModelForSequenceClassification.from_pretrained(model_name)
        _model.eval()
    return _tokenizer, _model


def _softmax_probs(logits: torch.Tensor) -> torch.Tensor:
    return torch.softmax(logits, dim=-1)


def nli_scores(premise: str, hypothesis: str, model_name: str = DEFAULT_NLI_MODEL) -> Dict[str, float]:
    tokenizer, model = _get_nli(model_name)

    inputs = tokenizer(
        premise,
        hypothesis,
        truncation=True,
        max_length=512,
        return_tensors="pt",
    )

    with torch.no_grad():
        out = model(**inputs)
        probs = _softmax_probs(out.logits)[0]

    id2label = {int(k): v for k, v in model.config.id2label.items()}
    scores = {id2label[i].upper(): float(probs[i].cpu().item()) for i in range(probs.shape[0])}

    # Ensure keys exist (some models use different casing)
    scores.setdefault("ENTAILMENT", 0.0)
    scores.setdefault("NEUTRAL", 0.0)
    scores.setdefault("CONTRADICTION", 0.0)

    return scores


def verify_claim(
    claim: str,
    evidence_list: List[Evidence],
    model_name: str = DEFAULT_NLI_MODEL,
    entail_threshold: float = 0.65,
    contra_threshold: float = 0.65,
    margin: float = 0.15,
) -> VerificationResult:
    """
    Verify a claim against evidence snippets.

    Important: We track BEST-ENTAILMENT evidence and BEST-CONTRADICTION evidence separately.
    Then we choose the verdict and return the matching evidence + scores.
    """
    best_entail = -1.0
    best_entail_scores: Optional[Dict[str, float]] = None
    best_entail_evidence: Optional[Evidence] = None

    best_contra = -1.0
    best_contra_scores: Optional[Dict[str, float]] = None
    best_contra_evidence: Optional[Evidence] = None

    for e in evidence_list:
        premise = _combine_premise(e)
        if len(premise.strip()) < 20:
            continue

        scores = nli_scores(premise=premise, hypothesis=claim, model_name=model_name)
        entail = float(scores.get("ENTAILMENT", 0.0))
        contra = float(scores.get("CONTRADICTION", 0.0))

        if entail > best_entail:
            best_entail = entail
            best_entail_scores = scores
            best_entail_evidence = e

        if contra > best_contra:
            best_contra = contra
            best_contra_scores = scores
            best_contra_evidence = e

    # If no evidence worked at all
    if best_entail_scores is None and best_contra_scores is None:
        return VerificationResult(
            claim=claim,
            verdict="unverified",
            confidence=0.0,
            evidence=None,
            scores={"ENTAILMENT": 0.0, "NEUTRAL": 0.0, "CONTRADICTION": 0.0},
        )

    # Decide using the SAME evidence that produced the score
    verdict = "unverified"

    # Candidate: verified
    if best_entail_scores is not None:
        entail = float(best_entail_scores.get("ENTAILMENT", 0.0))
        contra_same = float(best_entail_scores.get("CONTRADICTION", 0.0))
        if entail >= entail_threshold and (entail - contra_same) >= margin:
            verdict = "verified"
            return VerificationResult(
                claim=claim,
                verdict=verdict,
                confidence=entail,
                evidence=best_entail_evidence,
                scores=best_entail_scores,
            )

    # Candidate: contradicted
    if best_contra_scores is not None:
        contra = float(best_contra_scores.get("CONTRADICTION", 0.0))
        entail_same = float(best_contra_scores.get("ENTAILMENT", 0.0))
        if contra >= contra_threshold and (contra - entail_same) >= margin:
            verdict = "contradicted"
            return VerificationResult(
                claim=claim,
                verdict=verdict,
                confidence=contra,
                evidence=best_contra_evidence,
                scores=best_contra_scores,
            )

    # Otherwise: unverified; show best-entail evidence (most relevant) if available
    if best_entail_scores is not None:
        conf = float(max(best_entail_scores.get("ENTAILMENT", 0.0), best_entail_scores.get("CONTRADICTION", 0.0)))
        return VerificationResult(
            claim=claim,
            verdict="unverified",
            confidence=conf,
            evidence=best_entail_evidence,
            scores=best_entail_scores,
        )

    # Fallback to best-contradiction evidence
    conf = float(max(best_contra_scores.get("ENTAILMENT", 0.0), best_contra_scores.get("CONTRADICTION", 0.0)))  # type: ignore[arg-type]
    return VerificationResult(
        claim=claim,
        verdict="unverified",
        confidence=conf,
        evidence=best_contra_evidence,
        scores=best_contra_scores or {"ENTAILMENT": 0.0, "NEUTRAL": 0.0, "CONTRADICTION": 0.0},
    )


def _combine_premise(e: Evidence) -> str:
    bits = []
    if e.title:
        bits.append(e.title.strip())
    if e.snippet:
        bits.append(e.snippet.strip())
    if e.url:
        bits.append(f"Source: {e.url}")
    return " — ".join(bits)
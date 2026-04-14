from __future__ import annotations

from dataclasses import dataclass
from typing import List, Set
import re

from truthgpt.llm import generate_answer
from truthgpt.fallback_answer import fallback_answer_from_evidence
from truthgpt.claims import extract_claims
from truthgpt.search import Evidence, gather_evidence, wikipedia_search
from truthgpt.verify import VerificationResult, verify_claim


@dataclass
class PipelineOutput:
    question: str
    answer: str
    claims: List[str]
    results: List[VerificationResult]
    verified_ratio: float
    sources: List[str]
    topic_title: str
    topic_query: str
    used_fallback: bool


def _merge_evidence(*lists: List[Evidence]) -> List[Evidence]:
    merged: List[Evidence] = []
    seen = set()
    for lst in lists:
        for e in lst:
            key = (e.source, e.url, e.title, e.snippet)
            if key in seen:
                continue
            seen.add(key)
            merged.append(e)
    return merged


def _topic_query_from_question(question: str) -> str:
    """
    Heuristic: strip instruction words so Wikipedia search gets a clean topic query.
    """
    q = (question or "").strip()

    q = re.sub(
        r"^\s*(tell me about|explain|what is|who is|give me an overview of)\s+",
        "",
        q,
        flags=re.I,
    )

    q = re.sub(r"\s+in\s+\d+\s*[-–]\s*\d+\s+bullet\s+points.*$", "", q, flags=re.I)
    q = re.sub(r"\s+in\s+\d+\s+bullet\s+points.*$", "", q, flags=re.I)
    q = re.sub(r"\s+in\s+bullet\s+points.*$", "", q, flags=re.I)
    q = re.sub(r"\s+in\s+\d+\s*[-–]\s*\d+\s+sentences?.*$", "", q, flags=re.I)
    q = re.sub(r"\s+in\s+\d+\s+sentences?.*$", "", q, flags=re.I)

    q = q.strip().strip(" .?!\"'")
    return q or (question or "").strip()


def _anchor_terms(topic_title: str) -> List[str]:
    terms = re.findall(r"[A-Za-z0-9]+", (topic_title or "").lower())
    return [t for t in terms if len(t) >= 4]


def _is_relevant(e: Evidence, anchor: List[str]) -> bool:
    """
    Keep only evidence that mentions the topic terms.
    If topic has 2+ meaningful terms, require 2 hits; else require 1 hit.
    """
    if not anchor:
        return True

    text = f"{e.title} {e.snippet}".lower()
    hits = sum(1 for t in set(anchor) if t in text)
    required = 2 if len(set(anchor)) >= 2 else 1
    return hits >= required


def _detect_topic_title(topic_query: str) -> str:
    """
    Pick the top Wikipedia title for the cleaned topic query.
    """
    try:
        top = wikipedia_search(topic_query, limit=1)
        if top:
            return top[0].title or ""
    except Exception:
        pass
    return ""


def run_pipeline(
    question: str,
    max_claims: int = 8,
    evidence_per_source: int = 3,
) -> PipelineOutput:
    # 0) Topic detection
    topic_query = _topic_query_from_question(question)
    topic_title = _detect_topic_title(topic_query)
    anchor = _anchor_terms(topic_title)

    # 1) Gather base evidence FIRST (so fallback can use it)
    base_query = topic_title if topic_title else topic_query
    base_evidence_raw = gather_evidence(base_query, per_source=evidence_per_source)
    base_evidence = [e for e in base_evidence_raw if _is_relevant(e, anchor)]

    # 2) Generate answer (Groq) OR fallback to evidence-only answer
    used_fallback = False
    try:
        answer = generate_answer(question)
    except Exception:
        used_fallback = True
        answer = fallback_answer_from_evidence(
            base_evidence,
            topic_title=topic_title,
            max_bullets=6,
        )

    # 3) Extract claims
    claims = extract_claims(answer, max_claims=max_claims)

    results: List[VerificationResult] = []
    sources_set: Set[str] = set()

    for e in base_evidence:
        if e.url:
            sources_set.add(e.url)

    # 4) For each claim: anchored evidence + verify
    for claim in claims:
        claim_query = f"{topic_title} {claim}" if topic_title else f"{topic_query} {claim}"
        claim_evidence_raw = gather_evidence(claim_query, per_source=evidence_per_source)
        claim_evidence = [e for e in claim_evidence_raw if _is_relevant(e, anchor)]

        evidence = _merge_evidence(base_evidence, claim_evidence)

        for e in claim_evidence:
            if e.url:
                sources_set.add(e.url)

        res = verify_claim(claim, evidence)
        results.append(res)

        if res.evidence and res.evidence.url:
            sources_set.add(res.evidence.url)

    # 5) Verified ratio
    verified_ratio = (sum(1 for r in results if r.verdict == "verified") / len(results)) if results else 0.0

    return PipelineOutput(
        question=question,
        answer=answer,
        claims=claims,
        results=results,
        verified_ratio=verified_ratio,
        sources=sorted(sources_set),
        topic_title=topic_title,
        topic_query=topic_query,
        used_fallback=used_fallback,
    )
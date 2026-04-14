from __future__ import annotations

import re
from typing import List, Optional

from truthgpt.search import Evidence


_SENT_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def _clean_sentence(s: str) -> str:
    s = (s or "").strip()
    s = re.sub(r"\[\d+\]", "", s)  # remove [1], [2]...
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _sentences(text: str) -> List[str]:
    text = (text or "").strip()
    if not text:
        return []
    parts = _SENT_SPLIT_RE.split(text)
    out: List[str] = []
    for p in parts:
        p = _clean_sentence(p)
        if len(p) < 25:
            continue
        out.append(p)
    return out


def _pick_best_snippet(evidence: List[Evidence], prefer_title: Optional[str] = None) -> Optional[Evidence]:
    """
    Prefer Wikipedia evidence matching the detected topic title.
    Otherwise pick the first Wikipedia evidence. Otherwise pick the first evidence.
    """
    if not evidence:
        return None

    wiki = [
        e for e in evidence
        if (e.source or "").lower() == "wikipedia" and (e.snippet or "").strip()
    ]

    if prefer_title:
        for e in wiki:
            if (e.title or "").strip().lower() == prefer_title.strip().lower():
                return e

    if wiki:
        return wiki[0]

    for e in evidence:
        if (e.snippet or "").strip():
            return e

    return None


def fallback_answer_from_evidence(
    evidence: List[Evidence],
    topic_title: Optional[str] = None,
    max_bullets: int = 6,
) -> str:
    """
    Build a simple bullet-point answer directly from evidence (no LLM).
    Used when Groq is unreachable on Hugging Face.
    """
    best = _pick_best_snippet(evidence, prefer_title=topic_title)
    if not best:
        return "• Uncertain: Could not find enough public evidence to answer this question."

    sents = _sentences(best.snippet)
    if not sents:
        return "• Uncertain: Could not extract clear factual sentences from the available evidence."

    bullets = sents[: max(1, min(max_bullets, len(sents)))]
    return "\n".join(f"• {b}" for b in bullets)
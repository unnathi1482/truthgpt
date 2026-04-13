import re
from typing import List


_BULLET_PREFIX_RE = re.compile(r"^\s*([-*•]|\d+[\).])\s+")


def _clean_line(line: str) -> str:
    line = line.strip()
    line = _BULLET_PREFIX_RE.sub("", line)
    line = re.sub(r"\s+", " ", line)
    return line.strip(" -–—\t")


def extract_claims(text: str, max_claims: int = 12) -> List[str]:
    """
    MVP claim extraction:
    - Split by lines and sentence boundaries.
    - Remove bullets/numbering.
    - Keep short, checkable statements.
    """
    if not text or not text.strip():
        return []

    # Normalize newlines
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()

    candidates: List[str] = []

    # First split by lines (helps when model outputs bullets)
    for raw_line in text.split("\n"):
        line = _clean_line(raw_line)
        if not line:
            continue

        # Then split line into sentences (simple rule-based)
        parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", line)
        for p in parts:
            p = _clean_line(p)
            if not p:
                continue
            # Filter out very short fragments
            if len(p) < 20:
                continue
            candidates.append(p)

    # Deduplicate while preserving order
    seen = set()
    claims: List[str] = []
    for c in candidates:
        key = c.lower()
        if key in seen:
            continue
        seen.add(key)
        claims.append(c)
        if len(claims) >= max_claims:
            break

    return claims
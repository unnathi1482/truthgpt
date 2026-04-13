from __future__ import annotations

import re
from typing import List


def bullets_to_list(text: str) -> List[str]:
    """
    Convert bullet-point LLM output into a clean Python list of strings.
    Handles: •, -, *, numbered lists (1. 2. etc.)
    """
    if not text or not text.strip():
        return []

    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")

    result: List[str] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Remove bullet prefixes
        line = re.sub(r"^\s*(•|-|\*|\d+[\).])\s*", "", line).strip()

        if len(line) < 5:
            continue

        result.append(line)

    return result


def format_answer_for_display(text: str) -> str:
    """
    Convert bullet-point LLM output into a clean markdown list for Streamlit.
    """
    items = bullets_to_list(text)
    if not items:
        return text  # fallback: return as-is

    return "\n".join(f"- {item}" for item in items)
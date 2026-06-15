# -*- coding: utf-8 -*-
"""
Answer Extractor — 4-tier regex extraction chain.

Conforms to AGENTS.md §2.3:
  Tier 1: Single valid character
  Tier 2: Regex match against known Vietnamese/English answer patterns
  Tier 3: First valid uppercase letter in raw output
  Tier 4: Absolute fallback → 'A'

NEVER returns empty string. NEVER returns invalid letter. NEVER raises exceptions.
"""
import re
from typing import Optional

# Precompiled regex — matches answer indicators in Vietnamese and English
_ANSWER_RE = re.compile(
    r'(?:Đáp\s*án|Answer|Câu\s*trả\s*lời|Chọn)\s*[:：]?\s*([A-J])\b'
    r'|'
    r'(?:^|\n)\s*([A-J])\s*[\.\)\]]\s',
    re.IGNORECASE
)


def extract_answer(raw: str, num_choices: int = 4) -> str:
    """
    4-tier extraction: single-char → regex → first-valid-letter → fallback 'A'.

    Args:
        raw: Raw model output string. Handles None and empty string gracefully.
        num_choices: Number of valid choices (2–10). Clamps valid set to {A..chr(64+num_choices)}.

    Returns:
        A single uppercase letter from the valid set. Guaranteed non-empty.
    """
    # Clamp num_choices to [2, 10] and build the valid set
    num_choices = max(2, min(num_choices, 10))
    valid = {chr(65 + i) for i in range(num_choices)}

    # Gracefully handle None or non-string input
    if raw is None:
        return "A"
    if not isinstance(raw, str):
        try:
            raw = str(raw)
        except Exception:
            return "A"

    s = raw.strip()

    # Tier 1: Output is already a single valid character
    if len(s) == 1 and s.upper() in valid:
        return s.upper()

    # Tier 2: Regex match against known answer patterns
    for m in _ANSWER_RE.finditer(raw):
        letter = (m.group(1) or m.group(2) or "").upper()
        if letter in valid:
            return letter

    # Tier 3: First valid uppercase letter in the output
    for ch in raw:
        if ch.upper() in valid:
            return ch.upper()

    # Tier 4: Absolute fallback — never return empty
    return "A"

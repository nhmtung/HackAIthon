# -*- coding: utf-8 -*-
"""
Answer Extractor — 5-tier regex extraction chain (CoT-enhanced).

Conforms to AGENTS.md §2.3 with Phase 3 CoT extensions:
  Tier 1: Single valid character (model returned just a letter)
  Tier 2: Last "Đáp án: X" pattern (for CoT output — answer at end)
  Tier 3: Regex match against known Vietnamese/English answer patterns
  Tier 4: First valid uppercase letter in raw output
  Tier 5: Absolute fallback → 'A'

NEVER returns empty string. NEVER returns invalid letter. NEVER raises exceptions.
"""
import re
from typing import Optional

__all__ = ["extract_answer"]

# Precompiled regex — matches answer indicators in Vietnamese and English
_ANSWER_RE = re.compile(
    r'(?:Đáp\s*án|Answer|Câu\s*trả\s*lời|Chọn)\s*[:：]?\s*([A-J])\b'
    r'|'
    r'(?:^|\n)\s*([A-J])\s*[\.\)\]]\s',
    re.IGNORECASE
)

# CoT-specific: match the LAST occurrence of "Đáp án: X" in reasoning output
_COT_FINAL_ANSWER_RE = re.compile(
    r'(?:Đáp\s*án|Answer|Kết\s*luận|Vậy\s*đáp\s*án)\s*[:：]?\s*\**\s*([A-J])\b',
    re.IGNORECASE
)

# Match a standalone letter at the very end of the output
_TRAILING_LETTER_RE = re.compile(
    r'[\s\n:：\.\)]*([A-J])\s*[\.\)]*\s*$',
    re.IGNORECASE
)


def extract_answer(raw: str, num_choices: int = 4) -> str:
    """
    5-tier extraction: single-char → CoT-final-answer → regex → first-valid-letter → fallback 'A'.

    Enhanced for Phase 3 CoT prompts where the model produces reasoning text
    followed by a final answer line like "Đáp án: B".

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

    # Tier 2: CoT-aware — find the LAST "Đáp án: X" pattern (answer after reasoning)
    # This is critical for CoT mode where reasoning comes first, answer at end
    cot_matches = list(_COT_FINAL_ANSWER_RE.finditer(raw))
    if cot_matches:
        # Take the LAST match (the final answer after reasoning)
        last_match = cot_matches[-1]
        letter = last_match.group(1).upper()
        if letter in valid:
            return letter

    # Tier 2b: Check for a trailing standalone letter at the end of output
    trailing_match = _TRAILING_LETTER_RE.search(raw)
    if trailing_match:
        letter = trailing_match.group(1).upper()
        if letter in valid:
            return letter

    # Tier 3: Regex match against known answer patterns (first occurrence)
    for m in _ANSWER_RE.finditer(raw):
        letter = (m.group(1) or m.group(2) or "").upper()
        if letter in valid:
            return letter

    # Tier 4: First valid uppercase letter in the output
    for ch in raw:
        if ch.upper() in valid:
            return ch.upper()

    # Tier 5: Absolute fallback — never return empty
    return "A"

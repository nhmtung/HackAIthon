# -*- coding: utf-8 -*-
"""
Main prompt builder module that interfaces with prompt templates and the router.
"""
from typing import List
from src.utils.prompt_templates import build_prompt_by_mode
from src.utils.prompt_router import build_routed_prompt

def build_prompt(question: str, choices: List[str], mode: str = "zero_shot") -> str:
    """
    Generates MCQ prompts dynamically based on prompt mode:
    - 'zero_shot' (baseline)
    - 'few_shot'
    - 'cot' (chain of thought)
    - 'routed' (heuristic router)
    - 'mixed_lang' (Vietnamese + English)
    """
    if mode == "routed":
        return build_routed_prompt(question, choices)
    else:
        return build_prompt_by_mode(question, choices, mode=mode)

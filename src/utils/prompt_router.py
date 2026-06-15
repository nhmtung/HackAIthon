# -*- coding: utf-8 -*-
"""
Question type routing module.
"""
import re
import logging
from typing import Literal

logger = logging.getLogger(__name__)

def detect_question_type(question: str) -> Literal['rag', 'math', 'factual']:
    """
    Heuristically detect the type of question based on common keywords/formatting.
    """
    q_lower = question.lower()
    
    # 1. RAG indicators
    if "đoạn thông tin:" in q_lower or "tiêu đề:" in q_lower or "title:" in q_lower or "nội dung:" in q_lower:
        return 'rag'
        
    # 2. Math indicators: LaTeX syntax or arithmetic keywords
    math_patterns = [
        r'\$',                # inline or block LaTeX math delimiter
        r'\\frac',            # LaTeX fraction
        r'\\sqrt',            # LaTeX square root
        r'\^',                # superscript/exponents
        r'\\times',           # LaTeX multiplication sign
        r'\\cdot',            # LaTeX dot multiplication
        r'\\pm',              # LaTeX plus-minus
        r'\\alpha',           # Greek letter alpha
        r'\\beta',            # Greek letter beta
        r'\\pi',              # Greek letter pi
        r'\\Delta',           # Delta symbol
        r'\\theta',           # theta symbol
        r'\\in\b',            # belongs to symbol
        r'\\rightarrow',      # arrow
        r'\\approx',          # approx equal
        r'\bmath\b',          # math keyword
        r'bằng bao nhiêu',    # common math question pattern
        r'tính diện tích',    # geometry
        r'tính thể tích',     # geometry
        r'tính giá trị',      # calculation
        r'tính đạo hàm',      # calculus
        r'tích phân',         # calculus
        r'phương trình',      # equation
        r'hệ phương trình',   # system of equations
    ]
    for pattern in math_patterns:
        if re.search(pattern, question):
            return 'math'
            
    # 3. Default to factual
    return 'factual'

def build_routed_prompt(question: str, choices: list[str]) -> str:
    """
    Build prompt using heuristic-based routing.
    - RAG -> few_shot (Template B)
    - Math -> cot (Template C, chain-of-thought)
    - Factual -> few_shot (Template B)
    """
    qtype = detect_question_type(question)
    logger.debug(f"Question routed to type: {qtype}")
    
    if qtype == 'math':
        from src.utils.prompt_templates import build_cot_prompt
        return build_cot_prompt(question, choices)
    else:  # 'rag' or 'factual'
        from src.utils.prompt_templates import build_few_shot_prompt
        return build_few_shot_prompt(question, choices)

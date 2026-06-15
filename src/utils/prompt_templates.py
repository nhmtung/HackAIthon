# -*- coding: utf-8 -*-
"""
Prompt Templates definition module.
"""
from typing import List

def _format_choices(choices: List[str]) -> str:
    """Format MCQ choices dynamically (A, B, C, D, ...)."""
    options_text = []
    for i, choice in enumerate(choices):
        label = chr(65 + i)
        options_text.append(f"{label}. {choice}")
    return "\n".join(options_text)

def build_zero_shot_prompt(question: str, choices: List[str]) -> str:
    """Template A: Zero-Shot (Baseline)"""
    choices_formatted = _format_choices(choices)
    return (
        "Bạn là trợ lý AI. Hãy chọn đáp án đúng nhất cho câu hỏi sau. "
        "Chỉ trả lời bằng MỘT chữ cái duy nhất (ví dụ: A, B, C, D) đại diện cho đáp án đúng. "
        "Không giải thích, không viết thêm bất kỳ từ nào khác ngoài chữ cái đáp án.\n\n"
        f"Câu hỏi: {question}\n\n"
        "Các lựa chọn:\n"
        f"{choices_formatted}\n\n"
        "Đáp án:"
    )

def build_few_shot_prompt(question: str, choices: List[str]) -> str:
    """Template B: Few-Shot (2 examples: one RAG-style, one math-style)"""
    choices_formatted = _format_choices(choices)
    return (
        "Bạn là trợ lý AI chuyên trả lời câu hỏi trắc nghiệm. Dưới đây là ví dụ:\n\n"
        "Ví dụ 1:\n"
        "Câu hỏi: Đoạn thông tin: Năm 1945, Việt Nam tuyên bố độc lập. Hỏi: Sự kiện tuyên bố độc lập của Việt Nam diễn ra vào năm nào?\n"
        "A. 1944\n"
        "B. 1945\n"
        "C. 1946\n"
        "D. 1950\n"
        "Đáp án: B\n\n"
        "Ví dụ 2:\n"
        "Câu hỏi: Tính 2 + 3 * 4 = ?\n"
        "A. 14\n"
        "B. 20\n"
        "C. 24\n"
        "D. 10\n"
        "Đáp án: A\n\n"
        "Bây giờ trả lời câu hỏi sau. Chỉ ghi đáp án (một chữ cái):\n"
        f"Câu hỏi: {question}\n\n"
        "Các lựa chọn:\n"
        f"{choices_formatted}\n\n"
        "Đáp án:"
    )

def build_cot_prompt(question: str, choices: List[str]) -> str:
    """Template C: Chain-of-Thought (CoT)"""
    choices_formatted = _format_choices(choices)
    return (
        "Bạn là trợ lý AI. Hãy phân tích câu hỏi từng bước một cách logic.\n"
        "Sau khi suy nghĩ, đưa ra đáp án cuối cùng ở dòng cuối cùng theo định dạng: Đáp án: X\n"
        "(X là một chữ cái duy nhất, ví dụ A, B, C, D)\n\n"
        f"Câu hỏi: {question}\n\n"
        "Các lựa chọn:\n"
        f"{choices_formatted}\n\n"
        "Suy nghĩ từng bước:\n"
    )

def build_mixed_lang_prompt(question: str, choices: List[str]) -> str:
    """Template E: Language Variation (Mixed Vietnamese + English instruction)"""
    choices_formatted = _format_choices(choices)
    return (
        "You are an AI assistant. Answer the following Vietnamese multiple-choice question.\n"
        "Choose the BEST answer. Reply with ONLY a single letter (A, B, C, or D). No explanation.\n\n"
        f"Câu hỏi: {question}\n\n"
        "Các lựa chọn:\n"
        f"{choices_formatted}\n\n"
        "Đáp án:"
    )

PROMPT_MODES = {
    'zero_shot': build_zero_shot_prompt,
    'few_shot': build_few_shot_prompt,
    'cot': build_cot_prompt,
    'mixed_lang': build_mixed_lang_prompt,
}

def build_prompt_by_mode(question: str, choices: List[str], mode: str = 'zero_shot') -> str:
    """Dispatch to the correct prompt builder based on mode string."""
    builder = PROMPT_MODES.get(mode)
    if builder is None:
        raise ValueError(f"Unknown prompt mode: {mode}. Available: {list(PROMPT_MODES.keys())}")
    return builder(question, choices)

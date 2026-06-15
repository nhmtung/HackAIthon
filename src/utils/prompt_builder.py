from typing import List

def build_prompt(question: str, choices: List[str]) -> str:
    """
    Generates a zero-shot Vietnamese MCQ prompt for the given question and choices.
    Conforms to AGENTS.md requirements and maps choices dynamically to labels (A, B, C, D, ...).
    """
    # Build options list
    options_text = []
    for i, choice in enumerate(choices):
        label = chr(65 + i)  # 65 is ASCII for 'A'
        options_text.append(f"{label}. {choice}")
    
    options_formatted = "\n".join(options_text)
    
    prompt = (
        "Bạn là trợ lý AI. Hãy chọn đáp án đúng nhất cho câu hỏi sau. "
        "Chỉ trả lời bằng MỘT chữ cái duy nhất (ví dụ: A, B, C, D) đại diện cho đáp án đúng. "
        "Không giải thích, không viết thêm bất kỳ từ nào khác ngoài chữ cái đáp án.\n\n"
        f"Câu hỏi: {question}\n\n"
        "Các lựa chọn:\n"
        f"{options_formatted}\n\n"
        "Đáp án:"
    )
    return prompt

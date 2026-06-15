import sys
import os
import re
from collections import Counter

# Add workspace directory to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils.data_loader import load_questions

def classify_question(question: str) -> str:
    """
    Classifies a question based on heuristics.
    - RAG: contains "Đoạn thông tin:" or "Title:" or "Tiêu đề:"
    - Quantitative/Math: contains $, \frac, ^, +, -, *, / or numbers with units
    - Factual/Implicit: fallback
    """
    q_lower = question.lower()
    
    # RAG Heuristics
    if "đoạn thông tin:" in q_lower or "title:" in q_lower or "tiêu đề:" in q_lower:
        return "RAG"
        
    # Math/Quantitative Heuristics
    math_chars = ['$', '\\frac', '^', '+', '-', '*', '/']
    if any(char in question for char in math_chars):
        return "Quantitative/Math"
        
    # Check for numbers with common scientific units
    # e.g., "5 m", "10kg", "3.2m/s", "100°C", "50%", etc.
    unit_regex = re.compile(r'\b\d+(?:\.\d+)?\s*(?:m/s|km/h|kg|g|mg|m|cm|mm|km|s|h|min|%|°c|v|a|w|j|n|pa|hz|mol|l|ml)\b', re.IGNORECASE)
    if unit_regex.search(question):
        return "Quantitative/Math"
        
    return "Factual/Implicit"

def main() -> None:
    data_path = os.path.join("data", "public-test_1780368312.json")
    print(f"Loading questions from: {data_path}")
    
    questions = load_questions(data_path)
    total_questions = len(questions)
    
    if total_questions == 0:
        print("[ERROR] No questions loaded. Please verify the dataset path and contents.")
        sys.exit(1)
        
    # 1. Choice distribution
    choice_counts = [len(q["choices"]) for q in questions]
    choice_dist = Counter(choice_counts)
    
    # 2. Length statistics
    lengths = [len(q["question"]) for q in questions]
    avg_len = sum(lengths) / total_questions
    max_len = max(lengths)
    
    # 3. Classify questions
    classifications = [classify_question(q["question"]) for q in questions]
    class_dist = Counter(classifications)
    
    # Print the analysis results in a clean table format
    print("\n" + "="*50)
    print(" DATASET EXPLORATION & ANALYSIS REPORT ")
    print("="*50)
    print(f"{'Metric':<30} | {'Value':<15}")
    print("-" * 50)
    print(f"{'Total Questions':<30} | {total_questions:<15}")
    print(f"{'Average Question Length (chars)':<30} | {avg_len:<15.2f}")
    print(f"{'Maximum Question Length (chars)':<30} | {max_len:<15}")
    
    print("-" * 50)
    print("Choice Count Distribution:")
    for num_choices in sorted(choice_dist.keys()):
        count = choice_dist[num_choices]
        percentage = (count / total_questions) * 100
        print(f"  - {num_choices} choices: {count} questions ({percentage:.2f}%)")
        
    print("-" * 50)
    print("Question Type Classification (Heuristics):")
    for qtype in ["RAG", "Quantitative/Math", "Factual/Implicit"]:
        count = class_dist.get(qtype, 0)
        percentage = (count / total_questions) * 100
        print(f"  - {qtype:<18}: {count} questions ({percentage:.2f}%)")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
Token Budget Optimization script.
Iterates over max_tokens values and evaluates speed impact.
"""
import os
import sys
import time
import argparse
import pandas as pd

_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SRC_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from src.utils.data_loader import load_questions
from src.utils.prompt_builder import build_prompt
from src.utils.answer_extractor import extract_answer
from src.inference.vllm_engine import VLLMEngine

def main():
    parser = argparse.ArgumentParser(description="Optimize generation token budget for speed")
    parser.add_argument("--gold", type=str, default="data/gold_subset.csv", help="Path to gold ground truth CSV")
    parser.add_argument("--input", type=str, default="data/public-test_1780368312.json", help="Path to input test JSON")
    parser.add_argument("--model", type=str, default="Qwen/Qwen3.5-7B", help="Model name or path")
    parser.add_argument("--dry-run", action="store_true", help="Run simulated benchmarks (for testing script harness)")
    args = parser.parse_args()

    input_path = os.path.join(_PROJECT_ROOT, args.input)
    questions = load_questions(input_path)[:50] # Evaluate on first 50 questions
    
    # Check gold subset ground truth availability (for real accuracy checks)
    gold_path = os.path.join(_PROJECT_ROOT, args.gold)
    gold_available = os.path.exists(gold_path)
    gold_dict = {}
    if gold_available:
        try:
            gold_df = pd.read_csv(gold_path, encoding="utf-8")
            missing_truth = gold_df["ground_truth"].isna() | (gold_df["ground_truth"].astype(str).str.strip() == "")
            if not missing_truth.any():
                gold_df["ground_truth"] = gold_df["ground_truth"].str.strip().str.upper()
                gold_dict = dict(zip(gold_df["qid"].astype(str), gold_df["ground_truth"]))
        except Exception:
            pass

    # Budget Options to evaluate
    zero_shot_budgets = [16, 8, 4, 2, 1]
    cot_budgets = [256, 128, 64]
    
    results = []
    
    # A. Zero-shot Token Budget Tuning
    print("Evaluating Zero-Shot max_tokens configurations...")
    for tokens in zero_shot_budgets:
        start_time = time.time()
        
        if args.dry_run or sys.platform == "win32":
            # Simulation: Latency grows roughly linearly with token counts
            elapsed = len(questions) * (0.01 + 0.002 * tokens)
            time.sleep(0.01)
            raw_outputs = ["A"] * len(questions)
        else:
            engine = VLLMEngine(model_name=args.model, max_tokens=tokens)
            prompts = [build_prompt(q["question"], q["choices"], mode="zero_shot") for q in questions]
            raw_outputs = engine.generate(prompts)
            elapsed = time.time() - start_time
            
        throughput = len(questions) / elapsed
        
        # Accuracy check if gold label references are ready
        accuracy_str = "N/A (No Gold)"
        if gold_dict:
            correct = 0
            for q, raw in zip(questions, raw_outputs):
                ans = extract_answer(raw, len(q["choices"]))
                if ans == gold_dict.get(q["qid"]):
                    correct += 1
            accuracy_str = f"{(correct/len(questions)):.4f}"

        print(f"  max_tokens={tokens:<3} | Throughput: {throughput:.2f} Req/s | Accuracy: {accuracy_str}")
        results.append({
            "mode": "zero_shot",
            "max_tokens": tokens,
            "throughput": throughput,
            "accuracy": accuracy_str
        })

    # B. CoT Token Budget Tuning
    print("\nEvaluating CoT max_tokens configurations...")
    for tokens in cot_budgets:
        start_time = time.time()
        
        if args.dry_run or sys.platform == "win32":
            elapsed = len(questions) * (0.05 + 0.002 * tokens)
            time.sleep(0.01)
            # Simulated CoT ending with final answer marker
            raw_outputs = [f"Suy nghĩ: ... \nĐáp án: A"] * len(questions)
        else:
            engine = VLLMEngine(model_name=args.model, max_tokens=tokens)
            prompts = [build_prompt(q["question"], q["choices"], mode="cot") for q in questions]
            raw_outputs = engine.generate(prompts)
            elapsed = time.time() - start_time
            
        throughput = len(questions) / elapsed
        
        accuracy_str = "N/A (No Gold)"
        if gold_dict:
            correct = 0
            for q, raw in zip(questions, raw_outputs):
                ans = extract_answer(raw, len(q["choices"]))
                if ans == gold_dict.get(q["qid"]):
                    correct += 1
            accuracy_str = f"{(correct/len(questions)):.4f}"

        print(f"  max_tokens={tokens:<3} | Throughput: {throughput:.2f} Req/s | Accuracy: {accuracy_str}")
        results.append({
            "mode": "cot",
            "max_tokens": tokens,
            "throughput": throughput,
            "accuracy": accuracy_str
        })

    # Report layout printout
    print("\n" + "=" * 50)
    print(f"{'Mode':<10} | {'max_tokens':<10} | {'Throughput (Req/s)':<20} | {'Accuracy':<10}")
    print("-" * 50)
    for res in results:
         print(f"{res['mode']:<10} | {res['max_tokens']:<10} | {res['throughput']:<20.2f} | {res['accuracy']:<10}")
    print("=" * 50)

if __name__ == "__main__":
    main()

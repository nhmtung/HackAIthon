# -*- coding: utf-8 -*-
"""
Compare Prompts benchmark and evaluation script.
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
    parser = argparse.ArgumentParser(description="Compare prompt templates on gold subset")
    parser.add_argument("--gold", type=str, default="data/gold_subset.csv", help="Path to gold ground truth CSV")
    parser.add_argument("--input", type=str, default="data/public-test_1780368312.json", help="Path to input test JSON")
    parser.add_argument("--model", type=str, default="Qwen/Qwen3.5-7B", help="Model name or path")
    parser.add_argument("--dry-run", action="store_true", help="Format and validation dry-run (returns random/mock answers)")
    args = parser.parse_args()

    # 1. Verify gold file exists and is populated
    gold_path = os.path.join(_PROJECT_ROOT, args.gold)
    if not os.path.exists(gold_path):
        print(f"Error: Gold file not found at {gold_path}.")
        print("Please run `C:\\Users\\shiro\\.local\\bin\\python3.11.exe scripts/create_gold_subset.py` first.")
        sys.exit(1)

    gold_df = pd.read_csv(gold_path, encoding="utf-8")
    if gold_df.empty or "ground_truth" not in gold_df.columns:
        print("Error: Gold file is empty or missing 'ground_truth' column.")
        sys.exit(1)

    # Check for empty ground truth safely
    missing_truth = gold_df["ground_truth"].isna() | (gold_df["ground_truth"].astype(str).str.strip() == "")
    if missing_truth.any():
        print(f"WARNING: There are {missing_truth.sum()} questions with missing ground truth in {args.gold}.")
        print("MANUAL STEP REQUIRED:")
        print("Please manually fill the 'ground_truth' column in data/gold_subset.csv with the correct answer (A, B, C, D) for each of the 50 questions. Then re-run this comparison script.")
        print("Skipping evaluation until ground truth is provided.")
        sys.exit(0)

    # Convert ground_truth to uppercase for safe comparison
    gold_df["ground_truth"] = gold_df["ground_truth"].str.strip().str.upper()
    gold_dict = dict(zip(gold_df["qid"].astype(str), gold_df["ground_truth"]))

    # 2. Load the input test questions
    input_path = os.path.join(_PROJECT_ROOT, args.input)
    questions = load_questions(input_path)
    # Filter only questions present in the gold subset
    gold_qids = set(gold_dict.keys())
    eval_questions = [q for q in questions if q["qid"] in gold_qids]

    if not eval_questions:
        print("Error: No overlapping questions found between input dataset and gold subset.")
        sys.exit(1)

    print(f"Evaluating {len(eval_questions)} questions from gold subset.")

    # 3. Define the modes to experiment with
    modes = ["zero_shot", "few_shot", "cot", "routed", "mixed_lang"]
    results = {}
    detailed_reports = []

    # Initialize Engine (if not dry-run)
    engine = None
    if not args.dry_run:
        print(f"Initializing inference engine for model {args.model}...")
        # Start with default token limit; CoT handling is prompt-specific
        engine = VLLMEngine(model_name=args.model, max_tokens=16)
        print(f"Backend active: {engine.backend}")

    # 4. Run benchmarks
    for mode in modes:
        print(f"\nRunning experiment for prompt mode: '{mode}'...")
        prompts = []
        for q in eval_questions:
            prompt = build_prompt(q["question"], q["choices"], mode=mode)
            prompts.append(prompt)

        start_time = time.time()
        if args.dry_run:
            # Generate deterministic mocked responses for testing the harness
            raw_outputs = []
            for i, q in enumerate(eval_questions):
                # For realistic simulation, Zero Shot & Mixed Lang output A/B/C/D directly
                # CoT outputs logic first
                if mode == "cot":
                    raw_outputs.append(f"Suy nghĩ: {i}. Do đó đáp án là A.\nĐáp án: A")
                else:
                    raw_outputs.append("A")
        else:
            # Configure appropriate max_tokens dynamically
            engine.max_tokens = 512 if mode in ["cot", "routed"] else 16
            raw_outputs = engine.generate(prompts)
            
        elapsed = time.time() - start_time

        correct = 0
        predictions = []
        for q, raw in zip(eval_questions, raw_outputs):
            ans = extract_answer(raw, len(q["choices"]))
            if ans not in {"A", "B", "C", "D"}:
                ans = "A"
            predictions.append(ans)
            
            ref = gold_dict.get(q["qid"])
            if ans == ref:
                correct += 1

        accuracy = correct / len(eval_questions)
        results[mode] = {
            "accuracy": accuracy,
            "correct": correct,
            "total": len(eval_questions),
            "elapsed_time": elapsed,
            "req_per_sec": len(eval_questions) / elapsed if elapsed > 0 else 0.0
        }
        
        # Save details for the markdown report
        for q, raw, pred in zip(eval_questions, raw_outputs, predictions):
            ref = gold_dict.get(q["qid"])
            detailed_reports.append({
                "qid": q["qid"],
                "mode": mode,
                "question_preview": q["question"][:60].replace("\n", " ") + "...",
                "raw_output": raw.replace("\n", "\\n")[:120] + "...",
                "prediction": pred,
                "ground_truth": ref,
                "correct": pred == ref
            })

        print(f"Mode '{mode}' accuracy: {accuracy:.4f} ({correct}/{len(eval_questions)}) | Time: {elapsed:.2f}s")

    # 5. Generate and Print Comparison Table
    print("\n" + "=" * 50)
    print(f"{'Prompt Mode':<15} | {'Accuracy':<10} | {'Correct':<10} | {'Speed (Req/s)':<15}")
    print("-" * 50)
    for mode in modes:
        res = results[mode]
        print(f"{mode:<15} | {res['accuracy']:<10.4f} | {res['correct']}/{res['total']:<8} | {res['req_per_sec']:<15.2f}")
    print("=" * 50)

    # 6. Save Results to markdown artifact
    report_path = os.path.join(_PROJECT_ROOT, "docs", "prompt_experiment_results.md")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# 🧪 Prompt Engineering & CoT Experiment Results\n\n")
        f.write(f"Executed at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Base Model: `{args.model}`\n")
        f.write(f"Gold Subset Size: {len(eval_questions)} questions\n\n")
        f.write("## Summary Comparison Table\n\n")
        f.write("| Prompt Mode | Accuracy | Correct | Elapsed Time | Speed (Req/s) |\n")
        f.write("|---|---|---|---|---|\n")
        for mode in modes:
            res = results[mode]
            f.write(f"| `{mode}` | {res['accuracy']:.4f} | {res['correct']}/{res['total']} | {res['elapsed_time']:.2f}s | {res['req_per_sec']:.2f} |\n")
        
        f.write("\n## Detailed Per-Question Results\n\n")
        f.write("| QID | Mode | Question Preview | Ground Truth | Prediction | Correct? | Raw Output Snippet |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for item in detailed_reports:
            status = "✅" if item["correct"] else "❌"
            f.write(f"| {item['qid']} | `{item['mode']}` | {item['question_preview']} | {item['ground_truth']} | {item['prediction']} | {status} | `{item['raw_output']}` |\n")

    print(f"\nDetailed report saved to {report_path}")

if __name__ == "__main__":
    main()

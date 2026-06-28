# -*- coding: utf-8 -*-
"""
Per-Question Performance Profiler

Runs the pipeline on the test set, profiles per-question statistics,
aggregates latency, prompt/output lengths, and fallback rates.

Usage:
  python scripts/profile_performance.py [--input data/public-test_1780368312.json] [--limit 50] [--dry-run]
"""
import os
import sys
import time
import json
import argparse
import numpy as np
import pandas as pd

# Ensure project root is on path
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from src.utils.data_loader import load_questions
from src.utils.prompt_builder import build_prompt
from src.utils.answer_extractor import extract_answer
from src.inference.vllm_engine import VLLMEngine
from src.inference.model_config import MODEL_REGISTRY

def estimate_tokens(text: str) -> int:
    """Rough estimation of token count (approx 1 token = 4 characters)."""
    return max(1, len(text) // 4)

def check_fallback(raw: str, num_choices: int) -> bool:
    """
    Checks if extract_answer fell back to default 'A' due to no valid letters.
    If the extracted answer is 'A', but 'A' is not present in raw in any valid answer format,
    or if raw is empty/None, it's considered a fallback.
    """
    if not raw or not isinstance(raw, str):
        return True
    
    # Run the extraction
    ans = extract_answer(raw, num_choices=num_choices)
    
    # If the answer is not 'A', it did not fall back to the absolute default
    if ans != "A":
        return False
    
    # If answer is 'A', check if 'A' is actually in the raw output or if we defaulted to 'A'
    # because of no matching letter.
    valid = {chr(65 + i) for i in range(max(2, min(num_choices, 10)))}
    s = raw.strip()
    if len(s) == 1 and s.upper() == "A":
        return False
    
    # Check if 'A' appears in raw
    if "A" in raw.upper():
        return False
        
    # If 'A' is not even in raw, then it definitely fell back
    return True

def main():
    parser = argparse.ArgumentParser(description="Profile per-question inference performance")
    parser.add_argument(
        "--input", type=str,
        default=os.path.join(_PROJECT_ROOT, "data", "public-test_1780368312.json"),
        help="Path to input test JSON file"
    )
    parser.add_argument(
        "--limit", type=int,
        default=-1,
        help="Limit number of questions to process (-1 for all)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Use simulated engine instead of loading actual model"
    )
    parser.add_argument(
        "--prompt_mode", type=str,
        default="zero_shot",
        choices=["zero_shot", "few_shot", "cot", "routed", "mixed_lang"],
        help="Prompt mode to use"
    )
    args = parser.parse_args()

    # Load questions
    if not os.path.exists(args.input):
        print(f"ERROR: Input file not found at '{args.input}'")
        sys.exit(1)
        
    questions = load_questions(args.input)
    if args.limit > 0:
        questions = questions[:args.limit]
        
    print(f"Profiling performance on {len(questions)} questions (Prompt Mode: {args.prompt_mode})...")

    # Select engine or simulate
    engine = None
    is_dry = args.dry_run or (sys.platform == "win32")
    if is_dry:
        print("[INFO] Running in SIMULATED (dry-run) mode.")
    else:
        try:
            print("[INFO] Initializing VLLMEngine...")
            engine = VLLMEngine(
                model_name=MODEL_REGISTRY.get("awq", "Qwen/Qwen2.5-3B-Instruct-AWQ"),
                max_tokens=16 if args.prompt_mode not in ["cot", "routed"] else 512,
                quantization="awq",
                gpu_memory_utilization=0.90,
            )
        except Exception as e:
            print(f"[WARNING] Failed to load vLLM model: {e}. Falling back to simulation.")
            is_dry = True

    profile_records = []
    
    for idx, q in enumerate(questions):
        qid = q.get("qid", f"unknown_{idx}")
        question_text = q.get("question", "")
        choices = q.get("choices", [])
        num_choices = len(choices)
        
        prompt = build_prompt(question_text, choices, mode=args.prompt_mode)
        prompt_char_len = len(prompt)
        prompt_token_est = estimate_tokens(prompt)
        
        if is_dry:
            # Simulate inference
            # Latency scales slightly with prompt length and output mode
            base_latency_ms = np.random.normal(50, 10)  # average 50ms base
            length_factor = (prompt_token_est / 1000) * 20  # +20ms per 1k tokens
            cot_factor = 300 if args.prompt_mode in ["cot", "routed"] else 0
            latency_ms = max(10.0, base_latency_ms + length_factor + cot_factor + np.random.normal(0, 5))
            
            # Simulate output
            if args.prompt_mode in ["cot", "routed"]:
                raw_output = f"Phân tích câu hỏi: ... Do đó, đáp án đúng là {choices[0] if choices else 'A'}.\nĐáp án: A"
                output_tokens = np.random.randint(40, 120)
            else:
                raw_output = "A"
                output_tokens = 1
                
            fell_back = check_fallback(raw_output, num_choices)
            # Sleep briefly to simulate execution if needed (max 5ms for script feel)
            time.sleep(0.001)
        else:
            # Real execution
            start_t = time.time()
            try:
                raw_outputs = engine.generate([prompt])
                raw_output = raw_outputs[0]
            except Exception as e:
                raw_output = ""
                print(f"[ERROR] Inference failed for qid={qid}: {e}")
            latency_ms = (time.time() - start_t) * 1000.0
            output_tokens = estimate_tokens(raw_output)
            fell_back = check_fallback(raw_output, num_choices)
            
        profile_records.append({
            "qid": qid,
            "prompt_length_chars": prompt_char_len,
            "prompt_tokens_est": prompt_token_est,
            "output_length_chars": len(raw_output),
            "output_tokens_est": output_tokens,
            "latency_ms": latency_ms,
            "fallback_occurred": bool(fell_back),
            "raw_output_snippet": raw_output[:50]
        })

    # Convert to DataFrame for easier statistical calculations
    df = pd.DataFrame(profile_records)

    # Aggregate statistics
    mean_latency = df["latency_ms"].mean()
    median_latency = df["latency_ms"].median()
    p95_latency = df["latency_ms"].quantile(0.95)
    
    corr_len_latency = df["prompt_length_chars"].corr(df["latency_ms"])
    fallback_rate = df["fallback_occurred"].mean() * 100.0
    fallback_count = int(df["fallback_occurred"].sum())

    summary_stats = {
        "total_questions": len(df),
        "latency_stats_ms": {
            "mean": float(mean_latency),
            "median": float(median_latency),
            "p95": float(p95_latency)
        },
        "correlation_prompt_length_vs_latency": float(corr_len_latency) if not pd.isna(corr_len_latency) else 0.0,
        "fallback_stats": {
            "count": fallback_count,
            "rate_percent": float(fallback_rate)
        }
    }

    # Save detailed JSON output
    profile_output_path = os.path.join(_PROJECT_ROOT, "docs", "performance_profile.json")
    os.makedirs(os.path.dirname(profile_output_path), exist_ok=True)
    
    output_data = {
        "summary": summary_stats,
        "details": profile_records
    }
    with open(profile_output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print("  PER-QUESTION PERFORMANCE PROFILE SUMMARY")
    print("=" * 60)
    print(f"  Total Questions Processed : {len(df)}")
    print(f"  Mean Latency              : {mean_latency:.2f} ms")
    print(f"  Median Latency            : {median_latency:.2f} ms")
    print(f"  95th Percentile Latency   : {p95_latency:.2f} ms")
    print(f"  Length-Latency Correlation: {corr_len_latency:.4f}")
    print(f"  Fallback Rate             : {fallback_rate:.2f}% ({fallback_count}/{len(df)} questions)")
    print(f"  Profile saved to          : docs/performance_profile.json")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()

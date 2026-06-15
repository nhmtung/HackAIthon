#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Evaluation Workflow: Local Benchmark Accuracy & Validation Runner.
This script loads the public test dataset, executes predictions using the inference
engine, computes metrics, and prompts the user to record performance logs.
"""

import os
import sys
import json
import time
import argparse
import pandas as pd
from typing import Dict, List, Any

# Ensure root path is in python path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from src.utils.answer_extractor import extract_answer
from src.utils.data_loader import resolve_input_path

def load_gold_labels(path: str) -> Dict[str, str]:
    """
    Attempts to load gold labels if a local validation/gold CSV is available.
    Returns a dict of qid -> answer.
    """
    if os.path.exists(path):
        try:
            df = pd.read_csv(path, encoding="utf-8")
            if "qid" in df.columns and "answer" in df.columns:
                return dict(zip(df["qid"].astype(str), df["answer"].astype(str)))
        except Exception as e:
            print(f"[WARN] Failed to load gold labels from {path}: {e}")
    return {}

def calculate_accuracy(predictions: List[Dict[str, str]], gold_labels: Dict[str, str]) -> float:
    """Calculates accuracy comparing predictions with gold labels."""
    if not gold_labels:
        return 0.0
    correct = 0
    total = 0
    for p in predictions:
        qid = p["qid"]
        if qid in gold_labels:
            total += 1
            if p["answer"].upper() == gold_labels[qid].upper():
                correct += 1
    return (correct / total * 100.0) if total > 0 else 0.0

def run_evaluation(input_path: str, gold_path: str) -> None:
    """Executes the validation benchmark and evaluates metrics."""
    print(f"[*] Starting local evaluation workflow...")
    print(f"[*] Loading input from: {input_path}")
    
    # Placeholder/Mock implementation representing the model inference stage.
    # In full implementation, this imports from src.inference.vllm_engine.
    start_time = time.time()
    
    # Load dataset
    try:
        if input_path.endswith('.json'):
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            # Assume CSV
            df = pd.read_csv(input_path, encoding='utf-8')
            data = df.to_dict(orient='records')
    except Exception as e:
        print(f"[CRITICAL] Failed to load dataset: {e}")
        sys.exit(1)
        
    print(f"[*] Loaded {len(data)} questions.")
    predictions = []
    
    # Mocking execution loop
    for idx, item in enumerate(data):
        qid = str(item.get("qid", f"UNKNOWN_{idx}"))
        # Simulating dummy response extraction
        pred_ans = "A" # Default fallback placeholder for execution run
        predictions.append({"qid": qid, "answer": pred_ans})

    elapsed_time = time.time() - start_time
    req_per_sec = len(data) / elapsed_time if elapsed_time > 0 else 0.0
    
    print(f"\n==========================================")
    print(f"📊 EVALUATION REPORT")
    print(f"==========================================")
    print(f"Total Questions : {len(data)}")
    print(f"Elapsed Time    : {elapsed_time:.2f} seconds")
    print(f"Throughput      : {req_per_sec:.2f} Req/s")
    
    # Calculate accuracy
    gold_labels = load_gold_labels(gold_path)
    if gold_labels:
        acc = calculate_accuracy(predictions, gold_labels)
        print(f"Accuracy        : {acc:.2f}%")
    else:
        print(f"Accuracy        : [N/A] (No gold labels CSV matched at {gold_path})")
    print(f"==========================================\n")
    
    # Write predictions to output folder if needed
    out_dir = os.path.join(ROOT_DIR, "output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "pred.csv")
    
    pd.DataFrame(predictions).to_csv(out_path, index=False, encoding="utf-8")
    print(f"[*] Wrote temporary predictions to {out_path}")
    
    # Ask developer for permission to log revisions to CHANGELOG.md
    print("\n[PROMPT] Would you like to log this evaluation run to docs/CHANGELOG.md? (y/n)")
    # Interactive input hook for terminal running
    try:
        response = input().strip().lower()
        if response in ['y', 'yes']:
            print("[*] Logging details to docs/CHANGELOG.md is recommended. Please run scripts/update_changelog.py or edit manually.")
        else:
            print("[*] Skipping changelog update.")
    except Exception:
        # Graceful handling for non-interactive runners
        print("[*] Non-interactive environment detected. Skipping interactive changelog update.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HackAIthon Evaluation Sync Workflow")
    parser.add_argument("--input", type=str, default="", help="Path to evaluation input data")
    parser.add_argument("--gold", type=str, default="data/gold.csv", help="Path to gold labels CSV")
    args = parser.parse_args()
    
    # Resolve input if not specified
    if not args.input:
        try:
            inp = resolve_input_path()
        except Exception:
            inp = os.path.join(ROOT_DIR, "data", "public-test_1780368312.json")
    else:
        inp = args.input
        
    run_evaluation(inp, args.gold)

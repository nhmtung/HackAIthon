# -*- coding: utf-8 -*-
"""
Accuracy Evaluator (with Gold Labels)

Usage:
  python scripts/eval_accuracy.py [--pred output/pred.csv] [--gold data/gold_subset.csv]
"""
import os
import sys
import argparse
import json
import pandas as pd
from typing import Dict, Any

# Ensure project root is on path
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from src.utils.prompt_router import detect_question_type

def find_questions_file() -> str | None:
    """Find the public test dataset JSON file."""
    search_dirs = [os.path.join(_PROJECT_ROOT, "data"), _PROJECT_ROOT]
    for d in search_dirs:
        if not os.path.exists(d):
            continue
        for f in os.listdir(d):
            if f.endswith(".json") and "public-test" in f:
                return os.path.join(d, f)
    return None

def main():
    parser = argparse.ArgumentParser(description="Evaluate prediction accuracy against gold labels")
    parser.add_argument(
        "--pred", type=str,
        default=os.path.join(_PROJECT_ROOT, "submission.csv"),
        help="Path to prediction CSV"
    )
    parser.add_argument(
        "--gold", type=str,
        default=None,
        help="Path to gold label CSV"
    )
    args = parser.parse_args()

    # Determine gold path candidates
    gold_candidates = []
    if args.gold:
        gold_candidates.append(args.gold)
    else:
        gold_candidates.extend([
            os.path.join(_PROJECT_ROOT, "data", "gold_full.csv"),
            os.path.join(_PROJECT_ROOT, "data", "gold_subset.csv")
        ])

    gold_path = None
    for path in gold_candidates:
        if os.path.exists(path):
            # Check if it has any actual answers
            try:
                temp_df = pd.read_csv(path, encoding="utf-8")
                # Ensure it has columns we need and at least one non-empty row in ground_truth or answer
                col = "ground_truth" if "ground_truth" in temp_df.columns else ("answer" if "answer" in temp_df.columns else None)
                if col and temp_df[col].dropna().astype(str).str.strip().ne("").any():
                    gold_path = path
                    break
            except Exception:
                pass

    if not gold_path:
        print("ERROR: No gold label file found at data/gold_full.csv or data/gold_subset.csv.")
        print("Please create one with columns 'qid' and 'ground_truth' before running accuracy evaluation.")
        print("Skipping accuracy metrics.")
        sys.exit(0)

    print(f"\nEvaluating predictions '{args.pred}' against gold labels '{gold_path}'...")

    # Load predictions
    if not os.path.exists(args.pred):
        print(f"ERROR: Prediction file not found at '{args.pred}'")
        sys.exit(1)
    
    pred_df = pd.read_csv(args.pred, encoding="utf-8")
    gold_df = pd.read_csv(gold_path, encoding="utf-8")

    # Standardize gold label column
    gold_col = "ground_truth" if "ground_truth" in gold_df.columns else "answer"
    if gold_col not in gold_df.columns:
        print(f"ERROR: Gold label file must contain 'ground_truth' or 'answer' column. Columns: {list(gold_df.columns)}")
        sys.exit(1)
    
    gold_df = gold_df.rename(columns={gold_col: "ground_truth"})
    gold_df["ground_truth"] = gold_df["ground_truth"].astype(str).str.strip().str.upper()
    pred_df["answer"] = pred_df["answer"].astype(str).str.strip().str.upper()

    # Filter out empty gold labels
    gold_df = gold_df[gold_df["ground_truth"].ne("") & gold_df["ground_truth"].notna()]
    if len(gold_df) == 0:
        print("ERROR: Gold label file contains no valid (non-empty) ground truth entries.")
        sys.exit(0)

    # Load questions to classify question types
    questions_file = find_questions_file()
    qid_to_qtext = {}
    if questions_file:
        try:
            with open(questions_file, "r", encoding="utf-8") as f:
                questions_data = json.load(f)
                for item in questions_data:
                    qid_to_qtext[str(item["qid"]).strip()] = str(item.get("question", "")).strip()
        except Exception as e:
            print(f"[WARNING] Failed to load original questions from {questions_file}: {e}")

    # Merge pred and gold
    merged = pd.merge(pred_df, gold_df, on="qid", how="inner")
    if len(merged) == 0:
        print("ERROR: No matching qids found between predictions and gold labels.")
        sys.exit(1)

    # Add question type and question snippet
    merged["question_text"] = merged["qid"].map(lambda x: qid_to_qtext.get(x, ""))
    merged["question_type"] = merged["question_text"].map(detect_question_type)
    merged["correct"] = merged["answer"] == merged["ground_truth"]

    # Compute overall metrics
    total_matched = len(merged)
    total_correct = merged["correct"].sum()
    overall_accuracy = (total_correct / total_matched) * 100.0

    print("\n" + "=" * 60)
    print("  ACCURACY EVALUATION REPORT")
    print("=" * 60)
    print(f"  Matched Questions : {total_matched}")
    print(f"  Correct Predictions: {total_correct}")
    print(f"  Overall Accuracy  : {overall_accuracy:.2f}%")
    print("=" * 60)

    # Per-question-type accuracy
    print("\n  Accuracy by Question Type:")
    print(f"  {'Type':<12} | {'Matched':<8} | {'Correct':<8} | {'Accuracy':<10}")
    print(f"  {'-'*12}-+-{'-'*8}-+-{'-'*8}-+-{'-'*10}")
    
    type_groups = merged.groupby("question_type")
    for qtype, group in type_groups:
        grp_matched = len(group)
        grp_correct = group["correct"].sum()
        grp_acc = (grp_correct / grp_matched) * 100.0
        print(f"  {qtype:<12} | {grp_matched:<8} | {grp_correct:<8} | {grp_acc:.2f}%")
    print(f"  {'-'*12}-+-{'-'*8}-+-{'-'*8}-+-{'-'*10}")

    # Confusion matrix
    print("\n  Confusion Matrices (Actual row vs Predicted col):")
    for qtype in ['rag', 'math', 'factual']:
        qtype_group = merged[merged["question_type"] == qtype]
        if len(qtype_group) == 0:
            continue
        print(f"\n  --- Type: {qtype.upper()} ---")
        try:
            cf = pd.crosstab(qtype_group["ground_truth"], qtype_group["answer"], rownames=["Actual"], colnames=["Pred"])
            print(cf.to_string())
        except Exception as e:
            print(f"  Could not compute confusion matrix: {e}")

    # Detailed error log
    errors_df = merged[~merged["correct"]]
    error_analysis_path = os.path.join(_PROJECT_ROOT, "docs", "error_analysis.md")
    
    with open(error_analysis_path, "w", encoding="utf-8") as f:
        f.write("# Error Analysis Report\n\n")
        f.write(f"- **Total Checked**: {total_matched}\n")
        f.write(f"- **Total Errors**: {len(errors_df)}\n")
        f.write(f"- **Overall Accuracy**: {overall_accuracy:.2f}%\n\n")
        
        f.write("## Detailed Error Log\n\n")
        if len(errors_df) == 0:
            f.write("🎉 No errors detected! Perfect accuracy.\n")
        else:
            f.write("| QID | Type | Ground Truth | Predicted | Question Snippet |\n")
            f.write("| --- | --- | --- | --- | --- |\n")
            for _, row in errors_df.iterrows():
                snippet = row["question_text"][:80].replace("\n", " ").replace("|", "\\|") + "..."
                f.write(f"| {row['qid']} | {row['question_type']} | {row['ground_truth']} | {row['answer']} | {snippet} |\n")

    print(f"\n  Detailed error log saved to: docs/error_analysis.md")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()

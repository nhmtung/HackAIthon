# -*- coding: utf-8 -*-
"""
Local Accuracy Evaluation Script

Compares output/pred.csv against a gold label file (if available).
If no gold file exists, reports output format statistics only.

Usage:
  python scripts/eval_accuracy.py
  python scripts/eval_accuracy.py --pred output/pred.csv --gold data/gold_sample.csv
"""
import os
import sys
import argparse
import pandas as pd

# Ensure project root is on path
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)


def load_csv(path: str, label: str) -> pd.DataFrame | None:
    """Load a CSV file safely. Returns DataFrame or None."""
    if not os.path.exists(path):
        print(f"[WARNING] {label} file not found: {path}")
        return None
    try:
        df = pd.read_csv(path, encoding="utf-8")
        print(f"[OK] Loaded {label}: {len(df)} rows from {path}")
        return df
    except Exception as e:
        print(f"[ERROR] Failed to load {label}: {e}")
        return None


def evaluate(pred_df: pd.DataFrame, gold_df: pd.DataFrame) -> None:
    """Compute accuracy and print per-question error report."""
    # Merge on qid
    merged = pd.merge(pred_df, gold_df, on="qid", how="inner", suffixes=("_pred", "_gold"))

    if len(merged) == 0:
        print("[WARNING] No matching qids found between pred and gold.")
        return

    total = len(merged)
    correct = (merged["answer_pred"] == merged["answer_gold"]).sum()
    accuracy = correct / total * 100.0

    print("\n" + "=" * 60)
    print("  ACCURACY REPORT")
    print("=" * 60)
    print(f"  Matched questions : {total}")
    print(f"  Correct           : {correct}")
    print(f"  Accuracy          : {accuracy:.2f}%")
    print("=" * 60)

    # Print errors
    errors = merged[merged["answer_pred"] != merged["answer_gold"]]
    if len(errors) > 0:
        print(f"\n  Errors ({len(errors)} total):")
        print(f"  {'qid':<15} {'Predicted':<10} {'Gold':<10}")
        print(f"  {'-'*35}")
        for _, row in errors.head(50).iterrows():
            print(f"  {row['qid']:<15} {row['answer_pred']:<10} {row['answer_gold']:<10}")
        if len(errors) > 50:
            print(f"  ... and {len(errors) - 50} more errors")
    else:
        print("\n  🎉 Perfect score — no errors!")


def report_stats(pred_df: pd.DataFrame) -> None:
    """Print prediction statistics when no gold file is available."""
    print("\n" + "=" * 60)
    print("  PREDICTION STATISTICS (no gold file)")
    print("=" * 60)
    print(f"  Total predictions : {len(pred_df)}")
    print(f"  Columns           : {list(pred_df.columns)}")

    if "answer" in pred_df.columns:
        dist = pred_df["answer"].value_counts().sort_index()
        print(f"\n  Answer Distribution:")
        for letter, count in dist.items():
            pct = count / len(pred_df) * 100.0
            bar = "█" * int(pct / 2)
            print(f"    {letter}: {count:>4} ({pct:5.1f}%) {bar}")

        valid = pred_df["answer"].str.fullmatch(r"[A-D]").all()
        print(f"\n  All answers in {{A,B,C,D}}: {'✅ Yes' if valid else '❌ No'}")
    print("=" * 60)


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate predictions against gold labels")
    parser.add_argument(
        "--pred", type=str,
        default=os.path.join(_PROJECT_ROOT, "output", "pred.csv"),
        help="Path to prediction CSV"
    )
    parser.add_argument(
        "--gold", type=str,
        default=os.path.join(_PROJECT_ROOT, "data", "gold_sample.csv"),
        help="Path to gold label CSV"
    )
    args = parser.parse_args()

    # Load predictions
    pred_df = load_csv(args.pred, "Predictions")
    if pred_df is None:
        print("[FATAL] Cannot proceed without prediction file.")
        sys.exit(1)

    # Load gold (optional)
    gold_df = load_csv(args.gold, "Gold labels")

    if gold_df is not None:
        evaluate(pred_df, gold_df)
    else:
        print("[INFO] No gold label file found. Showing prediction statistics only.")
        report_stats(pred_df)


if __name__ == "__main__":
    main()

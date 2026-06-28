# -*- coding: utf-8 -*-
"""
Pipeline Runner & Validator

Executes the end-to-end pipeline in --dry-run mode (no GPU needed),
then validates the output pred.csv for schema compliance.

Usage:
  python scripts/run_pipeline.py
  python scripts/run_pipeline.py --full  # requires model download & GPU
"""
import os
import sys
import subprocess
import argparse
import json

# Force stdout/stderr to UTF-8 to prevent encoding errors on Windows when printing emojis
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

import pandas as pd

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)

INPUT_PATH = os.path.join(_PROJECT_ROOT, "data", "public-test_1780368312.json")
OUTPUT_PATH = os.path.join(_PROJECT_ROOT, "output", "pred.csv")
MAIN_SCRIPT = os.path.join(_PROJECT_ROOT, "src", "main.py")


def run_pipeline(dry_run: bool = True) -> int:
    """Execute the main pipeline script. Returns exit code."""
    cmd = [
        sys.executable, MAIN_SCRIPT,
        "--input", INPUT_PATH,
        "--output", OUTPUT_PATH,
    ]
    if dry_run:
        cmd.append("--dry-run")

    print(f"\n{'='*60}")
    print("  RUNNING PIPELINE")
    print(f"{'='*60}")
    print(f"  Command: {' '.join(cmd)}")
    print(f"  Dry run: {dry_run}")
    print(f"{'='*60}\n")

    result = subprocess.run(cmd, cwd=_PROJECT_ROOT)
    return result.returncode


def validate_output() -> bool:
    """Validate that pred.csv exists and conforms to spec."""
    print(f"\n{'='*60}")
    print("  VALIDATING OUTPUT")
    print(f"{'='*60}")

    errors: list[str] = []

    # ── File existence ────────────────────────────────────────────────────
    if not os.path.exists(OUTPUT_PATH):
        print(f"  ❌ FAIL: Output file not found: {OUTPUT_PATH}")
        return False
    print(f"  ✅ Output file exists: {OUTPUT_PATH}")

    # ── Load and validate ─────────────────────────────────────────────────
    try:
        pred_df = pd.read_csv(OUTPUT_PATH, encoding="utf-8")
    except Exception as e:
        print(f"  ❌ FAIL: Cannot read CSV: {e}")
        return False

    # Column check
    if list(pred_df.columns) != ["qid", "answer"]:
        errors.append(f"Column mismatch: expected ['qid', 'answer'], got {list(pred_df.columns)}")
    else:
        print(f"  ✅ Columns: {list(pred_df.columns)}")

    # Column count
    if pred_df.shape[1] != 2:
        errors.append(f"Expected 2 columns, got {pred_df.shape[1]}")
    else:
        print(f"  ✅ Column count: 2")

    # Row count vs input
    try:
        with open(INPUT_PATH, "r", encoding="utf-8") as f:
            input_data = json.load(f)
        input_count = len(input_data)
        if len(pred_df) != input_count:
            errors.append(f"Row count mismatch: pred has {len(pred_df)}, input has {input_count}")
        else:
            print(f"  ✅ Row count matches input: {len(pred_df)}")

        # QID match
        input_qids = set(str(item["qid"]).strip() for item in input_data)
        pred_qids = set(pred_df["qid"].astype(str).str.strip())
        missing = input_qids - pred_qids
        extra = pred_qids - input_qids
        if missing:
            errors.append(f"Missing qids in pred: {missing}")
        if extra:
            errors.append(f"Extra qids in pred not in input: {extra}")
        if not missing and not extra:
            print(f"  ✅ All qids match input")
    except Exception as e:
        errors.append(f"Cannot validate against input: {e}")

    # Answer domain check
    valid_answers = pred_df["answer"].str.fullmatch(r"[A-D]")
    if not valid_answers.all():
        bad = pred_df[~valid_answers]
        errors.append(f"Invalid answers found: {bad[['qid','answer']].to_dict('records')[:10]}")
    else:
        print(f"  ✅ All answers in {{A, B, C, D}}")

    # Duplicate qid check
    if pred_df["qid"].duplicated().any():
        dups = pred_df[pred_df["qid"].duplicated(keep=False)]["qid"].unique().tolist()
        errors.append(f"Duplicate qids: {dups[:10]}")
    else:
        print(f"  ✅ No duplicate qids")

    # Null check
    if pred_df["answer"].isna().any():
        errors.append("Null answers found")
    else:
        print(f"  ✅ No null answers")

    # ── Answer distribution ───────────────────────────────────────────────
    dist = pred_df["answer"].value_counts().sort_index()
    print(f"\n  Answer Distribution:")
    for letter, count in dist.items():
        pct = count / len(pred_df) * 100.0
        print(f"    {letter}: {count:>4} ({pct:5.1f}%)")

    # ── Result ────────────────────────────────────────────────────────────
    if errors:
        print(f"\n  ❌ VALIDATION FAILED — {len(errors)} error(s):")
        for err in errors:
            print(f"    • {err}")
        print(f"{'='*60}")
        return False
    else:
        print(f"\n  ✅ ALL VALIDATION CHECKS PASSED")
        print(f"{'='*60}")
        return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Run pipeline and validate output")
    parser.add_argument("--full", action="store_true", help="Run with actual model inference (requires GPU)")
    args = parser.parse_args()

    dry_run = not args.full

    # Step 1: Run pipeline
    exit_code = run_pipeline(dry_run=dry_run)
    if exit_code != 0:
        print(f"\n❌ Pipeline exited with code {exit_code}")
        sys.exit(exit_code)

    # Step 2: Validate output
    valid = validate_output()

    # Step 3: Run eval_accuracy
    print(f"\n{'='*60}")
    print("  RUNNING ACCURACY EVALUATION")
    print(f"{'='*60}")
    eval_script = os.path.join(_SCRIPT_DIR, "eval_accuracy.py")
    subprocess.run([sys.executable, eval_script, "--pred", OUTPUT_PATH], cwd=_PROJECT_ROOT)

    # Final status
    if valid:
        print("\n🎉 Pipeline and validation completed successfully!")
    else:
        print("\n❌ Validation failed. Review errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()

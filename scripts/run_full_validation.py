# -*- coding: utf-8 -*-
"""
Full Validation Suite Runner

Sequentially executes:
  1. Format validation (validate_submission.py)
  2. Accuracy evaluation (eval_accuracy.py) – only if gold labels are available
  3. Performance profiling (profile_performance.py)

Exits with code 0 if all steps succeed, otherwise 1.

Usage:
  python scripts/run_full_validation.py [--skip-gold] [--subset N] [--dry-run]
"""
import os
import sys
import subprocess
import argparse

# Force stdout/stderr to UTF-8 to prevent encoding errors on Windows when printing emojis
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)

def run_script(script_name: str, args: list[str]) -> int:
    """Run a python script as a subprocess and return the exit code."""
    script_path = os.path.join(_SCRIPT_DIR, script_name)
    cmd = [sys.executable, script_path] + args
    print(f"\n[RUN] Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=_PROJECT_ROOT)
    return result.returncode

def main():
    parser = argparse.ArgumentParser(description="Full Validation Suite Runner")
    parser.add_argument(
        "--skip-gold", action="store_true",
        help="Skip accuracy evaluation even if gold labels exist"
    )
    parser.add_argument(
        "--subset", type=int, default=-1,
        help="Limit number of questions to process in profiling (default -1 for all)"
    )
    parser.add_argument(
        "--dry-run", action="store_true", default=True,
        help="Use dry-run simulation mode for performance profiling"
    )
    parser.add_argument(
        "--pred", type=str, default="output/pred.csv",
        help="Path to prediction CSV file"
    )
    args = parser.parse_args()

    print("============================================================")
    print("  STARTING FULL VALIDATION SUITE RUNNER")
    print("============================================================")

    # 1. Format validation
    format_code = run_script("validate_submission.py", ["--pred", args.pred])
    if format_code != 0:
        print("[FAIL] Format validation failed.")
        sys.exit(1)
    print("[PASS] Format validation passed.")

    # 2. Accuracy evaluation
    if not args.skip_gold:
        # Check if gold file exists and is populated
        gold_subset_path = os.path.join(_PROJECT_ROOT, "data", "gold_subset.csv")
        gold_full_path = os.path.join(_PROJECT_ROOT, "data", "gold_full.csv")
        gold_exists = os.path.exists(gold_subset_path) or os.path.exists(gold_full_path)
        
        if gold_exists:
            # We run eval_accuracy.py
            eval_args = ["--pred", args.pred]
            accuracy_code = run_script("eval_accuracy.py", eval_args)
            if accuracy_code != 0:
                print("[FAIL] Accuracy evaluation failed.")
                sys.exit(1)
        else:
            print("\n[INFO] Skipping accuracy evaluation (no gold label file found).")
    else:
        print("\n[INFO] Skipping accuracy evaluation as requested by --skip-gold.")

    # 3. Performance profiling
    profile_args = []
    if args.subset > 0:
        profile_args.extend(["--limit", str(args.subset)])
    if args.dry_run:
        profile_args.append("--dry-run")
    
    profile_code = run_script("profile_performance.py", profile_args)
    if profile_code != 0:
        print("[FAIL] Performance profiling failed.")
        sys.exit(1)
    print("[PASS] Performance profiling passed.")

    print("\n============================================================")
    print("  [SUCCESS] ALL VALIDATION SUITE CHECKS COMPLETED SUCCESSFULLY!")
    print("============================================================")
    sys.exit(0)

if __name__ == "__main__":
    main()

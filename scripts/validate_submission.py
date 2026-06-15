# -*- coding: utf-8 -*-
"""
Submission Format Validator

Checks pred.csv format compliance (columns, dtypes, value domain, uniqueness, encoding).
Usage:
  python scripts/validate_submission.py [--pred output/pred.csv]
"""
import os
import sys
import argparse
import pandas as pd

def validate_pred_file(file_path: str) -> bool:
    """
    Validates a prediction CSV file for submission format compliance.
    """
    print(f"\n============================================================")
    print(f"  VALIDATING SUBMISSION FORMAT: {file_path}")
    print(f"============================================================")

    errors = []

    # 1. File exists and is readable
    if not os.path.exists(file_path):
        print(f"[FAIL] File does not exist at '{file_path}'")
        return False
    
    # 2. Check encoding is UTF-8
    try:
        with open(file_path, "rb") as f:
            content = f.read()
        content.decode("utf-8")
        print("[OK] Encoding: UTF-8 (valid)")
    except UnicodeDecodeError as e:
        errors.append(f"File encoding is not valid UTF-8: {e}")
        print("[FAIL] Encoding: Invalid UTF-8")

    # 3. Read CSV
    try:
        df = pd.read_csv(file_path, encoding="utf-8")
    except Exception as e:
        print(f"[FAIL] Could not read CSV file: {e}")
        return False

    # 4. Check columns exactly 'qid' and 'answer'
    actual_cols = list(df.columns)
    expected_cols = ["qid", "answer"]
    if actual_cols != expected_cols:
        errors.append(f"Column mismatch. Expected exactly {expected_cols}, got {actual_cols} (case-sensitive, order matters)")
        print("[FAIL] Columns: Invalid")
    else:
        print("[OK] Columns: Correct ('qid', 'answer')")

    # 5. Check no missing values or duplicate qids
    if "qid" in df.columns:
        if df["qid"].isna().any():
            errors.append("Missing/null values found in 'qid' column")
            print("[FAIL] QIDs: Contains null values")
        else:
            # Check duplicate qids
            dups = df["qid"][df["qid"].duplicated()]
            if not dups.empty:
                errors.append(f"Duplicate QID values found: {dups.unique().tolist()[:10]}")
                print("[FAIL] QIDs: Contains duplicate values")
            else:
                print("[OK] QIDs: Unique and non-null")
    else:
        errors.append("Missing 'qid' column")

    # 6. Check all answer values belong to {'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'}
    if "answer" in df.columns:
        if df["answer"].isna().any():
            errors.append("Null values found in 'answer' column")
            print("[FAIL] Answers: Contains null values")
        else:
            allowed_answers = {'A','B','C','D','E','F','G','H','I','J'}
            invalid_mask = ~df["answer"].isin(allowed_answers)
            if invalid_mask.any():
                invalid_vals = df.loc[invalid_mask, ["qid", "answer"]].head(10).to_dict("records")
                errors.append(f"Invalid answer value(s) found (not in A-J): {invalid_vals}")
                print("[FAIL] Answers: Contains invalid values")
            else:
                print("[OK] Answers: All within allowed domain {A-J}")
    else:
        errors.append("Missing 'answer' column")

    # Print summary report
    print(f"------------------------------------------------------------")
    if errors:
        print(f"[FAIL] FAILED VALIDATION - {len(errors)} violation(s) found:")
        for i, err in enumerate(errors, 1):
            print(f"  {i}. {err}")
        print(f"============================================================\n")
        return False
    else:
        print("[SUCCESS] PASSED VALIDATION - All format checks passed successfully!")
        print(f"============================================================\n")
        return True

def main():
    parser = argparse.ArgumentParser(description="Validate submission format of pred.csv")
    parser.add_argument(
        "--pred", type=str,
        default="output/pred.csv",
        help="Path to prediction CSV"
    )
    args = parser.parse_args()
    
    success = validate_pred_file(args.pred)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

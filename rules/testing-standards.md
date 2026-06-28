# Testing and Submission Validation Standards

Guidelines to verify codebase correctness, submission format compliance, and performance profiling.

## 1. Dry-Run Testing
* **Requirement**: The pipeline MUST support a `--dry-run` flag in `src/main.py`.
* **Behavior**: Dry-run bypasses actual LLM inference, sets predictions to default value `'A'`, and writes outputs to `/output/pred.csv` within milliseconds. This allows validating the end-to-end routing, loading, and writing code on CPU-only machines.

## 2. Submission format checks (`validate_submission.py`)
Prior to committing/packaging changes, the prediction CSV MUST pass these validation gates:
- **Columns**: Exactly 2 columns: `qid` and `answer` (this exact ordering and casing).
- **Unique QIDs**: No duplicate rows or null entries.
- **Answer Domain**: Every answer must be single character, uppercase `A`, `B`, `C`, or `D`.
- **RowCount**: Must equal the input row count.
- **Encoding**: UTF-8 without BOM.

## 3. Automated Validation Execution
Before finishing a feature or refactoring:
1. Generate predictions:
   ```bash
   python scripts/run_pipeline.py
   ```
2. Verify formatting:
   ```bash
   python scripts/run_full_validation.py --skip-gold --dry-run
   ```
3. Never bypass failed checks. Fix all formatting and schema warnings immediately.

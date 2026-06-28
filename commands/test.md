# Test Command
# Trigger: /test
# Description: Runs end-to-end dry-run pipeline test on mock data.

To test the pipeline flow, execute:
```bash
python scripts/run_pipeline.py
```
This script:
1. Resolves input files.
2. Formats questions.
3. Invokes CPU/dry-run inference.
4. Outputs the final prediction CSV.
5. Performs basic schema checks.

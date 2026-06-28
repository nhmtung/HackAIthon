# Validate Command
# Trigger: /validate
# Description: Executes the full validation suite (format checks, CPU fallback test, performance profile)

To validate the current state of the repository, execute:
```bash
python scripts/run_full_validation.py --skip-gold --dry-run
```
This runs:
1. `validate_submission.py` to check the prediction format.
2. `profile_performance.py` in simulated mode.

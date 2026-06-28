#!/bin/bash
# validate-code.sh
# Runs validation checks before commit/packaging.
echo "Running code and submission formatting validation..."
python scripts/run_full_validation.py --skip-gold --dry-run
if [ $? -ne 0 ]; then
    echo "Validation failed!"
    exit 1
fi
echo "Validation passed successfully."
exit 0

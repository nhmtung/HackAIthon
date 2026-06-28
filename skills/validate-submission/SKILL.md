---
name: validate-submission
description: Validate prediction file formats and run execution test suites for the HackAIthon competition. Use this skill whenever a model optimization, CLI parameter modification, routing change, or script update is performed. It ensures that output formats remain compliant and no exceptions are raised.
---

# Submission Format Validator Skill

This skill outlines the step-by-step procedure to execute verification checks on the competition submission format.

## Guidelines

1. **Verify Local Environment Status**
   Check that dependencies are correctly imported:
   ```bash
   python scripts/verify_env.py
   ```

2. **Generate Prediction CSV via Dry-Run**
   Run the quick pipeline dry-run test using mock data:
   ```bash
   python scripts/run_pipeline.py
   ```
   This generates the mock submission file at `output/pred.csv`.

3. **Run Validation Suite Checks**
   Orchestrate formatting, row count, unique ID, and value constraint tests:
   ```bash
   python scripts/run_full_validation.py --skip-gold --dry-run
   ```

4. **Verify Exit Status**
   - The validation commands must complete successfully (Exit Code 0).
   - Resolve any warnings/errors (e.g. invalid columns, null answers, duplicate qids) before proceeding to packaging or deployment steps.

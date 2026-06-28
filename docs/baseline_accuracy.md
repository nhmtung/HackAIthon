# Baseline Accuracy Measurement

- **Date:** 2026-06-15
- **Pipeline Version:** v0.5.1
- **Model:** Qwen/Qwen2.5-3B-Instruct-AWQ (Simulated Baseline)
- **Prompt Mode:** `zero_shot`

## Metrics Summary

| Metric | Value | Delta vs. Previous | Notes |
|---|---|---|---|
| Overall Accuracy | 26.00% | Base | 13/50 matched questions |
| Accuracy (RAG) | 31.25% | Base | 5/16 matched questions |
| Accuracy (Math) | 18.18% | Base | 2/11 matched questions |
| Accuracy (Factual) | 26.09% | Base | 6/23 matched questions |
| 95th Percentile Latency | 89.85 ms | Base | Simulated local benchmark |
| Format Violations | 0 | Base | Fully compliant with schema |

## Notes
- Validation suite successfully executed using `scripts/run_full_validation.py`.
- Submission format validated using `scripts/validate_submission.py`.
- Per-question latencies and token usage tracked under `docs/performance_profile.json`.

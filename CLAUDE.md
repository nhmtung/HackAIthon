# CLAUDE.md — HackAIthon 2026 Table C Platform Rules

Behavioral guidelines to reduce common LLM coding mistakes, combined with project-specific HackAIthon 2026 specifications.

## 1. Think Before Coding
* **Don't assume. Don't hide confusion. Surface tradeoffs.**
* Before implementing:
  - State your assumptions explicitly. If uncertain, ask.
  - If multiple interpretations exist, present them - don't pick silently.
  - If a simpler approach exists, say so. Push back when warranted.
  - If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First
* **Minimum code that solves the problem. Nothing speculative.**
  - No features beyond what was asked.
  - No abstractions for single-use code.
  - No "flexibility" or "configurability" that wasn't requested.
  - No error handling for impossible scenarios.
  - If you write 200 lines and it could be 50, rewrite it.

## 3. Surgical Changes
* **Touch only what you must. Clean up only your own mess.**
  - Don't "improve" adjacent code, comments, or formatting.
  - Don't refactor things that aren't broken.
  - Match existing style.
  - Remove imports/variables/functions that your changes made unused.

## 4. Goal-Driven Execution
* **Define success criteria. Loop until verified.**
  - Write tests or run validation scripts after code modifications.
  - Every changed line should trace directly to a verifiable goal.

## 5. Technology Stack & Hard Constraints
* **Language Runtime**: Python >= 3.10. UTF-8 encoding is mandatory for all file operations (`encoding="utf-8"`).
* **Approved Model Registry**: Qwen/Qwen2.5-3B-Instruct (and AWQ/GPTQ quantized variants) matching the ≤ 5B parameter size ceiling.
* **Deterministic Inference**: temperature = 0, top_p = 1.0, seed = 42, repetition_penalty = 1.0.
* **No Network Calls**: Inference pipeline must run offline. No external APIs or search APIs allowed.
* **Format Compliance**: Output must be written to `/output/pred.csv` with columns `qid,answer` matching the exact case and domain (`answer ∈ {A, B, C, D}`).

## 6. CLI Commands
* Run pipeline test: `python scripts/run_pipeline.py`
* Run full validation suite: `python scripts/run_full_validation.py --skip-gold --dry-run`
* Verify environment: `python scripts/verify_env.py`

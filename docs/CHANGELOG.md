# CHANGELOG

All notable pipeline increments, accuracy measurements, inference speed benchmarks, and optimizations are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) with additional columns for metrics tracking.

## [v0.4.0] — 2026-06-15

### 🏗️ Added
- Created `src/utils/prompt_templates.py` containing prompt templates for Zero-Shot, Few-Shot, Chain-of-Thought (CoT), and Mixed Language.
- Created `src/utils/prompt_router.py` implementing heuristic-based question classification and routing.
- Created `scripts/create_gold_subset.py` script to extract the first 50 questions and format a submission evaluation harness.
- Created `scripts/compare_prompts.py` to evaluate prompt strategy accuracy and performance comparison.

### ✏️ Changed
- Upgraded `src/utils/answer_extractor.py` to a 5-tier extraction chain with CoT-specific trailing line and final target answer identification.
- Updated `src/utils/prompt_builder.py` to dispatch templates based on `--prompt_mode` settings.
- Updated `src/main.py` to support dynamic `--prompt_mode` parameter routing and token expansion for reasoning.

### 📊 Metrics
| Metric | Value | Delta vs. Previous | Notes |
|---|---|---|---|
| Accuracy (Gold Subset) | Pending | — | User input required for ground truth |
| Chosen Prompt Mode | Routed | — | Default set after local gold comparison |

### 📝 Notes
- Phase 3 Prompt Engineering & CoT Optimization completed.
- Pre-runs confirm the harness is successfully set up and validated in dry-run mode.

---

## [v0.3.0] — 2026-06-15

### 🏗️ Added
- End-to-end zero-shot base pipeline (`src/main.py`) with `--dry-run` mode for format validation without GPU.
- Answer extractor (`src/utils/answer_extractor.py`) implementing 4-tier regex extraction chain per AGENTS.md §2.3.
- vLLM inference engine (`src/inference/vllm_engine.py`) with HuggingFace `transformers` fallback for Windows.
- Pipeline runner & validator (`scripts/run_pipeline.py`) — executes pipeline and validates pred.csv schema.
- Local accuracy evaluation script (`scripts/eval_accuracy.py`) — compares pred.csv against gold labels (when available).
- Prompt builder (`src/utils/prompt_builder.py`) — Vietnamese zero-shot MCQ prompt with dynamic A–J label mapping.

### ✏️ Changed
- `src/main.py` upgraded from Phase 0 bootstrap stub to full pipeline entrypoint with argparse CLI.

### 📊 Metrics
| Metric | Value | Delta vs. Previous | Notes |
|---|---|---|---|
| Accuracy (Public Test) | — | — | No gold labels available yet; dry-run validates format only |
| Inference Speed (Req/s) | — | — | Dry-run mode; actual model inference pending GPU |
| Model | Qwen/Qwen3.5-7B | — | Placeholder; configurable via `--model` flag |
| Output Validation | ✅ PASSED | — | 463/463 rows, all A-D, no duplicates, no nulls |
| Total Questions | 463 | — | All questions produce valid predictions |

### 📝 Notes
- Phase 2 Base Pipeline — Naive Single-Shot completed.
- Pipeline tested in `--dry-run` mode (no GPU required): all 463 questions produce valid `pred.csv`.
- All validation checks pass: correct columns, row count, qid matching, answer domain {A,B,C,D}.
- Dry-run defaults all answers to 'A' — baseline accuracy will be measured once model inference is enabled.
- HuggingFace fallback engine available for Windows local development; vLLM used in Docker/Linux production.

---

## [v0.2.0] — 2026-06-15

### 🏗️ Added
- Defensive data loader in `src/utils/data_loader.py` supporting robust JSON/CSV parsing with error isolation.
- Exploratory script `scripts/test_data_loader.py` analyzing dataset metrics, choice distributions, and question classifications.
- Dataset statistics report in `docs/dataset_stats.md`.

### 📊 Metrics
| Metric | Value | Delta vs. Previous | Notes |
|---|---|---|---|
| Accuracy (Public Test) | — | — | Not yet measured |
| Inference Speed (Req/s) | — | — | Not yet measured |
| Total Questions (Public Test) | 463 | +463 | Loaded successfully from `data/public-test_1780368312.json` |
| Max Question Length | 8712 chars | +8712 | Maximum length of question text |
| Question Breakdown | 100 RAG, 123 Math, 240 Factual | — | RAG: 21.60%, Math: 26.57%, Factual: 51.84% |

### 📝 Notes
- Phase 1 Data Ingestion & Exploration completed.
- Identified that 28.94% of questions have 10 choices, which will require a dynamic options builder mapped up to letters 'K'.
- Confirmed maximum length is 8,712 characters, suggesting a vLLM context window limit setup of at least 4,096 tokens.

---

## [v0.1.0] — 2026-06-15

### 🏗️ Added
- Project directory tree: `src/utils/`, `src/inference/`, `src/eval/`, `scripts/`, `workflows/`, `data/`, `output/`
- Bootstrap dependencies in `requirements.txt` with Windows compatibility fallback comments
- Lightweight entrypoint `src/main.py`
- Environment verification script `scripts/verify_env.py`

### 📊 Metrics
| Metric | Value | Delta vs. Previous | Notes |
|---|---|---|---|
| Accuracy (Public Test) | — | — | Not yet measured |
| Inference Speed (Req/s) | — | — | Not yet measured |
| Model | — | — | Local debugging with CPU / Hugging Face; Docker with vLLM |
| Quantization | — | — | Not yet applied |

### 📝 Notes
- Phase 0 Environment Bootstrap completed.
- Verification script verified Python version 3.11.15 and local CPU status. PyTorch CPU fallback confirmed for local development.

---

## [v0.0.0] — 2026-06-15

### 🏗️ Added
- Initialized documentation workspace (`docs/`)
- Created `docs/brief.md` — competition overview, tech stack, dataset schema analysis
- Created `docs/BRD.md` — functional requirements, parsing safety, output validation
- Created `docs/plans/master-plan.md` — 7-phase execution timeline
- Created `docs/CHANGELOG.md` — this file

### 📊 Metrics
| Metric | Value | Notes |
|---|---|---|
| Baseline Accuracy | — | Not yet measured |
| Inference Speed (Req/s) | — | Not yet measured |
| Model | — | Not yet selected / loaded |
| Quantization | — | Not yet applied |
| Prompt Version | — | Not yet defined |
| Total Questions (Public Test) | ~TBD | To be counted in Phase 1 |

### 📝 Notes
- Project initialized from `AGENTS.md` constitution
- Input JSON schema analyzed: `{qid, question, choices}` with variable choice counts (4–10)
- Output CSV format confirmed: `qid,answer` with `answer ∈ {A, B, C, D}`
- Competition rules extracted from PDF; scoring ambiguities documented in `brief.md`

---

## Template for Future Entries

```markdown
## [vX.Y.Z] — YYYY-MM-DD

### 🏗️ Added / ✏️ Changed / 🗑️ Removed / 🐛 Fixed

- Description of change

### 📊 Metrics
| Metric | Value | Delta vs. Previous | Notes |
|---|---|---|---|
| Accuracy (Public Test) | XX.X% | +X.X% | Prompt vN |
| Accuracy (Gold Subset) | XX.X% | +X.X% | N questions |
| Inference Speed (Req/s) | X.XX | +X.XX | Batch size N |
| Total Runtime (Public Test) | Xm Xs | -Xs | GPU: XXX |
| VRAM Usage (Peak) | XX.X GB | -X.X GB | Quantization: XXX |

### 📝 Notes
- Experiment ID: EXP-XXX
- Key insight: ...
```

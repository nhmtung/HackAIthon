# Master Execution Plan

> **Project:** Multi-Task AI Agent — Track C: INNOVATOR
> **Deadline:** Round 1 submission by 2026-06-23
> **Approach:** Iterative phases — each phase produces a testable, measurable increment.

---

## Phase 0: Environment Bootstrap (Day 0)

**Objective:** Establish reproducible development environment.

### Tasks

- [ ] Initialize Python project with `uv` or `pip` + `requirements.txt`
- [ ] Install core dependencies: `vllm`, `transformers`, `torch`, `pandas`, `langchain`, `huggingface_hub`
- [ ] Create project structure:
  ```
  e:\HackAIthon\
  ├── AGENTS.md                    # Agent constitution (exists)
  ├── docs/                        # Documentation workspace (this phase)
  │   ├── brief.md
  │   ├── BRD.md
  │   ├── CHANGELOG.md
  │   └── plans/
  │       └── master-plan.md
  ├── src/
  │   ├── main.py                  # Entrypoint
  │   ├── utils/
  │   │   ├── data_loader.py       # JSON/CSV parser
  │   │   ├── prompt_builder.py    # Prompt template construction
  │   │   └── answer_extractor.py  # Regex-based answer extraction
  │   ├── inference/
  │   │   ├── vllm_engine.py       # vLLM inference wrapper
  │   │   └── model_config.py      # Model selection & quantization config
  │   └── eval/
  │       └── evaluate.py          # Local accuracy evaluation
  ├── scripts/
  │   ├── run_local.py             # Local development runner
  │   ├── eval_accuracy.py         # Accuracy computation script
  │   └── build_docker.sh          # Docker build automation
  ├── Dockerfile
  ├── requirements.txt
  └── data/                        # Local data directory (gitignored)
      └── public-test_1780368312.json
  ```
- [ ] Download and cache primary model: `Qwen/Qwen3.5-7B` (or chosen variant)
- [ ] Verify GPU availability and VRAM capacity

### Exit Criteria
- `uv run python -c "import vllm; print(vllm.__version__)"` succeeds
- Project structure created and documented

---

## Phase 1: Data Ingestion & Exploration (Day 0–1)

**Objective:** Build robust data loading pipeline and understand dataset characteristics.

### Tasks

- [ ] Implement `src/utils/data_loader.py` with defensive JSON/CSV parsing (per BRD FR-01)
- [ ] Write test script `scripts/test_data_loader.py` to validate:
  - Total question count
  - Distribution of choice counts (4, 5, 6, 10, etc.)
  - Average/max question text length (character count)
  - Percentage of questions with embedded context (`Đoạn thông tin:` prefix)
  - Percentage of questions with LaTeX math content
- [ ] Generate dataset statistics report and save to `docs/dataset_stats.md`
- [ ] Categorize questions by type (RAG, Math, Factual, Scientific) — at least heuristically

### Exit Criteria
- `python scripts/test_data_loader.py` runs cleanly, prints statistics
- Dataset statistics document written

### Manual Test
```bash
python scripts/test_data_loader.py
# Expected output: question count, choice distribution, category breakdown
```

---

## Phase 2: Base Pipeline — Naive Single-Shot (Day 1–2)

**Objective:** Establish end-to-end pipeline from input → model inference → output CSV.

### Tasks

- [ ] Implement `src/utils/prompt_builder.py`:
  - Zero-shot Vietnamese MCQ prompt template
  - Dynamic option label mapping (A–J)
  - System prompt enforcing single-letter output
- [ ] Implement `src/utils/answer_extractor.py`:
  - Multi-strategy regex extraction (per BRD FR-02.2)
  - Fallback chain: single-char → regex → first-letter → default "A"
- [ ] Implement `src/inference/vllm_engine.py`:
  - Load model via vLLM `LLM` class
  - Configure `SamplingParams(temperature=0, max_tokens=16, top_p=1.0)`
  - Batch inference support
- [ ] Implement `src/main.py` entrypoint:
  - Load questions from `/data/` (CSV) or local JSON
  - Build prompts → run inference → extract answers → write pred.csv
- [ ] Run full pipeline on public test set
- [ ] Implement `src/eval/evaluate.py` for local accuracy measurement

### Prompt Template v1 (Zero-Shot)
```
Bạn là một trợ lý AI. Hãy đọc câu hỏi sau và chọn đáp án đúng nhất.
Chỉ trả lời bằng MỘT chữ cái (A, B, C, D, ...) — không giải thích.

Câu hỏi: {question}

Các lựa chọn:
{options}

Đáp án:
```

### Exit Criteria
- Full pipeline runs end-to-end without errors
- `pred.csv` generated with correct format (validated by schema check)
- Baseline accuracy measured and logged in CHANGELOG

### Manual Test
```bash
python src/main.py --input data/public-test_1780368312.json --output output/pred.csv
python scripts/eval_accuracy.py --pred output/pred.csv --gold data/gold.csv  # if gold available
```

---

## Phase 3: Prompt Engineering & CoT Optimization (Day 2–4)

**Objective:** Improve accuracy through prompt tuning without changing the model.

### Tasks

- [ ] **Experiment 3.1:** Few-shot prompting — prepend 2–3 solved examples per category
- [ ] **Experiment 3.2:** Chain-of-Thought (CoT) — allow short reasoning then extract final answer
  - Modify `SamplingParams(max_tokens=256)` for CoT
  - Strengthen answer extraction regex for CoT output
- [ ] **Experiment 3.3:** Task-specific routing:
  - Detect question type (RAG vs. Math vs. Factual) via heuristic keywords
  - Apply different prompt templates per category
  - RAG: "Dựa trên đoạn văn trên, ..."
  - Math: "Hãy tính toán từng bước, ..."
  - Factual: "Dựa trên kiến thức chung, ..."
- [ ] **Experiment 3.4:** Thinking mode — if Qwen3.5 supports `/think` or `enable_thinking`, test it
- [ ] **Experiment 3.5:** Language tuning — test Vietnamese-only vs. mixed prompts
- [ ] Compare accuracy across all experiments, select best combination
- [ ] Log all results in CHANGELOG with experiment IDs

### Exit Criteria
- ≥ 3 prompt variants tested with measured accuracy
- Best prompt variant identified and set as default
- Accuracy improvement documented

---

## Phase 4: vLLM Optimization & Speed Tuning (Day 3–5)

**Objective:** Maximize inference throughput (Req/s) for competitive speed scoring.

### Tasks

- [ ] **Quantization:** Test AWQ/GPTQ 4-bit variants of chosen model
  - Compare: full precision (FP16) vs. AWQ-INT4 vs. GPTQ-INT4
  - Measure: accuracy delta vs. speed gain
- [ ] **Batching:** Optimize vLLM batch size
  - Test batch sizes: 1, 4, 8, 16, 32
  - Profile GPU utilization at each level
- [ ] **KV-Cache tuning:**
  - Set `gpu_memory_utilization=0.90` (or higher if stable)
  - Configure `max_model_len` to minimum necessary (based on max question length + max_tokens)
  - Enable `enable_prefix_caching=True` for repeated system prompts
- [ ] **Token budget optimization:**
  - Reduce `max_tokens` to minimum needed (1 for single-letter, 16 for safety, 256 for CoT)
  - Truncate excessively long questions to model's context window
- [ ] **Parallelism:** Test `tensor_parallel_size` if multi-GPU available
- [ ] **Benchmark:** Measure end-to-end Req/s on full public test set
- [ ] Log speed benchmarks in CHANGELOG

### Key vLLM Parameters to Tune
```python
llm = LLM(
    model="Qwen/Qwen3.5-7B-AWQ",     # or chosen variant
    quantization="awq",                # if using quantized model
    gpu_memory_utilization=0.90,
    max_model_len=4096,                # tune based on data analysis
    enable_prefix_caching=True,
    dtype="half",                      # FP16
    # tensor_parallel_size=1,          # increase if multi-GPU
)

sampling_params = SamplingParams(
    temperature=0,
    max_tokens=16,                     # minimal for single-letter output
    top_p=1.0,
    repetition_penalty=1.0,
)
```

### Exit Criteria
- Quantized model tested with accuracy parity (< 2% drop)
- Optimal batch size and memory configuration identified
- Req/s benchmark recorded

---

## Phase 5: Local Evaluation & Validation Suite (Day 4–5)

**Objective:** Build comprehensive evaluation infrastructure.

### Tasks

- [ ] Implement `scripts/eval_accuracy.py`:
  - Load predicted CSV and gold CSV
  - Compute: overall accuracy, per-category accuracy, confusion matrix
  - Output: summary table + per-question error log
- [ ] Implement `scripts/validate_submission.py`:
  - Check pred.csv format compliance (columns, dtypes, value domain)
  - Check for missing qids, duplicate qids, invalid answer values
  - Check file encoding (UTF-8)
- [ ] Create a small gold-label subset (manually label 20–50 questions) for local eval
- [ ] Implement `scripts/benchmark_speed.py`:
  - Measure total inference time
  - Compute Req/s
  - Profile per-question latency distribution
- [ ] Run full validation suite and fix any issues

### Exit Criteria
- Validation script passes on generated pred.csv
- Local accuracy measured on gold subset
- Speed benchmark documented

### Manual Test
```bash
python scripts/validate_submission.py --pred output/pred.csv
python scripts/eval_accuracy.py --pred output/pred.csv --gold data/gold_subset.csv
python scripts/benchmark_speed.py --input data/public-test_1780368312.json
```

---

## Phase 6: Docker Packaging & Final Submission (Day 5–6)

**Objective:** Package everything into a submission-ready Docker container.

### Tasks

- [ ] Write `Dockerfile`:
  ```dockerfile
  FROM nvidia/cuda:12.1-runtime-ubuntu22.04
  # Install Python, pip, dependencies
  # COPY model weights (or download in build)
  # COPY source code
  # Set entrypoint
  ENTRYPOINT ["python", "src/main.py"]
  ```
- [ ] Write `scripts/build_docker.sh`:
  - Build image with proper tag
  - Test locally with mounted `/data` and `/output` volumes
  - Push to Docker Hub
- [ ] Write `docker-compose.yml` for local testing:
  ```yaml
  services:
    agent:
      build: .
      volumes:
        - ./data:/data
        - ./output:/output
      deploy:
        resources:
          reservations:
            devices:
              - driver: nvidia
                count: 1
                capabilities: [gpu]
  ```
- [ ] Test Docker container end-to-end:
  - Mount public test data → run container → verify pred.csv output
  - Verify same results as local run (determinism check)
- [ ] Write `README.md` with reproduction instructions
- [ ] Prepare technical documentation (free-format, per CP-02)
- [ ] Push to Docker Hub + GitHub
- [ ] Submit on leaderboard

### Exit Criteria
- Docker container runs successfully with `docker run`
- pred.csv output matches local run results
- All deliverables uploaded (Docker Hub, GitHub, documentation)

---

## Phase Summary & Time Budget

| Phase | Duration | Key Output | Priority |
|---|---|---|---|
| Phase 0 | 0.5 day | Environment ready | P0 |
| Phase 1 | 0.5 day | Data loader + statistics | P0 |
| Phase 2 | 1 day | End-to-end baseline pipeline | P0 |
| Phase 3 | 2 days | Optimized prompts | P1 |
| Phase 4 | 1.5 days | Speed-optimized inference | P1 |
| Phase 5 | 1 day | Evaluation & validation suite | P0 |
| Phase 6 | 1 day | Docker container + submission | P0 |
| **Total** | **~7 days** | | |

> **Note:** Phases 3 and 4 can be parallelized. Phase 5 should start as early as Phase 2 completion. Phase 6 should have a buffer day before the deadline.

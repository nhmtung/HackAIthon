# ANTI-GRAVITY AGENT CONSTITUTION v2.0

## Track C — INNOVATOR | Vietnamese Student HackAIthon 2026

> **Classification:** RUNTIME SYSTEM PROMPT — PRIMARY CONSTRAINT DOCUMENT
> **Scope:** Every response, every code generation, every file modification, every tool invocation.
> **Authority:** This document is the supreme constitution of the project. All downstream agent workflows, subagent definitions, and code-generation tasks are strictly bound by every directive herein. Violations are unrecoverable failures.
> **Companion Docs:** `docs/brief.md` (competition context), `docs/BRD.md` (functional requirements), `docs/plans/master-plan.md` (execution timeline), `docs/CHANGELOG.md` (version log).

---

## §1. COMPLIANCE BARRICADES — LOCKED EXECUTION PROFILE

### §1.1 Language Runtime

| Constraint | Value | Enforcement |
|---|---|---|
| Language | **Python >= 3.10** | No other runtime (Node.js, Rust, Go, Java, etc.) may be used for any pipeline component. Shell scripts (`.sh`, `.ps1`) are permitted ONLY for automation wrappers around Python entrypoints. |
| Type Hints | Required | All function signatures must use Python type hints (`def func(x: str) -> list[dict]:`). |
| Encoding | **UTF-8** | Every file read, file write, and string operation must explicitly specify `encoding="utf-8"`. No implicit system-default encoding. |

### §1.2 Approved Model Registry

The following is the **COMPLETE AND EXHAUSTIVE** list of models that may be loaded, referenced, downloaded, or invoked. Any model not on this list is **PROHIBITED**.

#### Base LLMs (Select One or Combine)

| Model Family | Parameter Ceiling | Examples |
|---|---|---|
| **Qwen3.5 Series** | **≤ 9B parameters** | `Qwen/Qwen3.5-1.5B`, `Qwen/Qwen3.5-4B`, `Qwen/Qwen3.5-7B`, and quantized variants (AWQ, GPTQ, GGUF) of models ≤ 9B |
| **Gemma-4 Series** | No explicit cap stated | `google/gemma-4-*` family |

#### Supporting Models (Embedding / Rerank)

| Model | Purpose | HuggingFace ID |
|---|---|---|
| **BGE-m3** | Dense/sparse/ColBERT multilingual embedding for RAG retrieval | `BAAI/bge-m3` |
| **Qwen-Rerank** | Cross-encoder reranking for RAG pipeline | `Qwen/Qwen-Rerank` (or equivalent Qwen reranker) |

#### Absolute Prohibitions

- ❌ No external API calls (OpenAI, Anthropic, Google AI Studio, Cohere, etc.)
- ❌ No internet access during inference
- ❌ No models outside the registry above (no Llama, Mistral, Phi, Claude, GPT, etc.)
- ❌ No pre-computed answer lookup tables or cached answer databases
- ❌ No hard-coded answers for specific `qid` values

### §1.3 Approved Library Set

Only the following Python libraries (and their transitive dependencies) may be used as core pipeline components:

```
vllm              # High-throughput LLM serving with PagedAttention
transformers      # HuggingFace model loading and tokenization
torch             # PyTorch backend (GPU compute)
pandas            # Data manipulation, CSV I/O
langchain         # Orchestration, prompt templates, chains
huggingface_hub   # Model downloading and caching
```

**Permitted utility libraries** (standard library or lightweight helpers):

```
json, csv, os, sys, re, pathlib, glob, ast, time, logging, argparse,
typing, dataclasses, collections, math, functools, itertools, hashlib,
unittest, pytest  # for testing only
```

**Before adding ANY library not listed above:** Stop and ask the user for explicit approval. Justify the need. Never silently introduce unapproved dependencies.

### §1.4 Compliance Checkpoint

Before generating or modifying ANY code, mentally verify:

1. ✅ Does this code only use Python >= 3.10?
2. ✅ Does this code only load models from the Approved Model Registry (§1.2)?
3. ✅ Does this code only import libraries from the Approved Library Set (§1.3)?
4. ✅ Does this code avoid all external API calls and internet access during inference?
5. ✅ Does the output conform to the Deterministic Output Specification (§2)?

If ANY answer is NO → **STOP. DO NOT GENERATE. Alert the user.**

---

## §2. DETERMINISTIC OUTPUT ENFORCEMENT

### §2.1 Output File Specification

| Parameter | Value | Non-Negotiable |
|---|---|---|
| File path | `/output/pred.csv` | ✅ |
| Encoding | UTF-8 (no BOM) | ✅ |
| Column count | Exactly **2** | ✅ |
| Column names | `qid,answer` (this exact order, this exact casing) | ✅ |
| Header row | Required: `qid,answer` | ✅ |
| `qid` values | Must match input `qid` values exactly, one-to-one | ✅ |
| `answer` values | Single uppercase letter ∈ **{A, B, C, D}** | ✅ |
| Row count | Must equal input question count | ✅ |
| Trailing newline | Permitted but not required | — |

### §2.2 Forbidden Output Content

The following must **NEVER** appear in any cell of `pred.csv`:

| Forbidden Content | Example | Why |
|---|---|---|
| Reasoning text | `"The answer is A because..."` | Instant disqualification |
| Conversational filler | `"Sure!"`, `"Let me think..."` | Instant disqualification |
| Markdown artifacts | `"**A**"`, `` `A` `` | Parsing failure |
| Multiple letters | `"A,B"`, `"AB"` | Ambiguous |
| Lowercase letters | `"a"`, `"c"` | Format violation |
| Empty cells | `""`, `" "` | Missing prediction |
| Numeric answers | `"1"`, `"3"` | Wrong domain |
| Whitespace padding | `" A "`, `"A\n"` | Parsing failure |
| Quotes | `'"A"'` | Extra characters |

### §2.3 Answer Extraction Pipeline (Mandatory Implementation)

Every inference script MUST implement a **4-tier extraction chain** to convert raw LLM output into a single valid letter. This is non-negotiable.

```python
import re

# Precompiled regex — matches answer indicators in Vietnamese and English
_ANSWER_RE = re.compile(
    r'(?:Đáp\s*án|Answer|Câu\s*trả\s*lời|Chọn)\s*[:：]?\s*([A-D])\b'
    r'|'
    r'(?:^|\n)\s*([A-D])\s*[\.\)\]\b]',
    re.IGNORECASE
)

def extract_answer(raw: str, num_choices: int = 4) -> str:
    """
    4-tier extraction: single-char → regex → first-valid-letter → fallback 'A'.
    NEVER returns empty string. NEVER returns invalid letter.
    """
    valid = {chr(65 + i) for i in range(min(num_choices, 4))}  # {A,B,C,D} max
    s = raw.strip()

    # Tier 1: Output is already a single valid character
    if len(s) == 1 and s.upper() in valid:
        return s.upper()

    # Tier 2: Regex match against known answer patterns
    for m in _ANSWER_RE.finditer(raw):
        letter = (m.group(1) or m.group(2)).upper()
        if letter in valid:
            return letter

    # Tier 3: First valid uppercase letter in the output
    for ch in raw:
        if ch.upper() in valid:
            return ch.upper()

    # Tier 4: Absolute fallback — never return empty
    return "A"
```

**Rules for this function:**
- It MUST be used for EVERY prediction, no exceptions.
- It MUST return exactly one character from `{A, B, C, D}`.
- It MUST NOT raise exceptions under any input.
- It MUST handle None, empty string, and garbage input gracefully.

### §2.4 Output Writer (Mandatory Implementation)

```python
import pandas as pd
import os

def write_predictions(predictions: list[dict], path: str = "/output/pred.csv") -> None:
    """Write validated predictions to CSV. Creates parent directories."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df = pd.DataFrame(predictions, columns=["qid", "answer"])

    # Final validation gate
    assert df.shape[1] == 2, f"Column count violation: {df.shape[1]}"
    assert list(df.columns) == ["qid", "answer"], f"Column name violation: {list(df.columns)}"
    assert df["answer"].str.fullmatch(r"[A-D]").all(), \
        f"Answer domain violation: {df[~df['answer'].str.fullmatch(r'[A-D]')]['answer'].tolist()}"
    assert not df["qid"].duplicated().any(), "Duplicate qid detected"
    assert not df["answer"].isna().any(), "Null answer detected"

    df.to_csv(path, index=False, encoding="utf-8")
```

### §2.5 Inference Configuration Constraints

All vLLM / transformers inference calls MUST use:

```python
# Deterministic decoding — no randomness
temperature = 0          # Greedy decoding
top_p = 1.0              # No nucleus sampling
max_tokens = 16          # Minimal for single-letter (increase to 256–512 ONLY for CoT experiments)
repetition_penalty = 1.0  # No repetition penalty distortion
seed = 42                # Fixed seed for reproducibility
```

---

## §3. DATA SAFETY & FAIL-SAFES

### §3.1 Universal Error Handling Mandate

**Every function** that touches I/O, parsing, model inference, or string manipulation MUST be wrapped in a `try-except` block. The pipeline must NEVER crash on a single malformed question. It must skip, log, and continue.

#### Pattern: Safe Question Processing

```python
def process_question(item: dict, index: int) -> dict | None:
    """Process a single question. Returns prediction dict or None on failure."""
    try:
        qid = str(item["qid"]).strip()
        question = str(item["question"]).strip()
        choices = item["choices"]

        if not qid:
            raise ValueError("Empty qid")
        if not question:
            raise ValueError("Empty question text")
        if not isinstance(choices, list) or len(choices) < 2:
            raise ValueError(f"Invalid choices array: {type(choices).__name__}, len={len(choices) if isinstance(choices, list) else 'N/A'}")

        # ... build prompt, run inference, extract answer ...
        answer = extract_answer(raw_output, num_choices=len(choices))
        return {"qid": qid, "answer": answer}

    except KeyError as e:
        print(f"[ERROR] Item {index}: Missing required field {e}. Defaulting to 'A'.")
        return {"qid": item.get("qid", f"UNKNOWN_{index}"), "answer": "A"}
    except (ValueError, TypeError) as e:
        print(f"[ERROR] Item {index} (qid={item.get('qid', '?')}): {e}. Defaulting to 'A'.")
        return {"qid": item.get("qid", f"UNKNOWN_{index}"), "answer": "A"}
    except Exception as e:
        print(f"[CRITICAL] Item {index}: Unexpected error: {e}. Defaulting to 'A'.")
        return {"qid": item.get("qid", f"UNKNOWN_{index}"), "answer": "A"}
```

**Iron rules:**
- A malformed question MUST still produce a row in `pred.csv` with answer `"A"`.
- An inference failure (OOM, timeout, model error) MUST still produce answer `"A"`.
- The pipeline MUST produce exactly N rows for N input questions — no more, no less.
- `print()` or `logging` for all warnings/errors — never silent failures.

### §3.2 Input File Detection (Docker Runtime)

The entrypoint MUST detect input files in this priority order:

```python
import os

def resolve_input_path() -> str:
    """Resolve input file path. Raises FileNotFoundError only if NO file exists."""
    candidates = [
        "/data/private_test.csv",
        "/data/public_test.csv",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    raise FileNotFoundError(
        f"No input file found. Checked: {candidates}. "
        f"Contents of /data/: {os.listdir('/data/') if os.path.isdir('/data/') else 'DIRECTORY NOT FOUND'}"
    )
```

### §3.3 JSON Parsing Safety (Local Development)

When loading `*.json` files during local development:

- MUST use `encoding="utf-8"` explicitly.
- MUST catch `json.JSONDecodeError`, `FileNotFoundError`, `UnicodeDecodeError`.
- MUST validate top-level structure is a `list`.
- MUST validate each item contains `qid` (str), `question` (str), `choices` (list[str]).
- MUST strip whitespace from all string fields.
- MUST skip and log malformed items — never crash.

### §3.4 CSV Parsing Safety (Production Runtime)

When loading `*.csv` files from `/data/`:

- MUST use `pd.read_csv(..., encoding="utf-8")`.
- MUST handle the `choices` column as either a native list or a string-encoded list (use `ast.literal_eval` with try-except).
- MUST validate all expected columns exist before processing.
- MUST handle empty rows, NaN values, and type mismatches gracefully.

### §3.5 Private Test Readiness (2,000 Questions)

The pipeline will be evaluated on **2,000 hidden Private Test questions** in Round 2. Design for:

- Questions may contain edge cases not seen in the public test set.
- Questions may have unusual Unicode characters, extremely long context (>15,000 chars), or malformed LaTeX.
- Some questions may push the model's context window limit — implement graceful truncation.
- Total runtime must be reasonable for 2,000 questions (target: < 60 minutes).

---

## §4. DEVELOPMENT PROCESS & AUTOMATED LOGGING

### §4.1 Manual Testing After Each Phase

Upon completing any function, module, class, or file structure, you MUST:

1. Write a specific test script or test command.
2. Provide exact execution instructions:
   ```
   Manual Test:
   $ python scripts/test_<module_name>.py
   Expected: <what success looks like>
   ```
3. Never mark a phase as complete until the test passes.

### §4.2 Automation-First for Humans

If a task requires complex manual steps (environment setup, data conversion, Docker builds, model downloads), you MUST:

1. Proactively write an automation script (`.py` preferred, `.sh` acceptable).
2. Name it descriptively: `scripts/setup_env.py`, `scripts/download_model.py`, `scripts/build_docker.sh`.
3. Ensure the script is executable with a single command.

### §4.3 CHANGELOG Auto-Injection Protocol (Mandatory Post-Modification Trigger)

**This rule activates AFTER EVERY successful code modification that alters pipeline logic or could impact evaluation metrics.**

#### Step 1: Walkthrough Summary

Immediately after the modification, present the user with a structured summary:

```
──────────────────────────────────────────
📋 CHANGE SUMMARY
──────────────────────────────────────────
Files Modified : <list of files>
Change Type    : <Added | Changed | Fixed | Removed | Optimized>
Description    : <1-2 sentence description of what changed>
Rationale      : <why this change was made>

📊 ESTIMATED IMPACT
──────────────────────────────────────────
Accuracy Impact   : <+X.X% | -X.X% | Neutral | Unknown>
Speed Impact      : <+X.XX Req/s | -X.XX Req/s | Neutral | Unknown>
VRAM Impact       : <+X.X GB | -X.X GB | Neutral | Unknown>
Risk Level        : <Low | Medium | High>
──────────────────────────────────────────
```

#### Step 2: CHANGELOG Entry Generation

Then immediately append an entry to `docs/CHANGELOG.md` in this format:

```markdown
## [vX.Y.Z] — YYYY-MM-DD

### <emoji> <Change Type>
- <Description of change>

### 📊 Metrics
| Metric | Value | Delta vs. Previous | Notes |
|---|---|---|---|
| Accuracy (Est.) | XX.X% | +X.X% | <method/prompt version> |
| Inference Speed | X.XX Req/s | +X.XX | <batch size, quantization> |
| VRAM Usage | XX.X GB | -X.X GB | <model variant> |

### 📝 Notes
- <Key insight or rationale>
```

#### Step 3: User Confirmation

After presenting the summary, ask: *"Should I log this entry to `docs/CHANGELOG.md`?"*

#### Version Numbering Convention

| Change Type | Version Bump | Example |
|---|---|---|
| Documentation only | `v0.0.Z` | v0.0.1, v0.0.2 |
| New module / feature | `v0.Y.0` | v0.1.0, v0.2.0 |
| Prompt / strategy change | `v0.Y.0` | v0.3.0 |
| Breaking pipeline change | `vX.0.0` | v1.0.0 |
| Bug fix | `v0.0.Z` | v0.0.3 |

---

## §5. DOCKER CONTAINER ARCHITECTURE

### §5.1 Container Specification

```
┌─────────────────────────────────────────────────────┐
│                 Docker Container                     │
│                                                      │
│  Base Image : nvidia/cuda:12.1-runtime-ubuntu22.04   │
│  Python     : >= 3.10                                │
│  GPU        : Required (CUDA)                        │
│                                                      │
│  VOLUMES:                                            │
│    /data/    ← Mounted by evaluator (read-only)      │
│    /output/  ← Written by pipeline (write)           │
│                                                      │
│  ENTRYPOINT:                                         │
│    python src/main.py                                │
│                                                      │
│  FLOW:                                               │
│    1. Detect input: /data/private_test.csv            │
│       fallback:     /data/public_test.csv             │
│    2. Load questions                                  │
│    3. Load model (cached in image)                    │
│    4. Run inference (batched, deterministic)          │
│    5. Extract answers (4-tier regex chain)            │
│    6. Write /output/pred.csv                          │
│    7. Exit 0                                          │
└─────────────────────────────────────────────────────┘
```

### §5.2 Container Requirements

- All model weights MUST be baked into the image (no runtime downloads).
- The container MUST work offline (no internet access during inference).
- The container MUST exit with code 0 on success.
- The container MUST produce `/output/pred.csv` even if some questions fail (§3.1 fallback).

---

## §6. DATASET CHARACTERISTICS (REFERENCE)

### §6.1 Input Schema

```json
{
  "qid": "test_XXXX",          // string, zero-padded 4-digit ID
  "question": "...",           // string, Vietnamese text, may contain:
                               //   - Embedded passages (prefix: "Đoạn thông tin:")
                               //   - LaTeX math ($...$, \frac{}{})
                               //   - Escaped newlines (\n)
                               //   - 50 to 15,000+ characters
  "choices": ["...", "..."]    // array of 4–10 string options
}
```

### §6.2 Question Taxonomy

| Category | Detection Heuristic | Prompt Strategy |
|---|---|---|
| **RAG / Reading Comprehension** | `question` contains `"Đoạn thông tin:"` or `"Tiêu đề:"` | Extract answer from provided passage |
| **Quantitative / Mathematical** | Contains LaTeX (`$`, `\frac`), numbers, units | Step-by-step calculation |
| **Factual / Academic** | Short question, no context passage | Rely on model's parametric knowledge |
| **Scientific Taxonomy** | Domain-specific terminology, multiple passages | Cross-reference and synthesize |

### §6.3 Variable Choice Counts

Questions have between **4 and 10 choices**. The competition rules state `answer ∈ {A, B, C, D}`, but the dataset contains questions with up to 10 options. Resolution:

- Map `choices[i]` → `chr(65 + i)` dynamically (A=0, B=1, ..., J=9).
- The answer extraction function (§2.3) clamps output to `{A, B, C, D}` for safety.
- Log any prediction that would have been E–J for post-analysis.

---

## §7. PERFORMANCE TARGETS

| Metric | Target | Stretch Goal | Scoring Weight |
|---|---|---|---|
| **Accuracy** | > 70% | > 85% | 80 points |
| **Inference Speed** | > 5 Req/s | > 15 Req/s | 10 points |
| **Innovation Score** | Documented strategy | Novel approach | 10 points |

### §7.1 Speed Optimization Levers

| Lever | Expected Impact | Phase |
|---|---|---|
| AWQ/GPTQ 4-bit quantization | 2–3× throughput | Phase 4 |
| vLLM batched inference | 3–5× throughput | Phase 2+ |
| `max_tokens=16` (single-letter mode) | Major speed gain | Phase 2 |
| `enable_prefix_caching=True` | 10–30% throughput gain for repeated system prompts | Phase 4 |
| `gpu_memory_utilization=0.90` | Maximize KV-cache capacity | Phase 4 |
| Truncate long contexts to `max_model_len` | Prevent OOM, maintain throughput | Phase 4 |

---

## §8. EXECUTION TIMELINE (REFERENCE)

| Phase | Name | Duration | Key Output |
|---|---|---|---|
| 0 | Environment Bootstrap | 0.5 day | Dependencies installed, project structure |
| 1 | Data Ingestion & Exploration | 0.5 day | `data_loader.py`, dataset statistics |
| 2 | Base Pipeline (Single-Shot) | 1 day | End-to-end inference, baseline accuracy |
| 3 | Prompt Engineering & CoT | 2 days | Optimized prompts, accuracy improvement |
| 4 | vLLM Speed Optimization | 1.5 days | Quantization, batching, KV-cache tuning |
| 5 | Evaluation & Validation Suite | 1 day | `eval_accuracy.py`, `validate_submission.py` |
| 6 | Docker Packaging & Submission | 1 day | Docker image on Docker Hub, GitHub repo |

**Deadline: Round 1 submission by 2026-06-23.**

---

## §9. PROJECT STRUCTURE (CANONICAL)

```
e:\HackAIthon\
├── AGENTS.md                          # THIS FILE — supreme constitution
├── docs/
│   ├── brief.md                       # Competition overview & dataset analysis
│   ├── BRD.md                         # Business requirements & functional specs
│   ├── CHANGELOG.md                   # Engineering version log
│   └── plans/
│       └── master-plan.md             # Phase-by-phase execution timeline
├── src/
│   ├── main.py                        # Docker entrypoint
│   ├── utils/
│   │   ├── data_loader.py             # JSON/CSV parser with safety wrappers
│   │   ├── prompt_builder.py          # Prompt template construction
│   │   └── answer_extractor.py        # 4-tier regex answer extraction
│   ├── inference/
│   │   ├── vllm_engine.py             # vLLM inference wrapper
│   │   └── model_config.py            # Model selection & quantization config
│   └── eval/
│       └── evaluate.py                # Local accuracy evaluation
├── scripts/
│   ├── run_local.py                   # Local development runner
│   ├── eval_accuracy.py               # Accuracy computation
│   ├── validate_submission.py         # pred.csv format validation
│   ├── benchmark_speed.py             # Inference speed benchmarking
│   └── build_docker.sh                # Docker build automation
├── Dockerfile                         # Container definition
├── requirements.txt                   # Pinned dependencies
└── data/                              # Local data (gitignored)
    └── public-test_1780368312.json    # Public test set
```

---

## §10. AGENT BEHAVIORAL DIRECTIVES

### §10.1 Context Loading

At the start of every conversation or task:

1. Read `AGENTS.md` (this file) as the primary constraint.
2. Read `docs/CHANGELOG.md` to understand current project state and version.
3. Read `docs/plans/master-plan.md` to understand which phase is active.
4. Reference `docs/brief.md` and `docs/BRD.md` as needed for technical details.

### §10.2 Response Discipline

- **Be precise.** No vague suggestions. Every code block must be copy-pasteable.
- **Be defensive.** Every I/O function must have try-except. Every output must be validated.
- **Be measurable.** Every change must have an estimated impact on accuracy and speed.
- **Be compliant.** Every response must respect the Compliance Barricades (§1).
- **Be atomic.** One logical change per implementation step. Test before moving on.

### §10.3 Forbidden Actions

- ❌ Never generate code that imports unapproved libraries without user consent.
- ❌ Never hardcode answers for specific question IDs.
- ❌ Never skip error handling to "keep things simple."
- ❌ Never generate pred.csv with reasoning text, markdown, or multi-character answers.
- ❌ Never modify this AGENTS.md file without explicit user instruction.
- ❌ Never assume the private test schema is identical to the public test — always code defensively.

### §10.4 AUTOMATED VIBE-GIT WORKFLOW (AUTONOMOUS SKILLS)

You (the AI Agent) are granted autonomous permission to execute local Git commands under the following strict state-machine rules:

#### Trigger Conditions (When to Commit)
- **DO NOT** commit on minor typos or halfway through coding.
- **MUST** automatically trigger a commit loop immediately after:
  1. A code modification passes the validation test script successfully.
  2. A core architectural refactoring is completed (e.g., changes to `data_loader.py` or prompt wrappers).
  3. Performance statistics inside `docs/CHANGELOG.md` are updated.

#### Execution Routine Sequence
When a trigger condition is met, you must execute these steps sequentially using your terminal/command execution tool:
1. Run `git pull origin main` to fetch and rebase any upstream syncs.
2. Run `git add .` to stage the changes (relying strictly on `.gitignore` boundaries).
3. Generate a conventional commit message based on the task:
   - Schema: `<type>(<scope>): <short description>` (e.g., `feat(ingest): implement try-catch in json data parser`).
4. Execute `git commit -m "<your_generated_message>"`.
5. Execute `git push origin main` to broadcast the state to GitHub.
6. Print a clear execution walkthrough to the developer: "🚀 Autonomous Sync Completed: [Commit Hash] - [Commit Message]".

#### Failure Mitigation
- If `git push` fails due to a merge conflict, stop immediately, do not use `--force`, print the git log error, and ask the developer for visual alignment intervention.

---

*End of Constitution. All directives are active and binding.*
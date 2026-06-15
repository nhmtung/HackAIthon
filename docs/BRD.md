# Business Requirements Document (BRD)

> **Project:** Multi-Task AI Agent — Track C: INNOVATOR
> **Competition:** Vietnamese Student HackAIthon 2026
> **Document Version:** 1.0.0
> **Last Updated:** 2026-06-15

---

## 1. Functional Requirements

### FR-01: Data Ingestion & Parsing

#### FR-01.1: Input Format Detection

The entrypoint must auto-detect the input file format at `/data/`:

| Priority | File | Format | Action |
|---|---|---|---|
| 1 | `/data/public_test.csv` | CSV | Parse with `pandas.read_csv()` |
| 2 | `/data/private_test.csv` | CSV | Parse with `pandas.read_csv()` |
| 3 | Local dev: `*.json` | JSON array | Parse with `json.load()` |

The entrypoint script must check file existence in priority order:
```python
import os
if os.path.exists("/data/private_test.csv"):
    input_path = "/data/private_test.csv"
elif os.path.exists("/data/public_test.csv"):
    input_path = "/data/public_test.csv"
else:
    raise FileNotFoundError("No input file found at /data/")
```

#### FR-01.2: JSON Parsing Safety (Local Development)

When loading the local JSON file (`public-test_1780368312.json`), implement defensive parsing:

```python
import json

def load_questions(filepath: str) -> list[dict]:
    """
    Safely load and validate the question dataset.
    Returns a list of validated question dicts.
    Raises ValueError on schema violations.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Malformed JSON at {filepath}: {e}")
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {filepath}")
    except UnicodeDecodeError as e:
        raise ValueError(f"Encoding error in {filepath}: {e}")

    if not isinstance(raw_data, list):
        raise ValueError(f"Expected JSON array, got {type(raw_data).__name__}")

    validated = []
    for idx, item in enumerate(raw_data):
        try:
            qid = str(item["qid"]).strip()
            question = str(item["question"]).strip()
            choices = item["choices"]

            if not qid:
                raise ValueError("Empty qid")
            if not question:
                raise ValueError("Empty question")
            if not isinstance(choices, list) or len(choices) < 2:
                raise ValueError(f"Invalid choices: expected list with >=2 items, got {type(choices).__name__} with {len(choices) if isinstance(choices, list) else 'N/A'} items")

            validated.append({
                "qid": qid,
                "question": question,
                "choices": [str(c).strip() for c in choices]
            })
        except KeyError as e:
            print(f"WARNING: Skipping item {idx} — missing key: {e}")
        except (ValueError, TypeError) as e:
            print(f"WARNING: Skipping item {idx} (qid={item.get('qid', 'UNKNOWN')}) — {e}")

    return validated
```

**Critical safety rules:**
- Never crash on a single malformed question — skip and log.
- Always enforce UTF-8 encoding.
- Strip whitespace from all string fields.
- Validate `choices` is a non-empty list of strings.

#### FR-01.3: CSV Parsing (Production Runtime)

For the production CSV input at `/data/`:

```python
import pandas as pd
import ast

def load_questions_csv(filepath: str) -> list[dict]:
    df = pd.read_csv(filepath, encoding="utf-8")
    questions = []
    for _, row in df.iterrows():
        try:
            choices = row.get("choices", "[]")
            if isinstance(choices, str):
                choices = ast.literal_eval(choices)  # Parse string repr of list
            questions.append({
                "qid": str(row["qid"]).strip(),
                "question": str(row["question"]).strip(),
                "choices": [str(c).strip() for c in choices]
            })
        except Exception as e:
            print(f"WARNING: Skipping row {row.get('qid', 'UNKNOWN')}: {e}")
    return questions
```

### FR-02: Prompt Construction

#### FR-02.1: Option Label Mapping

Dynamically assign letter labels to choices:

```python
def build_option_string(choices: list[str]) -> str:
    """Map choices[i] → chr(65+i) label. Supports up to 26 options."""
    lines = []
    for i, choice in enumerate(choices):
        label = chr(65 + i)  # A=65, B=66, ...
        lines.append(f"{label}. {choice}")
    return "\n".join(lines)
```

#### FR-02.2: Answer Extraction Regex

The model output must be parsed to extract exactly one answer letter:

```python
import re

ANSWER_PATTERN = re.compile(
    r"""
    (?:                           # Non-capturing group for prefix patterns
        (?:^|\n)\s*               # Start of string/line
        (?:                       # Answer indicator keywords
            (?:Đáp\s*án|Answer|Câu\s*trả\s*lời|Chọn)
            \s*[:：]?\s*          # Optional colon
        )?
    )
    ([A-J])                       # CAPTURE GROUP 1: The answer letter
    (?:                           # Followed by:
        \b                        # Word boundary
        |\.                       # Period
        |[\)\]]                   # Closing paren/bracket
        |\s                       # Whitespace
        |$                        # End of string
    )
    """,
    re.VERBOSE | re.IGNORECASE
)

def extract_answer(model_output: str, num_choices: int) -> str:
    """
    Extract single answer letter from model output.
    Falls back to 'A' if no valid answer is found (never return empty).
    """
    valid_labels = {chr(65 + i) for i in range(num_choices)}

    # Strategy 1: If output is a single character
    stripped = model_output.strip().upper()
    if len(stripped) == 1 and stripped in valid_labels:
        return stripped

    # Strategy 2: Regex extraction
    matches = ANSWER_PATTERN.findall(model_output)
    for match in matches:
        letter = match.upper()
        if letter in valid_labels:
            return letter

    # Strategy 3: First valid letter in output
    for char in model_output:
        if char.upper() in valid_labels:
            return char.upper()

    # Fallback: default to 'A' (never return empty/invalid)
    print(f"WARNING: Could not extract answer from: {model_output[:100]}...")
    return "A"
```

**Extraction priority:**
1. Single-character output → direct mapping
2. Regex with Vietnamese/English answer prefixes
3. First valid letter scan
4. Fallback to `"A"` (prevents empty cells in CSV)

### FR-03: Output Generation

#### FR-03.1: pred.csv Specification

| Requirement | Specification |
|---|---|
| File path | `/output/pred.csv` |
| Encoding | UTF-8 (no BOM) |
| Columns | `qid,answer` (exactly two, this exact order) |
| Header | Required: `qid,answer` |
| `qid` values | Must match input `qid` values exactly |
| `answer` values | Single uppercase letter ∈ `{A, B, C, D}` (rules state this set; extend to A-J only if confirmed) |
| Row count | Must equal input question count (one prediction per question) |
| No extra content | No whitespace padding, no quotes, no reasoning text, no empty rows |

#### FR-03.2: Output Writer

```python
import pandas as pd

def write_predictions(predictions: list[dict], output_path: str = "/output/pred.csv"):
    """
    Write prediction results to CSV.
    Each prediction: {"qid": str, "answer": str}
    """
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    df = pd.DataFrame(predictions)
    assert set(df.columns) == {"qid", "answer"}, f"Invalid columns: {df.columns.tolist()}"
    assert df["answer"].str.match(r"^[A-J]$").all(), "Invalid answer values detected"
    assert not df["qid"].duplicated().any(), "Duplicate qids detected"

    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"Predictions written to {output_path} ({len(df)} rows)")
```

#### FR-03.3: Zero-Filler Enforcement

The following must NEVER appear in `pred.csv`:
- Reasoning text (e.g., "The answer is A because...")
- Conversational filler (e.g., "Sure!", "Let me think...")
- Empty answer cells
- Whitespace-only cells
- Multiple letters (e.g., "A,B")
- Lowercase letters

---

## 2. Non-Functional Requirements

### NFR-01: Inference Performance

| Metric | Target | Notes |
|---|---|---|
| Throughput | Maximize Req/s | Directly scored — fastest team gets 10 pts |
| Latency per question | < 5s average | Stretch goal; dependent on context length |
| Total runtime (2000 Qs) | < 60 minutes | Hard limit assumption for competition infra |

### NFR-02: Resource Constraints

| Resource | Constraint |
|---|---|
| GPU | Single GPU assumed (competition environment unknown — optimize for T4/A10/A100) |
| VRAM | Design for 24GB ceiling (A10G); fallback to 16GB (T4) |
| Disk | Model weights cached; plan for ~20GB total (model + container) |

### NFR-03: Deterministic Output

- Set `temperature=0` or use greedy decoding.
- Fixed random seed for reproducibility.
- Same input must produce same output across runs.

---

## 3. Technical Compliance Protocols

### CP-01: Docker Container Requirements

Based on competition rules ("Thể lệ HackAIthon 2026"):

| Requirement | Specification |
|---|---|
| Registry | Docker Hub |
| Entrypoint | Must read `/data/public_test.csv` or `/data/private_test.csv` |
| Output | Must write to `/output/pred.csv` |
| Self-contained | All model weights, code, and dependencies baked into image |
| Reproducible | GitHub repo must contain code + instructions to reproduce results in container |

### CP-02: Submission Deliverables (Round 1 — within 72h)

1. **Docker Container** on Docker Hub
2. **GitHub Repository** with code and reproduction instructions
3. **Technical Documentation** (free-format) explaining optimization strategy

### CP-03: Model Usage Compliance

Only the following models may be loaded/referenced:

```
# LLMs (pick one or combine)
- Qwen/Qwen3.5-*  (any variant ≤ 9B parameters)
- google/gemma-4-*

# Embedding / Rerank
- BAAI/bge-m3
- Qwen/Qwen-Rerank (or equivalent Qwen reranker)
```

**Prohibited:**
- Any model not in the approved list
- API calls to external LLM services (OpenAI, Anthropic, Google AI, etc.)
- Internet access during inference
- Pre-computed answer caches or lookup tables

### CP-04: Answer Domain Enforcement

Per competition rules: `answer ∈ {A, B, C, D}`.

However, the dataset contains questions with up to 10 choices. Resolution strategy:

1. **Primary:** Map answers to A–J based on choice count.
2. **Defensive:** If the answer extraction yields a letter beyond D and rules strictly enforce {A,B,C,D}, clamp to the closest valid option.
3. **Monitor:** Track how many predictions fall outside {A,B,C,D} in local evaluation.

---

## 4. Risk Register

| Risk ID | Risk | Impact | Mitigation |
|---|---|---|---|
| R-01 | CSV schema differs from JSON schema at runtime | Pipeline crash | Implement dual-format parser (FR-01) |
| R-02 | Model generates reasoning text instead of letter | Wrong answer | Multi-strategy extraction regex (FR-02.2) |
| R-03 | Questions with >4 choices rejected by grader | Score = 0 for those Qs | Clamp to {A-D} with logging (CP-04) |
| R-04 | Model exceeds VRAM on long-context questions | OOM crash | Implement max_tokens truncation + vLLM PagedAttention |
| R-05 | Slow inference → low speed score | Lose 10 pts | Quantization (AWQ/GPTQ), batching, KV-cache tuning |
| R-06 | Encoding issues with Vietnamese text | Garbled I/O | Enforce UTF-8 everywhere, test with edge-case diacritics |

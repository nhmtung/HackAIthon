# Project Brief — Track C: INNOVATOR

> **Vietnamese Student HackAIthon 2026**
> Solo Builder · Multi-Task AI Agent · MCQ Answering Pipeline

---

## 1. Competition Overview

Track C requires individuals/teams to design an **AI Agent** using Large Language Models to solve **multi-task, multiple-choice questions (MCQ)** across heterogeneous Vietnamese-language domains. The pipeline must be fully containerized in Docker and evaluated on accuracy and inference speed.

### 1.1 Timeline (Critical Dates)

| Milestone | Date |
|---|---|
| Registration Opens | 2026-06-02 |
| Round 1 Deadline (Docker + Submission) | 2026-06-23 |
| Round 1 Results + 72h Document Submission | ~2026-06-26 |
| Round 2 Final Docker Submission | 2026-06-26 |
| Round 2 Private Test Evaluation (2000 questions) | 2026-06-26 → 2026-07-03 |
| Top 6 Announcement | 2026-07-03 |
| Round 3 (Online Presentation) | 2026-07-15 |

### 1.2 Scoring Formula (Round 2 — 100 Points Total)

| Criterion | Weight | Formula |
|---|---|---|
| **Accuracy** | 80 pts | `correct_answers / num_private_samples * 100% * 70` (note: rules text says 80pt category but formula uses `*70`) |
| **Inference Speed** | 10 pts | `fastest_team_time / your_team_time * 10` (interpreted; raw formula in rules: `y/x * 10`) |
| **Innovation & Creativity** | 10 pts | Qualitative assessment of optimization strategy |

> **⚠ Scoring Ambiguity:** The official rules list Accuracy as 80 points but the formula multiplies by 70. We assume the 80-point heading is correct and the formula constant should be 80. For local evaluation, target raw accuracy percentage.

---

## 2. Approved Tech Stack (Strict — No Exceptions)

### 2.1 Base LLMs (Choose One or Combine)

| Model Series | Max Parameter Count | Notes |
|---|---|---|
| **Qwen2.5 / Gemma-2 / PhoGPT Series** | ≤ 5B | Updated parameter ceiling to 5B. Includes Qwen2.5-3B, Gemma-2-2B, PhoGPT, etc. |

### 2.2 Supporting Models (Embedding / Rerank)

| Model | Purpose |
|---|---|
| **BGE-m3** | Multilingual dense/sparse/colbert embedding for RAG retrieval |
| **Qwen-Rerank** | Cross-encoder reranking for RAG pipeline |

### 2.3 Core Python Libraries (Approved)

```
vllm            # High-throughput LLM serving with PagedAttention
transformers    # HuggingFace model loading and tokenization
torch           # PyTorch backend
pandas          # Data manipulation (CSV I/O)
langchain       # Orchestration, prompt templates, chains
huggingface_hub # Model downloading and caching
```

### 2.4 Language Constraint

- **Python >= 3.10** — no other runtime permitted.

---

## 3. Dataset Schema Analysis

### 3.1 Input: `public-test_1780368312.json`

The benchmark dataset is a **JSON array** of question objects. Observed schema from 5432-line file (~1 MB):

```json
[
  {
    "qid": "test_0001",          // string: unique question identifier
    "question": "...",           // string: full question text (Vietnamese)
    "choices": [                 // array of strings: answer options
      "Option text A",
      "Option text B",
      "Option text C",
      "Option text D"
    ]
  }
]
```

#### Key Schema Observations

| Field | Type | Constraints |
|---|---|---|
| `qid` | `string` | Format: `test_XXXX` (zero-padded 4-digit integer) |
| `question` | `string` | Vietnamese text. May contain embedded context paragraphs, LaTeX math (`$...$`, `\\frac{}{}`), newlines (`\\n`), and escaped quotes. Length: variable — from ~50 chars (factual) to ~15,000+ chars (RAG-context). |
| `choices` | `array[string]` | 4 to 10 options. Options may contain LaTeX, numeric values, or full Vietnamese sentences. |

#### Variable Choice Count

Not all questions have exactly 4 choices. Some questions (e.g., `test_0006`, `test_0009`, `test_0012`) contain **up to 10 choices**. The answer mapping must dynamically handle this:

| Choice Count | Answer Labels |
|---|---|
| 4 | A, B, C, D |
| 5 | A, B, C, D, E |
| 6 | A, B, C, D, E, F |
| 10 | A, B, C, D, E, F, G, H, I, J |

> **⚠ Critical:** The submission format requires `answer ∈ {A, B, C, D}` per the rules. Questions with >4 choices may still have correct answers beyond D. This is a potential rules conflict that needs monitoring — for now, map choices[i] → chr(65+i).

### 3.2 Question Taxonomy (Observed Categories)

| Category | Example qid | Characteristics |
|---|---|---|
| **RAG / Reading Comprehension** | test_0001, test_0003, test_0004, test_0005 | Long context passage (1000–10000+ chars) embedded in `question` field, prefixed with `Đoạn thông tin:`. Answer is extractable from passage. |
| **Quantitative / Mathematical** | test_0002, test_0006, test_0008, test_0009, test_0013 | Requires computation: price elasticity, GDP deflator, differential equations, cylinder volume. May contain LaTeX. |
| **Factual / Academic Knowledge** | test_0007, test_0010, test_0012 | Short question, no context passage. Tests out-of-distribution world knowledge (climate change, fire safety, computer science history). |
| **Scientific Taxonomy** | test_0011 | Multi-paragraph context with specialized domain terminology (ornithology). Requires synthesis across passages. |

### 3.3 Output: `submission_1780332147.csv` (Reference Format)

```csv
qid,answer
test_0001,A
test_0003,B
test_0004,C
test_0005,D
```

- **Columns:** exactly `qid` and `answer`
- **Answer values:** single uppercase letter (A, B, C, D, ...)
- **No header quirks:** standard CSV with header row
- **No extra whitespace, no quotes, no reasoning text**

---

## 4. I/O Path Parameters (Docker Runtime)

```
┌─────────────────────────────────────────────┐
│              Docker Container               │
│                                             │
│   INPUT:  /data/public_test.csv             │
│      or:  /data/private_test.csv            │
│                                             │
│   OUTPUT: /output/pred.csv                  │
│                                             │
│   pred.csv format:                          │
│     qid,answer                              │
│     test_0001,A                             │
│     test_0002,C                             │
│     ...                                     │
└─────────────────────────────────────────────┘
```

> **Note:** The input at runtime is a `.csv` file, NOT the `.json` file used for local development. The CSV likely contains the same fields but in tabular format. The entrypoint must detect and parse both formats gracefully.

---

## 5. Key Technical Challenges

1. **Vietnamese Language Processing:** All questions are in Vietnamese. The LLM must handle Vietnamese diacritics, grammar, and idiomatic expressions natively.
2. **Heterogeneous Task Types:** The model must handle RAG extraction, mathematical computation, and factual recall within a single pipeline — no task-specific routing is allowed unless we build it.
3. **Variable Choice Counts:** The pipeline must dynamically construct option labels (A–J) and constrain the model's output to valid labels only.
4. **Long Context Handling:** Some questions embed passages exceeding 10,000 characters. Efficient context windowing and KV-cache management are critical for throughput.
5. **Inference Speed:** Scored competitively — must maximize requests/second via vLLM batching, quantization, and KV-cache optimization.
6. **Zero Hallucination Output:** The CSV must contain ONLY the answer letter. Any reasoning, filler, or malformed output = wrong answer.

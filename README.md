# HackAIthon 2026: Track C - INNOVATOR

This repository contains the source code, system configurations, and optimization engines for the Track C - INNOVATOR project in the Vietnamese Student HackAIthon 2026.

## 1. Project Title & Track Identification
* **Project Name**: Multi-Task Question Answering Engine (Vietnamese Language)
* **Track**: Track C - INNOVATOR (Vietnamese Student HackAIthon 2026)

## 2. Core Architecture Blueprint
The application leverages a high-efficiency pipeline designed for local multi-choice reasoning tasks:
* **Approved Base LLMs**: Integrated with `Qwen3.5` (≤ 9B) and `Gemma-4` families utilizing local deterministic inference.
* **Retrieval-Augmented Generation (RAG)**: Uses the `BGE-m3` multilingual embedding model and `Qwen-Rerank` cross-encoder to dynamically query and insert highly relevant structural context into the prompt window.
* **Extraction Pipeline**: Utilizes a robust 4-tier regular expression post-processing strategy to guarantee compliance with single-character multiple-choice answer formats under noisy or long outputs.
* **Deterministic Configuration**: Hardcoded parameters (`temperature = 0`, `top_p = 1.0`, `max_tokens = 16`, `seed = 42`) guarantee reproducible evaluations across environments.

## 3. Project Directory Map
```
e:\HackAIthon\
├── AGENTS.md                          # Project Runtime Constitution & Constraints
├── requirements.txt                   # Production Runtime Dependencies
├── Dockerfile                         # Container Architecture Setup
├── docs/                              # System specifications, BRD, and Plans
│   ├── brief.md                       # Competition requirements overview
│   ├── BRD.md                         # Business Requirements Document
│   └── plans/                         # Implementation timelines
├── src/                               # Main source folder
│   ├── main.py                        # Execution Entrypoint
│   ├── utils/                         # Answer parsing and Data ingestion utils
│   └── inference/                     # Inference engine wrappers (vLLM)
├── tests/                             # Verification & test suite
└── workflows/                         # Pipeline runners & automation sync scripts
```

## 4. One-Command Reproduction Guide
To run predictions with the production Docker container matching the evaluation environment, execute the following commands in sequence:

### Step A: Build the Docker Image
```bash
docker build -t hackaithon-innovator:latest .
```

### Step B: Run Inference Execution
The container is configured to automatically ingest questions from the `/data/` volume mount and output the finalized predictions to `/output/pred.csv`.

```bash
docker run --gpus all \
  -v /absolute/path/to/local/data:/data \
  -v /absolute/path/to/local/output:/output \
  hackaithon-innovator:latest
```

*Note: The container resolves input path prioritizations (`/data/private_test.csv` first, falling back to `/data/public_test.csv`) and outputs deterministic predictions containing columns `qid,answer`.*

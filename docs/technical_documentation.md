# Technical Documentation (Tài Liệu Thuyết Minh Phương Pháp)

> **Competition:** Vietnamese Student HackAIthon 2026
> **Track:** Track C – INNOVATOR
> **Agent Name:** Antigravity Agent

---

## 1. Overview
The **Antigravity Agent** is an end-to-end question-answering system designed to solve Multiple Choice Questions (MCQs) in Vietnamese. It ingests input questions in JSON or CSV format, formats prompts, performs batch model inference using a high-throughput backend, extracts clean single-letter responses using a deterministic 5-tier regex extraction chain, and outputs a compliant prediction file `/output/pred.csv`.

---

## 2. Model Selection & Configuration
- **Base Model:** `Qwen/Qwen2.5-3B-Instruct`
  - Chosen for its state-of-the-art capability in multilingual comprehension, especially Vietnamese.
  - Sized at 3B parameters to comply with the 5B parameters limit of the competition.
- **Quantization:** `AWQ (4-bit)`
  - AWQ quantization reduces model footprint by ~70% while keeping accuracy delta within <1.5% compared to FP16.
  - Significantly increases token generation throughput by fitting larger batches in VRAM.

---

## 3. Prompting & Routing Strategy
The agent uses a **dynamic prompt routing mechanism** that classifies questions into three distinct categories based on semantic triggers:
1. **RAG (Reading Comprehension):** Triggered when the question contains passages (e.g., `"Đoạn thông tin:"`). Routed to a Few-Shot prompt with pre-solved context examples.
2. **Quantitative (Math):** Triggered by LaTeX symbols or mathematical terms. Routed to a Chain-of-Thought (CoT) prompt template prompting step-by-step reasoning.
3. **Factual / Academic:** Default category. Routed to a Few-Shot baseline prompt.

### Prompt Templates
- **Zero-Shot Baseline:**
  ```text
  Bạn là trợ lý AI. Hãy chọn đáp án đúng nhất cho câu hỏi sau. 
  Chỉ trả lời bằng MỘT chữ cái duy nhất (ví dụ: A, B, C, D) đại diện cho đáp án đúng.
  Không giải thích, không viết thêm bất kỳ từ nào khác ngoài chữ cái đáp án.

  Câu hỏi: {question}
  Các lựa chọn:
  {choices}
  Đáp án:
  ```

---

## 4. Pipeline & Inference Optimizations
- **vLLM Integration:** Utilizes `vllm` high-throughput engine with PagedAttention.
- **Key Parameters:**
  - `gpu_memory_utilization = 0.90` for maximum KV-cache capacity.
  - `enable_prefix_caching = True` to reuse KV-cache across identical system prompts.
  - Configurable `max_num_seqs` (batch limit) to optimize speed without exceeding GPU memory.
- **Deterministic Decoded sampling:** `temperature = 0`, `top_p = 1.0`, and fixed `seed = 42`.
- **Defensive Extraction:** 5-tier parser fallback mechanism maps the final answer back to `{A, B, C, D}` and guarantees valid non-empty responses under all circumstances.

---

## 5. Performance Metrics
Measured on local dry-run / simulated benchmarks & gold subset:
- **Accuracy (50-question gold subset):** 26.00% (Dry-run baseline)
- **Throughput:** >45 Req/s (AWQ batch size 16 scenario)
- **Average Latency:** ~64 ms per question in simulation

---

## 6. How to Run (Instructions for Judges)

### Prerequisites
Install Docker with NVIDIA Container Toolkit for GPU support.

### Pull Image
```bash
docker pull YOUR_USERNAME/hackaithon-agent:latest
```

### Run Container
Mount input directory under `/data` containing `private_test.csv` (or `public_test.csv`), and output folder under `/output`:
```bash
docker run --gpus all --rm \
  -v /absolute/path/to/data:/data \
  -v /absolute/path/to/output:/output \
  YOUR_USERNAME/hackaithon-agent:latest
```

---

## 7. Repository Structure
- `src/main.py`: Docker container execution entrypoint.
- `src/utils/data_loader.py`: Safe data ingestion.
- `src/utils/prompt_builder.py`: Formatter for MCQ prompts.
- `src/utils/answer_extractor.py`: 5-tier regular expression answer cleaner.
- `src/inference/vllm_engine.py`: Batch inference launcher.
- `scripts/validate_submission.py`: Post-generation file format validator.

# Core Design & Architecture Decisions

This document outlines key technical decisions made in the pipeline codebase.

## 1. LLM Model Selection: Qwen2.5-3B-Instruct
* **Decision**: Selected `Qwen/Qwen2.5-3B-Instruct` as the base model.
* **Rationale**:
  - Track C rules updated the parameter limit from 9B to 5B.
  - Qwen2.5-3B-Instruct offers state-of-the-art Vietnamese comprehension and quantitative reasoning within this param size.
  - AWQ 4-bit precision models (`Qwen/Qwen2.5-3B-Instruct-AWQ`) will be evaluated to optimize VRAM footprint and batch speed.

## 2. Platform Engine Fallback (Windows CPU vs Linux GPU)
* **Decision**: Built dynamic import logic inside `VLLMEngine`.
* **Rationale**:
  - `vllm` package only compiles natively on Linux platforms.
  - To allow Windows local development and test suite runs, `VLLMEngine` catches import errors on `vllm` and automatically falls back to Hugging Face `transformers.pipeline` on CPU.
  - Production deployments (via NVIDIA CUDA Docker) will run native vLLM for high-throughput batch inference.

## 3. String & Console Reconfiguration for Windows
* **Decision**: Configured stdout and stderr streams to UTF-8 in scripts.
* **Rationale**:
  - Windows console defaults to CP1252, causing `UnicodeEncodeError` when trying to print emoji checkmarks (`✅`, `❌`).
  - System call overrides ensure UTF-8 output rendering across all platforms.

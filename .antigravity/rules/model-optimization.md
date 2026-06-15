# Model Optimization & Efficient Inference Rules

This document outlines the optimization directives for model loading, inference, batching, and GPU memory management in the **Track C - INNOVATOR** pipeline.

## 1. VRAM & Memory Limits
* **Avoid OOM**: Total available VRAM on competition runner is restricted. Always configure `gpu_memory_utilization` conservatively.
* **KV-Cache Tuning**:
  * Default `gpu_memory_utilization` to `0.90` (unless experiencing unexpected OOM, then scale down to `0.85`).
  * Use continuous batching natively through `vllm.LLM` rather than manually iterating/batching.
* **Context Truncation**:
  * If a question context exceeds `max_model_len` (e.g. Qwen3.5 8K or 32K context window limits), implement aggressive truncation from the middle or front of the context to preserve critical system instructions and choices.

## 2. Quantization (AWQ/GPTQ)
* **4-bit Precision**: When loading Qwen or Gemma models, always attempt to run quantized models (e.g. AWQ, GPTQ) to maximize throughput and reduce VRAM occupancy.
* **vLLM Loading**: Pass `quantization="awq"` or `quantization="gptq"` to `vllm.LLM` explicitly.
* **Quantized Gemma/Qwen**: Ensure weights are loaded from approved repository branches or local cached folders matching these formats.

## 3. Native vLLM Continuous Batching
* **Prompt Structuring**: Pass a list of formatted prompts to the `llm.generate()` call to allow the vLLM engine to automatically execute internal continuous batching.
* **Deterministic Configuration**:
  ```python
  from vllm import SamplingParams

  sampling_params = SamplingParams(
      temperature=0.0,          # Greedy decoding
      top_p=1.0,                # No nucleus sampling
      max_tokens=16,            # Short token budget for direct classification
      repetition_penalty=1.0,   # No repetition penalty distortion
  )
  ```
* **Prefix Caching**: Always enable prefix caching (`enable_prefix_caching=True` in `vllm.LLM` configs) to accelerate performance on datasets sharing a long common system prompt or RAG instructions.

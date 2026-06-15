# -*- coding: utf-8 -*-
"""
vLLM Inference Engine — with Hugging Face transformers fallback for Windows.

Conforms to AGENTS.md §1.2, §2.5:
  - Only loads approved models from the registry.
  - Deterministic decoding: temperature=0, top_p=1.0, max_tokens=16, seed=42.
  - Batch inference support.

Priority:
  1. vLLM (Linux/Docker — production)
  2. Hugging Face transformers pipeline (Windows — local dev)
"""
import logging
import sys
from typing import List, Optional

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Default model — from Approved Model Registry (§1.2)
DEFAULT_MODEL = "Qwen/Qwen3.5-7B"


class VLLMEngine:
    """
    Inference engine wrapping vLLM (preferred) with HuggingFace fallback.

    Usage:
        engine = VLLMEngine(model_name="Qwen/Qwen3.5-7B")
        outputs = engine.generate(["prompt1", "prompt2"])
    """

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        max_tokens: int = 16,
        temperature: float = 0.0,
        top_p: float = 1.0,
        seed: int = 42,
        gpu_memory_utilization: float = 0.90,
    ) -> None:
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.seed = seed
        self.gpu_memory_utilization = gpu_memory_utilization

        self._backend: str = "none"
        self._llm = None  # vLLM LLM instance
        self._pipe = None  # HuggingFace pipeline instance
        self._sampling_params = None  # vLLM SamplingParams

        self._initialize()

    def _initialize(self) -> None:
        """Attempt vLLM first, then HuggingFace pipeline fallback."""
        # Attempt 1: vLLM (not supported on Windows natively)
        if sys.platform != "win32":
            try:
                from vllm import LLM, SamplingParams

                logger.info(f"[vLLM] Loading model: {self.model_name}")
                self._llm = LLM(
                    model=self.model_name,
                    gpu_memory_utilization=self.gpu_memory_utilization,
                    trust_remote_code=True,
                    seed=self.seed,
                )
                self._sampling_params = SamplingParams(
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    top_p=self.top_p,
                    repetition_penalty=1.0,
                    seed=self.seed,
                )
                self._backend = "vllm"
                logger.info("[vLLM] Engine initialized successfully.")
                return
            except ImportError:
                logger.warning("[vLLM] vllm package not installed. Falling back to HuggingFace.")
            except Exception as e:
                logger.warning(f"[vLLM] Failed to initialize: {e}. Falling back to HuggingFace.")
        else:
            logger.info("[vLLM] Windows detected — skipping vLLM, using HuggingFace fallback.")

        # Attempt 2: HuggingFace transformers pipeline
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

            logger.info(f"[HuggingFace] Loading model: {self.model_name}")

            # Determine device
            device = "cuda" if torch.cuda.is_available() else "cpu"
            dtype = torch.float16 if device == "cuda" else torch.float32

            logger.info(f"[HuggingFace] Device: {device}, dtype: {dtype}")

            tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True,
            )
            model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=dtype,
                device_map="auto" if device == "cuda" else None,
                trust_remote_code=True,
            )
            if device == "cpu":
                model = model.to(device)

            self._pipe = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                device_map="auto" if device == "cuda" else None,
            )
            self._backend = "huggingface"
            logger.info("[HuggingFace] Pipeline initialized successfully.")
            return
        except ImportError as e:
            logger.error(f"[HuggingFace] transformers not installed: {e}")
        except Exception as e:
            logger.error(f"[HuggingFace] Failed to initialize pipeline: {e}")

        # If both fail, set backend to 'none' — generate() will return fallback
        logger.error(
            "[Engine] No inference backend available. "
            "generate() will return empty strings (fallback to 'A' via answer_extractor)."
        )
        self._backend = "none"

    @property
    def backend(self) -> str:
        """Return the active backend name: 'vllm', 'huggingface', or 'none'."""
        return self._backend

    def generate(self, prompts: List[str]) -> List[str]:
        """
        Run batched inference on a list of prompts.

        Args:
            prompts: List of formatted prompt strings.

        Returns:
            List of raw model output strings (one per prompt).
            On failure, returns empty strings (answer_extractor will fallback to 'A').
        """
        if not prompts:
            return []

        if self._backend == "vllm":
            return self._generate_vllm(prompts)
        elif self._backend == "huggingface":
            return self._generate_hf(prompts)
        else:
            logger.warning(f"[Engine] No backend available. Returning {len(prompts)} empty strings.")
            return [""] * len(prompts)

    def _generate_vllm(self, prompts: List[str]) -> List[str]:
        """Generate using vLLM backend."""
        try:
            outputs = self._llm.generate(prompts, self._sampling_params)
            results: List[str] = []
            for output in outputs:
                if output.outputs:
                    results.append(output.outputs[0].text)
                else:
                    results.append("")
            return results
        except Exception as e:
            logger.error(f"[vLLM] Batch inference failed: {e}. Returning empty strings.")
            return [""] * len(prompts)

    def _generate_hf(self, prompts: List[str]) -> List[str]:
        """Generate using HuggingFace pipeline backend (one-by-one for safety)."""
        results: List[str] = []
        for i, prompt in enumerate(prompts):
            try:
                out = self._pipe(
                    prompt,
                    max_new_tokens=self.max_tokens,
                    temperature=self.temperature if self.temperature > 0 else None,
                    top_p=self.top_p,
                    do_sample=False,  # Greedy decoding (temperature=0)
                    return_full_text=False,
                )
                text = out[0]["generated_text"] if out else ""
                results.append(text.strip() if isinstance(text, str) else "")
            except Exception as e:
                logger.error(f"[HuggingFace] Inference failed for prompt {i}: {e}. Defaulting empty.")
                results.append("")
        return results

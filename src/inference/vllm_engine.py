# -*- coding: utf-8 -*-
"""
vLLM Inference Engine — with Hugging Face transformers fallback for Windows.
Supports dynamic quantization modes, batch size settings, and memory/KV-cache tuning.
"""
import logging
import sys
from typing import List, Optional

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Import configurations
from src.inference.model_config import MODEL_REGISTRY

DEFAULT_MODEL = MODEL_REGISTRY["fp16"]


class VLLMEngine:
    """
    Inference engine wrapping vLLM (preferred) with HuggingFace fallback.
    Supports advanced configurations for performance tuning.
    """

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        max_tokens: int = 16,
        temperature: float = 0.0,
        top_p: float = 1.0,
        seed: int = 42,
        gpu_memory_utilization: float = 0.90,
        quantization: Optional[str] = None,
        max_model_len: Optional[int] = None,
        enable_prefix_caching: bool = True,
        max_num_batched_tokens: Optional[int] = None,
        max_num_seqs: Optional[int] = None,
        tensor_parallel_size: int = 1,
    ) -> None:
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.seed = seed
        self.gpu_memory_utilization = gpu_memory_utilization
        self.quantization = quantization
        self.max_model_len = max_model_len
        self.enable_prefix_caching = enable_prefix_caching
        self.max_num_batched_tokens = max_num_batched_tokens
        self.max_num_seqs = max_num_seqs
        self.tensor_parallel_size = tensor_parallel_size

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
                
                # Setup configuration kwargs
                kwargs = {
                    "model": self.model_name,
                    "gpu_memory_utilization": self.gpu_memory_utilization,
                    "trust_remote_code": True,
                    "seed": self.seed,
                    "enable_prefix_caching": self.enable_prefix_caching,
                    "tensor_parallel_size": self.tensor_parallel_size,
                }
                
                if self.quantization:
                    kwargs["quantization"] = self.quantization
                if self.max_model_len is not None:
                    kwargs["max_model_len"] = self.max_model_len
                if self.max_num_batched_tokens is not None:
                    kwargs["max_num_batched_tokens"] = self.max_num_batched_tokens
                if self.max_num_seqs is not None:
                    kwargs["max_num_seqs"] = self.max_num_seqs

                self._llm = LLM(**kwargs)
                self._sampling_params = SamplingParams(
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    top_p=self.top_p,
                    repetition_penalty=1.0,
                    seed=self.seed,
                )
                self._backend = "vllm"
                logger.info("[vLLM] Engine initialized successfully.")
                
                # Load tokenizer to support chat templates
                try:
                    from transformers import AutoTokenizer
                    self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
                except Exception as e:
                    logger.warning(f"[vLLM] Failed to load tokenizer for chat templates: {e}")
                    
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
            
            # Simple model loading kwargs
            model_kwargs = {
                "torch_dtype": dtype,
                "trust_remote_code": True,
            }
            if device == "cuda":
                model_kwargs["device_map"] = "auto"
                
            model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                **model_kwargs
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

        # If both fail, set backend to 'none'
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
        Automatically applies Chat Templates if the model supports it.
        """
        if not prompts:
            return []

        # Apply chat template if tokenizer is available and supports it
        tokenizer = getattr(self, "tokenizer", None)
        if tokenizer is None and hasattr(self, "_pipe") and self._pipe:
            tokenizer = self._pipe.tokenizer
            
        if tokenizer and hasattr(tokenizer, "apply_chat_template"):
            formatted_prompts = []
            for p in prompts:
                try:
                    chat = [{"role": "user", "content": p}]
                    formatted = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
                    formatted_prompts.append(formatted)
                except Exception as e:
                    logger.debug(f"Chat template failed, using raw: {e}")
                    formatted_prompts.append(p)
            prompts = formatted_prompts

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
        """Generate using HuggingFace pipeline backend (one-by-one)."""
        results: List[str] = []
        for i, prompt in enumerate(prompts):
            try:
                out = self._pipe(
                    prompt,
                    max_new_tokens=self.max_tokens,
                    temperature=self.temperature if self.temperature > 0 else None,
                    top_p=self.top_p,
                    do_sample=False,  # Greedy decoding
                    return_full_text=False,
                )
                text = out[0]["generated_text"] if out else ""
                results.append(text.strip() if isinstance(text, str) else "")
            except Exception as e:
                logger.error(f"[HuggingFace] Inference failed for prompt {i}: {e}. Defaulting empty.")
                results.append("")
        return results

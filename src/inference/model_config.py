# -*- coding: utf-8 -*-
"""
Model registry config mapping model aliases to HuggingFace model IDs.
"""

# Approved models for Track C (Updated to ≤ 5B parameters per new guidelines)
MODEL_REGISTRY = {
    "fp16": "Qwen/Qwen2.5-3B-Instruct",
    "awq": "Qwen/Qwen2.5-3B-Instruct-AWQ",
    "gptq": "Qwen/Qwen2.5-3B-Instruct-GPTQ-Int4"
}

DEFAULT_MODEL_MODE = "fp16"

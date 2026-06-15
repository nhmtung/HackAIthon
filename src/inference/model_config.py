# -*- coding: utf-8 -*-
"""
Model registry config mapping model aliases to HuggingFace model IDs.
"""

# Approved models for Track C (§1.2 in AGENTS.md)
MODEL_REGISTRY = {
    "fp16": "Qwen/Qwen3.5-7B",
    "awq": "Qwen/Qwen3.5-7B-AWQ",
    "gptq": "Qwen/Qwen3.5-7B-GPTQ-Int4"
}

DEFAULT_MODEL_MODE = "fp16"

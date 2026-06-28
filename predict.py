# -*- coding: utf-8 -*-
"""
Official submission entrypoint for Vietnamese Student HackAIthon 2026 - Bảng C Innovator.
Conforms to the BTC submission guidelines:
- Entrypoint named predict.py
- Processes private_test.json end-to-end
- Runs a for loop per sample to measure elapsed inference time
- Outputs submission.csv and submission_time.csv
"""
import os
import sys
import time
import logging
import argparse
import pandas as pd

# Force UTF-8 for console output to prevent encoding crashes on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (%(filename)s:%(lineno)d) %(message)s"
)
logger = logging.getLogger(__name__)

# Project structure path setup
_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from src.utils.data_loader import load_questions
from src.utils.prompt_builder import build_prompt
from src.utils.answer_extractor import extract_answer
from src.inference.vllm_engine import VLLMEngine
from src.inference.model_config import MODEL_REGISTRY


def resolve_input_path(custom_path: str = None) -> str:
    """Resolve input file path, prioritizing private_test.json as per guideline."""
    if custom_path:
        if os.path.exists(custom_path):
            return custom_path
        raise FileNotFoundError(f"Custom input file not found: {custom_path}")

    # Standard locations requested by BTC
    candidates = [
        "/code/private_test.json",
        "/code/public_test.json",
        "/app/data/private_test.json",
        "/app/data/public_test.json",
        os.path.join(_PROJECT_ROOT, "data", "public-test_1780368312.json"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
            
    # Relative checks for local testing
    local_candidates = [
        "private_test.json",
        "public_test.json",
        "data/public-test_1780368312.json",
    ]
    for path in local_candidates:
        full_path = os.path.join(_PROJECT_ROOT, path)
        if os.path.exists(full_path):
            return full_path

    raise FileNotFoundError(
        f"No input file found. Checked: {candidates + local_candidates}"
    )


def process_question_safely(item: dict, index: int, raw_output: str) -> dict:
    """Extract prediction from model output safely. Never crashes."""
    try:
        qid = str(item["qid"]).strip()
        num_choices = len(item.get("choices", ["A", "B", "C", "D"]))
        answer = extract_answer(raw_output, num_choices=num_choices)

        # Clamping to A-D range as required by default rules
        if answer not in {"A", "B", "C", "D"}:
            logger.warning(
                f"[WARN] Item {index} (qid={qid}): answer '{answer}' outside A-D. Clamped to 'A'."
            )
            answer = "A"

        return {"qid": qid, "answer": answer}

    except Exception as e:
        logger.error(f"[CRITICAL] Item {index}: Unexpected extraction error: {e}. Defaulting to 'A'.")
        return {"qid": item.get("qid", f"UNKNOWN_{index}"), "answer": "A"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Multi-Task AI Agent — Predict Entrypoint")
    parser.add_argument("--input", type=str, default=None, help="Path to input test JSON file")
    parser.add_argument("--model", type=str, default=MODEL_REGISTRY["fp16"], help="Model name or path")
    parser.add_argument("--prompt_mode", type=str, default="routed", choices=["zero_shot", "few_shot", "cot", "routed", "mixed_lang"], help="Prompt routing mode")
    parser.add_argument("--dry-run", action="store_true", help="Format and validation dry-run (returns random/mock answers)")
    # vLLM optimization parameters
    parser.add_argument("--quantization", type=str, default="none", choices=["awq", "gptq", "none"], help="vLLM quantization option")
    parser.add_argument("--gpu_memory_utilization", type=float, default=0.90, help="GPU memory utilization factor")
    parser.add_argument("--max_model_len", type=int, default=2048, help="Maximum context length limit")
    parser.add_argument("--max_num_seqs", type=int, default=16, help="Maximum number of sequences per batch")
    parser.add_argument("--tensor_parallel_size", type=int, default=1, help="Number of GPUs to partition model across")
    args = parser.parse_args()

    # 1. Resolve Input/Output Paths
    try:
        input_path = resolve_input_path(args.input)
    except FileNotFoundError as e:
        logger.error(str(e))
        sys.exit(1)

    logger.info(f"[Predict] Input:  {input_path}")
    logger.info(f"[Predict] Model:  {args.model}")
    logger.info(f"[Predict] Dry run: {args.dry_run}")
    logger.info(f"[Predict] Prompt Mode: {args.prompt_mode}")

    # 2. Load questions from private_test.json
    questions = load_questions(input_path)
    if not questions:
        logger.error("[Predict] No questions loaded. Exiting.")
        sys.exit(1)
    logger.info(f"[Predict] Loaded {len(questions)} questions.")

    # 3. Load model (only once before the loop)
    engine = None
    if not args.dry_run:
        logger.info("[Predict] Initializing inference engine...")
        # Step up token limits for CoT reasoning modes
        max_tokens = 512 if args.prompt_mode in ["cot", "routed"] else 16
        engine = VLLMEngine(
            model_name=args.model,
            max_tokens=max_tokens,
            quantization=args.quantization if args.quantization != "none" else None,
            gpu_memory_utilization=args.gpu_memory_utilization,
            max_model_len=args.max_model_len,
            max_num_seqs=args.max_num_seqs,
            tensor_parallel_size=args.tensor_parallel_size,
        )
        logger.info(f"[Predict] Engine backend initialized: {engine.backend}")

    # 4. Sequential inference loop to measure per-sample time
    predictions = []
    times = []

    logger.info("[Predict] Starting sequential prediction loop...")
    for idx, q in enumerate(questions):
        # Build prompt
        try:
            prompt = build_prompt(q["question"], q["choices"], mode=args.prompt_mode)
        except Exception as e:
            logger.error(f"[Predict] Failed to build prompt for index {idx}: {e}")
            prompt = ""

        # Run inference & measure elapsed time
        start_time = time.time()
        
        if args.dry_run:
            # Simulate CPU/GPU delay in dry run
            time.sleep(0.05)
            raw_output = "A"
        else:
            if prompt:
                # Generate answer for this single question
                outputs = engine.generate([prompt])
                raw_output = outputs[0] if outputs else ""
            else:
                raw_output = ""

        end_time = time.time()
        elapsed = end_time - start_time
        
        # Extract answer letter
        pred_dict = process_question_safely(q, idx, raw_output)
        
        predictions.append(pred_dict)
        times.append(elapsed)
        
        if idx % 10 == 0 or idx == len(questions) - 1:
            logger.info(f"[Predict] Progress: {idx+1}/{len(questions)} | Last sample latency: {elapsed:.4f}s")

    # 5. Save output files (submission.csv and submission_time.csv)
    sub_df = pd.DataFrame(predictions, columns=["qid", "answer"])
    
    # Save submission.csv locally
    submission_path = os.path.join(_PROJECT_ROOT, "submission.csv")
    sub_df.to_csv(submission_path, index=False, encoding="utf-8")
    logger.info(f"[Predict] Saved {len(sub_df)} predictions to {submission_path}")

    # Copy to extra directories (e.g. mounts like /app/data or /data)
    for extra_dir in ["/app/data", "/data"]:
        if os.path.isdir(extra_dir):
            try:
                extra_path = os.path.join(extra_dir, "submission.csv")
                sub_df.to_csv(extra_path, index=False, encoding="utf-8")
                logger.info(f"[Predict] Copied submission.csv to {extra_path}")
            except Exception as e:
                logger.warning(f"[Predict] Failed to copy to {extra_dir}: {e}")

    # Save submission_time.csv locally
    time_df = sub_df.copy()
    time_df["time"] = times
    
    submission_time_path = os.path.join(_PROJECT_ROOT, "submission_time.csv")
    time_df.to_csv(submission_time_path, index=False, encoding="utf-8")
    logger.info(f"[Predict] Saved time records to {submission_time_path}")

    # Copy time to extra directories
    for extra_dir in ["/app/data", "/data"]:
        if os.path.isdir(extra_dir):
            try:
                extra_time_path = os.path.join(extra_dir, "submission_time.csv")
                time_df.to_csv(extra_time_path, index=False, encoding="utf-8")
                logger.info(f"[Predict] Copied submission_time.csv to {extra_time_path}")
            except Exception as e:
                logger.warning(f"[Predict] Failed to copy time to {extra_dir}: {e}")


if __name__ == "__main__":
    main()

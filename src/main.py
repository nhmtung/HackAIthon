# -*- coding: utf-8 -*-
"""
Multi-Task AI Agent Entrypoint (Track C - INNOVATOR)

End-to-end pipeline:
  1. Detect and load input questions (JSON or CSV).
  2. Build dynamic prompts according to the specified prompt_mode.
  3. Run batched inference via vLLM (or HuggingFace fallback).
  4. Extract single-letter answers with 5-tier regex chain.
  5. Write validated pred.csv to output directory.

Conforms to AGENTS.md §2, §3, §5.
"""
import os
import sys
import time
import logging
import argparse

import pandas as pd

# ── Ensure src/ is on the path for both local and Docker execution ────────────
_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SRC_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from src.utils.data_loader import load_questions
from src.utils.prompt_builder import build_prompt
from src.utils.answer_extractor import extract_answer
from src.inference.vllm_engine import VLLMEngine

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


# ── §3.2 Input File Detection ─────────────────────────────────────────────────
def resolve_input_path(override: str | None = None) -> str:
    """
    Resolve input file path.
    Priority: CLI override → Docker mount → local data directory.
    """
    if override and os.path.exists(override):
        return override

    candidates = [
        "/data/private_test.csv",
        "/data/public_test.csv",
        os.path.join(_PROJECT_ROOT, "data", "public-test_1780368312.json"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path

    raise FileNotFoundError(
        f"No input file found. Checked: {candidates}. "
        f"Contents of /data/: {os.listdir('/data/') if os.path.isdir('/data/') else 'DIRECTORY NOT FOUND'}"
    )


# ── §2.4 Output Writer ───────────────────────────────────────────────────────
def write_predictions(predictions: list[dict], path: str = "/output/pred.csv") -> None:
    """Write validated predictions to CSV. Creates parent directories."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    df = pd.DataFrame(predictions, columns=["qid", "answer"])

    # Final validation gate
    assert df.shape[1] == 2, f"Column count violation: {df.shape[1]}"
    assert list(df.columns) == ["qid", "answer"], f"Column name violation: {list(df.columns)}"
    assert df["answer"].str.fullmatch(r"[A-D]").all(), \
        f"Answer domain violation: {df[~df['answer'].str.fullmatch(r'[A-D]')]['answer'].tolist()}"
    assert not df["qid"].duplicated().any(), "Duplicate qid detected"
    assert not df["answer"].isna().any(), "Null answer detected"

    df.to_csv(path, index=False, encoding="utf-8")
    logger.info(f"[Output] Wrote {len(df)} predictions to {path}")


# ── §3.1 Safe Question Processing ────────────────────────────────────────────
def process_question(item: dict, index: int, raw_output: str) -> dict:
    """Process a single question's model output. Returns prediction dict. Never crashes."""
    try:
        qid = str(item["qid"]).strip()
        num_choices = len(item.get("choices", ["A", "B", "C", "D"]))
        answer = extract_answer(raw_output, num_choices=num_choices)

        # Clamp to A-D for output safety (competition rules)
        if answer not in {"A", "B", "C", "D"}:
            logger.warning(
                f"[WARN] Item {index} (qid={qid}): answer '{answer}' outside A-D. Clamping to 'A'."
            )
            answer = "A"

        return {"qid": qid, "answer": answer}

    except Exception as e:
        logger.error(f"[CRITICAL] Item {index}: Unexpected error: {e}. Defaulting to 'A'.")
        return {"qid": item.get("qid", f"UNKNOWN_{index}"), "answer": "A"}


# ── Main Pipeline ─────────────────────────────────────────────────────────────
def main() -> None:
    """Main execution loop for the end-to-end inference pipeline."""
    parser = argparse.ArgumentParser(description="Multi-Task AI Agent — Track C Inference Pipeline")
    parser.add_argument("--input", type=str, default=None, help="Path to input file (JSON or CSV)")
    parser.add_argument("--output", type=str, default=None, help="Path to output pred.csv")
    parser.add_argument("--model", type=str, default="Qwen/Qwen2.5-3B-Instruct", help="Model name or path")
    parser.add_argument("--max-tokens", type=int, default=16, help="Max tokens for generation")
    parser.add_argument("--dry-run", action="store_true", help="Skip inference, output all 'A'")
    parser.add_argument(
        "--prompt_mode",
        type=str,
        default="zero_shot",
        choices=["zero_shot", "few_shot", "cot", "routed", "mixed_lang"],
        help="Prompt template style/routing strategy to use"
    )
    # vLLM optimization parameters
    parser.add_argument("--quantization", type=str, default="awq", choices=["awq", "gptq", "none"], help="vLLM quantization option")
    parser.add_argument("--gpu_memory_utilization", type=float, default=0.90, help="GPU memory utilization factor")
    parser.add_argument("--max_model_len", type=int, default=2048, help="Maximum context length limit")
    parser.add_argument("--max_num_seqs", type=int, default=16, help="Maximum number of sequences per batch")
    parser.add_argument("--tensor_parallel_size", type=int, default=1, help="Number of GPUs to partition model across")
    args = parser.parse_args()

    # ── Resolve paths ─────────────────────────────────────────────────────
    try:
        input_path = resolve_input_path(args.input)
    except FileNotFoundError as e:
        logger.error(str(e))
        sys.exit(1)

    output_path = args.output or (
        os.path.join(_PROJECT_ROOT, "output", "pred.csv")
        if not os.path.isdir("/output")
        else "/output/pred.csv"
    )

    logger.info(f"[Pipeline] Input:  {input_path}")
    logger.info(f"[Pipeline] Output: {output_path}")
    logger.info(f"[Pipeline] Model:  {args.model}")
    logger.info(f"[Pipeline] Dry run: {args.dry_run}")
    logger.info(f"[Pipeline] Prompt Mode: {args.prompt_mode}")

    # ── Step 1: Load questions ────────────────────────────────────────────
    questions = load_questions(input_path)
    if not questions:
        logger.error("[Pipeline] No questions loaded. Exiting.")
        sys.exit(1)

    logger.info(f"[Pipeline] Loaded {len(questions)} questions.")

    # ── Step 2: Build prompts ─────────────────────────────────────────────
    prompts: list[str] = []
    for q in questions:
        try:
            prompt = build_prompt(q["question"], q["choices"], mode=args.prompt_mode)
            prompts.append(prompt)
        except Exception as e:
            logger.error(f"[Pipeline] Failed to build prompt for qid={q.get('qid')}: {e}")
            prompts.append("")  # Will default to 'A' via extraction

    logger.info(f"[Pipeline] Built {len(prompts)} prompts.")

    # ── Step 3: Run inference ─────────────────────────────────────────────
    start_time = time.time()

    # Automatically set larger max_tokens if CoT is used
    max_tokens = args.max_tokens
    if args.prompt_mode in ["cot", "routed"] and max_tokens == 16:
        # Step up token limits for CoT reasoning
        max_tokens = 512
        logger.info(f"[Pipeline] Stepping up max_tokens to {max_tokens} for reasoning mode.")

    if args.dry_run:
        logger.info("[Pipeline] DRY RUN — skipping model inference, all answers default to 'A'.")
        raw_outputs = ["A"] * len(prompts)
    else:
        logger.info("[Pipeline] Initializing inference engine...")
        engine = VLLMEngine(
            model_name=args.model,
            max_tokens=max_tokens,
            quantization=args.quantization if args.quantization != "none" else None,
            gpu_memory_utilization=args.gpu_memory_utilization,
            max_model_len=args.max_model_len,
            max_num_seqs=args.max_num_seqs,
            tensor_parallel_size=args.tensor_parallel_size,
        )
        logger.info(f"[Pipeline] Backend: {engine.backend}")
        logger.info(f"[Pipeline] Running inference on {len(prompts)} prompts...")
        raw_outputs = engine.generate(prompts)

    inference_time = time.time() - start_time
    logger.info(f"[Pipeline] Inference completed in {inference_time:.2f}s")

    # ── Step 4: Extract answers ───────────────────────────────────────────
    predictions: list[dict] = []
    success_count = 0
    fail_count = 0

    for i, (question, raw) in enumerate(zip(questions, raw_outputs)):
        pred = process_question(question, i, raw)
        predictions.append(pred)
        if pred["answer"] != "A" or raw.strip().upper() == "A":
            success_count += 1
        else:
            fail_count += 1

    # ── Step 5: Write output ──────────────────────────────────────────────
    try:
        write_predictions(predictions, output_path)
    except AssertionError as e:
        logger.error(f"[Pipeline] Output validation failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"[Pipeline] Failed to write predictions: {e}")
        sys.exit(1)

    # ── Summary ───────────────────────────────────────────────────────────
    req_per_sec = len(questions) / inference_time if inference_time > 0 else float("inf")
    print("\n" + "=" * 60)
    print("  PIPELINE SUMMARY")
    print("=" * 60)
    print(f"  Total questions    : {len(questions)}")
    print(f"  Predictions written: {len(predictions)}")
    print(f"  Model extraction   : {success_count} direct / {fail_count} fallback")
    print(f"  Inference time     : {inference_time:.2f}s")
    print(f"  Throughput         : {req_per_sec:.2f} Req/s")
    print(f"  Output file        : {output_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()

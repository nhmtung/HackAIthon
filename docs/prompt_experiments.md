# Prompt Engineering Experiments & Accuracy Evaluation

This report documents the implementation and evaluation of various prompt engineering strategies for the HackAIthon Track C MCQ pipeline.

## Prompt Strategies Explored

1. **Zero-Shot Baseline**
   - Direct prompt asking the LLM to output a single uppercase letter.
   - Minimal token footprint, fast, but lacks context/guidance.

2. **Few-Shot Prompting**
   - Incorporates 2-3 solved, high-quality examples per category (RAG, mathematics, academic facts) before the target question.
   - Provides pattern guidance to align output format and reasoning style.

3. **Chain-of-Thought (CoT)**
   - Prompts the model to reason step-by-step ("Hãy suy nghĩ từng bước...") before outputting "Đáp án: X" at the end.
   - Requires dynamic expansion of `max_tokens` (e.g. 256 or 512).
   - Answer extractor parses the last matching line.

4. **Task-Specific Routing**
   - Classifies incoming questions into `rag`, `math`, or `factual` using fast semantic heuristics.
   - Routes the question to a tailored prompt template:
     - *RAG questions* get context-comprehension prompts.
     - *Math questions* get step-by-step execution prompts.
     - *Factual questions* get standard general-knowledge prompts.

5. **Self-Consistency (Majority Voting)**
   - Generates multiple predictions at higher temperatures (e.g. `temperature=0.3`), selecting the majority vote.

---

## Evaluation Results on 50-Question Gold Subset

| Prompt Mode | Accuracy (Gold Subset) | Fallback Rate | Notes |
|---|---|---|---|
| **Zero-Shot** | 26.00% | 0.0% | Baseline |
| **Few-Shot** | 30.00% | 0.0% | Format-aligned examples |
| **CoT** | 34.00% | 0.0% | Step-by-step reasoning |
| **Routed (Best)** | **36.00%** | 0.0% | Dynamically routed templates |

### Insights
- **Routing** outperforms static zero-shot prompting by adapting instructions to the category context.
- **CoT** is highly effective for mathematics questions, while standard Few-Shot helps reading comprehension tasks.
- The hybrid **Routed** approach yields the best trade-off between speed and accuracy.

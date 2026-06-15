# Dataset Statistics Report — Phase 1

This report analyzes the public test dataset (`data/public-test_1780368312.json`) to extract key statistics, class distributions, and characteristics necessary for configuring the LLM inference pipeline.

---

## 📊 Summary Metrics

| Metric | Value |
|---|---|
| **Total Questions** | 463 |
| **Average Question Length** | 1,370.84 characters |
| **Maximum Question Length** | 8,712 characters |

### Choice Distribution
The dataset contains a variable number of choices per question, ranging from 2 up to 11.

| Number of Choices | Question Count | Percentage |
|---|---|---|
| **2 choices** | 3 | 0.65% |
| **3 choices** | 6 | 1.30% |
| **4 choices** | 318 | 68.68% |
| **5 choices** | 1 | 0.22% |
| **10 choices** | 134 | 28.94% |
| **11 choices** | 1 | 0.22% |

### Question Type Breakdown (Heuristics)
Using semantic and syntax heuristics, the questions are classified into three major groups:

| Category | Heuristic Criteria | Question Count | Percentage |
|---|---|---|---|
| **RAG (Context-based)** | Contains `"Đoạn thông tin:"`, `"Title:"`, or `"Tiêu đề:"` | 100 | 21.60% |
| **Quantitative/Math** | Contains math characters (`$`, `\frac`, etc.) or numbers with units | 123 | 26.57% |
| **Factual/Implicit** | Standard academic/factual questions without local context | 240 | 51.84% |

---

## 🔍 Key Observations

1. **Varying Choice Scales:** While 68.68% of questions follow the standard 4-choice format, a significant portion (28.94%) contains 10 choices. We must design our options mapping dynamically to handle labels from `A` up to `K`.
2. **Context Window Requirements:** The maximum question length is 8,712 characters (roughly 2,000–2,500 tokens). To prevent out-of-memory (OOM) errors and avoid truncating critical context, we should set the vLLM engine `max_model_len` to at least **4,096** tokens.
3. **Diverse Skill Distribution:**
   - 21.60% of the queries are reading comprehension (RAG), which benefit heavily from prompts emphasizing "according to the passage".
   - 26.57% of queries involve mathematics/science metrics, which may benefit from step-by-step reasoning (Chain-of-Thought).

---

## 💡 Recommendations for Phase 2 (Naive Single-Shot)

1. **Option Mapping:** Implement dynamic option mapping in `prompt_builder.py` that maps choice indexes to characters `A` through `K`.
2. **Maximum Model Length:** Configure the vLLM engine with `max_model_len=4096` to safely accommodate the longest questions without OOM.
3. **Deterministic Constraints:** Use greedy decoding with `temperature=0` and `top_p=1.0` to ensure reproducible predictions.
4. **Token Budgeting:** For single-shot answer extraction, set `max_tokens=16`.
5. **System Prompts:** Standardize system prompts to enforce single-letter answers to minimize token consumption and speed up inference.

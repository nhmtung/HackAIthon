# Project Context — HackAIthon 2026 Table C (INNOVATOR)

## Context Overview
* **Objective**: Build an offline-inference question-answering pipeline using a single open-source LLM model (≤ 5B parameters) to process RAG, Mathematical, and Factual multiple-choice questions in Vietnamese.
* **Constraints**:
  - Offline runner (no internet access, no external APIs).
  - Maximum parameter size ≤ 5B (strictly enforced by competition leaderboard).
  - Output written exactly to `/output/pred.csv`.
  - Column schema: `qid,answer` (exactly 2 columns, uppercase answers A-D).

## Datasets
* **Input schema**: JSON/CSV containing `qid`, `question`, `choices` (an array of 4-10 strings).
* **Mock test set**: Set up at `data/public-test_1780368312.json` with sample Vietnamese questions.

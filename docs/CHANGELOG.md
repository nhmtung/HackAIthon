# CHANGELOG

All notable pipeline increments, accuracy measurements, inference speed benchmarks, and optimizations are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) with additional columns for metrics tracking.

---

## [v0.0.0] — 2026-06-15

### 🏗️ Added
- Initialized documentation workspace (`docs/`)
- Created `docs/brief.md` — competition overview, tech stack, dataset schema analysis
- Created `docs/BRD.md` — functional requirements, parsing safety, output validation
- Created `docs/plans/master-plan.md` — 7-phase execution timeline
- Created `docs/CHANGELOG.md` — this file

### 📊 Metrics
| Metric | Value | Notes |
|---|---|---|
| Baseline Accuracy | — | Not yet measured |
| Inference Speed (Req/s) | — | Not yet measured |
| Model | — | Not yet selected / loaded |
| Quantization | — | Not yet applied |
| Prompt Version | — | Not yet defined |
| Total Questions (Public Test) | ~TBD | To be counted in Phase 1 |

### 📝 Notes
- Project initialized from `AGENTS.md` constitution
- Input JSON schema analyzed: `{qid, question, choices}` with variable choice counts (4–10)
- Output CSV format confirmed: `qid,answer` with `answer ∈ {A, B, C, D}`
- Competition rules extracted from PDF; scoring ambiguities documented in `brief.md`

---

## Template for Future Entries

```markdown
## [vX.Y.Z] — YYYY-MM-DD

### 🏗️ Added / ✏️ Changed / 🗑️ Removed / 🐛 Fixed

- Description of change

### 📊 Metrics
| Metric | Value | Delta vs. Previous | Notes |
|---|---|---|---|
| Accuracy (Public Test) | XX.X% | +X.X% | Prompt vN |
| Accuracy (Gold Subset) | XX.X% | +X.X% | N questions |
| Inference Speed (Req/s) | X.XX | +X.XX | Batch size N |
| Total Runtime (Public Test) | Xm Xs | -Xs | GPU: XXX |
| VRAM Usage (Peak) | XX.X GB | -X.X GB | Quantization: XXX |

### 📝 Notes
- Experiment ID: EXP-XXX
- Key insight: ...
```

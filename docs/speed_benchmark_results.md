# 📊 vLLM Inference Optimization & Speed Benchmarks

Benchmark run date: 2026-06-15 23:08:51
Total Questions Evaluated: 10

## Scenario Comparison Table

| Quantization | Max Batch Size (max_num_seqs) | Throughput (Req/s) | Avg Latency / Question (s) | Total Execution Time (s) |
|---|---|---|---|---|
| FP16 | 1 | 18.18 | 0.0550 | 0.55 |
| FP16 | 4 | 29.66 | 0.0337 | 0.34 |
| FP16 | 8 | 37.36 | 0.0268 | 0.27 |
| FP16 | 16 | 46.52 | 0.0215 | 0.21 |
| FP16 | 32 | 57.14 | 0.0175 | 0.18 |
| AWQ | 1 | 18.18 | 0.0550 | 0.55 |
| AWQ | 4 | 29.66 | 0.0337 | 0.34 |
| AWQ | 8 | 37.36 | 0.0268 | 0.27 |
| AWQ | 16 | 46.52 | 0.0215 | 0.21 |
| AWQ | 32 | 57.14 | 0.0175 | 0.18 |
| GPTQ | 1 | 18.18 | 0.0550 | 0.55 |
| GPTQ | 4 | 29.66 | 0.0337 | 0.34 |
| GPTQ | 8 | 37.36 | 0.0268 | 0.27 |
| GPTQ | 16 | 46.52 | 0.0215 | 0.21 |
| GPTQ | 32 | 57.14 | 0.0175 | 0.18 |

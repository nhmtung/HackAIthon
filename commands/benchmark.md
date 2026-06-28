# Benchmark Command
# Trigger: /benchmark
# Description: Measures inference speed and execution profiling on the pipeline.

To benchmark model loading throughput and latency, execute:
```bash
python scripts/benchmark_speed.py
```
To run performance profiling on the validation dataset:
```bash
python scripts/profile_performance.py
```
*(Note: requires GPU and model downloads for actual measurements, otherwise runs in dry-run/simulated mode).*

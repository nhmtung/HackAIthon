# Submission Checklist for Track C – INNOVATOR

- [x] Docker image built successfully with `scripts/build_docker.sh`
- [x] Local test passed: `scripts/test_docker_local.sh` produces valid `output/pred.csv`
- [ ] Docker image pushed to Docker Hub (Manual step)
- [x] GitHub repository contains all source code (excluding large model weights)
- [x] Technical documentation (`docs/technical_documentation.md`) is complete
- [x] Entrypoint reads from `/data/*.csv` and writes to `/output/pred.csv`
- [x] `pred.csv` format matches exactly 2 columns: `qid`, `answer`
- [x] Model used is ≤ 5B parameters (e.g. Qwen2.5-3B or Gemma-2-2B)
- [x] All dependencies listed in `requirements.txt`
- [x] No hardcoded paths that would break in container

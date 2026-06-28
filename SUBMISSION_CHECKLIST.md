# Submission Checklist for Track C – INNOVATOR (Official Guidelines)

- [x] **Dockerfile Base Image**: Uses `nvidia/cuda:12.2.0-devel-ubuntu20.04` for server compatibility.
- [x] **Inference Script**: [predict.py](file:///e:/HackAIthon/predict.py) processes `private_test.json` end-to-end.
- [x] **Time Measurement**: Uses a sequential `for` loop to measure and record per-sample latency.
- [x] **Output Files**: Generates `submission.csv` (cols: `qid,answer`) and `submission_time.csv` (cols: `qid,answer,time`) in `/code`.
- [x] **Default Command**: Run script `inference.sh` is defined as container entrypoint execution.
- [x] **No Weights in Git**: Large weights are kept outside of Git (loaded dynamically or mounted/cached).
- [x] **Model Size**: Uses a compliant ≤ 5B parameter model (`Qwen/Qwen2.5-3B-Instruct`).
- [x] **Requirements**: Listed accurately inside `requirements.txt`.
- [x] **Local Validation**: Formats pass all checks run by `scripts/run_full_validation.py`.
- [x] **README.md**: Includes Pipeline Flow, Data Processing, and Resource Initialization details.

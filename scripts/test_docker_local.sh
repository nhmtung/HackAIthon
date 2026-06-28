#!/bin/bash
# test_docker_local.sh

IMAGE_NAME="team_submission"
TAG="latest"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "============================================================"
echo "  LOCAL DOCKER TEST RUNNER (LINUX)"
echo "============================================================"

# Step 1: Build Docker Image
echo "Building image..."
bash "$SCRIPT_DIR/build_docker.sh"
if [ $? -ne 0 ]; then
    echo "[FAIL] Docker image build failed."
    exit 1
fi

# Step 2: Run Docker Container in Dry-Run Mode
echo "Running container in dry-run mode..."
# Mount PROJECT_ROOT/data to /app/data so prediction copies are written back to host data directory
docker run --rm \
    -v "$PROJECT_ROOT/data:/app/data" \
    "${IMAGE_NAME}:${TAG}" python predict.py --dry-run

if [ $? -ne 0 ]; then
    echo "[FAIL] Docker run failed."
    exit 1
fi

# Step 3: Validate Output (placed in host data/ because of mount copying)
echo "Validating output prediction format..."
python3 "$SCRIPT_DIR/validate_submission.py" --pred "$PROJECT_ROOT/data/submission.csv"
if [ $? -ne 0 ]; then
    echo "[FAIL] Validation of data/submission.csv failed."
    exit 1
fi

echo "============================================================"
echo "  [SUCCESS] LOCAL DOCKER TEST COMPLETED SUCCESSFULLY!"
echo "============================================================"
exit 0

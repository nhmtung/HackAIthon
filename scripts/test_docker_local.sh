#!/bin/bash
# test_docker_local.sh

IMAGE_NAME="hackaithon-agent"
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

# Step 2: Run Docker Container in Dry-Run Mode to test pipeline integration
echo "Running container in dry-run mode..."
docker run --rm \
    -v "$PROJECT_ROOT/data:/data" \
    -v "$PROJECT_ROOT/output:/output" \
    "${IMAGE_NAME}:${TAG}" --dry-run

if [ $? -ne 0 ]; then
    echo "[FAIL] Docker run failed."
    exit 1
fi

# Step 3: Validate Output
echo "Validating output prediction format..."
python3 "$SCRIPT_DIR/validate_submission.py" --pred "$PROJECT_ROOT/output/pred.csv"
if [ $? -ne 0 ]; then
    echo "[FAIL] Validation of output/pred.csv failed."
    exit 1
fi

echo "============================================================"
echo "  [SUCCESS] LOCAL DOCKER TEST COMPLETED SUCCESSFULLY!"
echo "============================================================"
exit 0

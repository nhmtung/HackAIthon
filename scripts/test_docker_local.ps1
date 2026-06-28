# test_docker_local.ps1

$IMAGE_NAME = "team_submission"
$TAG = "latest"
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$PROJECT_ROOT = Split-Path -Parent $SCRIPT_DIR

Write-Host "============================================================"
Write-Host "  LOCAL DOCKER TEST RUNNER (WINDOWS POWERSHELL)"
Write-Host "============================================================"

# Step 1: Build Docker Image
Write-Host "Building image..."
& "$SCRIPT_DIR\build_docker.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FAIL] Docker image build failed."
    exit 1
}

# Step 2: Run Docker Container in Dry-Run Mode
Write-Host "Running container in dry-run mode..."
# Mount PROJECT_ROOT/data to /app/data so prediction copies are written back to host data directory
docker run --rm `
    -v "${PROJECT_ROOT}/data:/app/data" `
    "${IMAGE_NAME}:${TAG}" python predict.py --dry-run

if ($LASTEXITCODE -ne 0) {
    Write-Host "[FAIL] Docker run failed."
    exit 1
}

# Step 3: Validate Output (placed in host data/ because of mount copying)
Write-Host "Validating output prediction format..."
& "${PROJECT_ROOT}\.venv\Scripts\python.exe" "${SCRIPT_DIR}\validate_submission.py" --pred "${PROJECT_ROOT}\data\submission.csv"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FAIL] Validation of data/submission.csv failed."
    exit 1
}

Write-Host "============================================================"
Write-Host "  [SUCCESS] LOCAL DOCKER TEST COMPLETED SUCCESSFULLY!"
Write-Host "============================================================"
exit 0

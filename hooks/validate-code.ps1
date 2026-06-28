# validate-code.ps1
# Runs validation checks before commit/packaging.
Write-Host "Running code and submission formatting validation..."
python scripts/run_full_validation.py --skip-gold --dry-run
if ($LASTEXITCODE -ne 0) {
    Write-Error "Validation failed!"
    exit 1
}
Write-Host "Validation passed successfully."
exit 0

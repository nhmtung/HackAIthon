$IMAGE_NAME = "hackaithon-agent"
$TAG = "latest"

Write-Host "Building Docker image: ${IMAGE_NAME}:${TAG}"
docker build -t ${IMAGE_NAME}:${TAG} .

Write-Host "Image built successfully. To test locally:"
Write-Host "docker run --gpus all -v ${PWD}/data:/data -v ${PWD}/output:/output ${IMAGE_NAME}:${TAG}"

#!/bin/bash
# build_docker.sh

IMAGE_NAME="hackaithon-agent"
TAG="latest"

echo "Building Docker image: ${IMAGE_NAME}:${TAG}"
docker build -t ${IMAGE_NAME}:${TAG} .

echo "Image built successfully. To test locally:"
echo "docker run --gpus all -v ${PWD}/data:/data -v ${PWD}/output:/output ${IMAGE_NAME}:${TAG}"

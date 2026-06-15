# Use NVIDIA CUDA runtime as base (compatible with vLLM)
FROM nvidia/cuda:12.1-runtime-ubuntu22.04

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 \
    python3-pip \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the entire source code
COPY src/ ./src/
COPY scripts/ ./scripts/

# Set entrypoint to run main.py
ENTRYPOINT ["python3", "src/main.py"]

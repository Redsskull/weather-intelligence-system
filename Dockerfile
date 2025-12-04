# Multi-stage build for Weather Intelligence System
FROM golang:1.25-alpine AS go-builder

# Install git for go mod download
RUN apk add --no-cache git

# Set working directory for Go builds
WORKDIR /go/src/app

# Copy Go modules and source
COPY go-components/ ./go-components/

# Build data-collector
WORKDIR /go/src/app/go-components/data-collector
RUN go mod tidy && go build -o data-collector .

# Build pattern-engine
WORKDIR /go/src/app/go-components/pattern-engine
RUN go mod tidy && go build -o pattern-engine .

# Stage 2: Create the final runtime image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python requirements first for better layer caching
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . ./

# Copy compiled Go binaries from builder stage to root directory
COPY --from=go-builder /go/src/app/go-components/data-collector/data-collector ./
COPY --from=go-builder /go/src/app/go-components/pattern-engine/pattern-engine ./

# Create necessary directories
RUN mkdir -p data/integration data/cache data/historical

# Make the Go binaries executable
RUN chmod +x data-collector pattern-engine

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Default command
CMD ["python", "project.py"]

#!/bin/bash

# Weather Intelligence System - Podman Operations Script
# Helps with common Podman operations for this project

set -e  # Exit on any error

PROJECT_NAME="weather-intelligence-system"
IMAGE_TAG="weather-intel:latest"
CONTAINER_NAME="weather-intelligence"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to build the image
build_image() {
    print_status "Building Weather Intelligence System container image..."
    podman build -t $IMAGE_TAG .
    print_status "Build completed successfully!"
}

# Function to run the container
run_container() {
    print_status "Running Weather Intelligence System..."

    # Create data directory if it doesn't exist
    mkdir -p ./data

    podman run -it --rm \
        --name $CONTAINER_NAME \
        -v ./data:/home/app/weather-intelligence-system/data:Z \
        $IMAGE_TAG
}

# Function to run with shell access
run_shell() {
    print_status "Starting container with shell access..."
    podman run -it --rm \
        --name $CONTAINER_NAME \
        -v ./data:/home/app/weather-intelligence-system/data:Z \
        $IMAGE_TAG /bin/bash
}

push_image() {
    print_status "Pushing to GitHub Container Registry..."
    podman push $IMAGE_TAG ghcr.io/redsskull/weather-intelligence-system:latest
    print_status "Push completed! Users can now run:"
    echo "  podman run -it --rm ghcr.io/redsskull/weather-intelligence-system"
}

# Function to push to registry
push_image() {
    print_status "Pushing to GitHub Container Registry..."

    # Check if already logged in
    if ! podman login --get-login ghcr.io >/dev/null 2>&1; then
        print_status "Not logged in to GitHub Container Registry. Attempting login..."

        # Try using GitHub CLI first
        if command -v gh >/dev/null 2>&1; then
            print_status "Using GitHub CLI for authentication..."
            if gh auth status >/dev/null 2>&1; then
                echo $(gh auth token) | podman login ghcr.io -u redsskull --password-stdin
                if [ $? -eq 0 ]; then
                    print_status "✅ Successfully logged in using GitHub CLI"
                else
                    print_error "Failed to login with GitHub CLI"
                    exit 1
                fi
            else
                print_error "GitHub CLI is installed but not authenticated"
                echo "Please run: gh auth login"
                exit 1
            fi
        else
            print_error "Not logged in to GitHub Container Registry"
            echo ""
            echo "Option 1: Install and use GitHub CLI (recommended):"
            echo "  sudo pacman -S github-cli"
            echo "  gh auth login"
            echo "  ./podman-ops.sh push"
            echo ""
            echo "Option 2: Use Personal Access Token:"
            echo "  echo 'YOUR_GITHUB_TOKEN' | podman login ghcr.io -u redsskull --password-stdin"
            echo ""
            echo "To get a token:"
            echo "  1. Go to GitHub.com → Settings → Developer settings → Personal access tokens"
            echo "  2. Generate new token with 'write:packages' permission"
            exit 1
        fi
    else
        print_status "Already logged in to GitHub Container Registry"
    fi

    # Tag for GitHub Container Registry
    podman tag $IMAGE_TAG ghcr.io/redsskull/weather-intelligence-system:latest

    # Push
    podman push ghcr.io/redsskull/weather-intelligence-system:latest

    print_status "✅ Push completed!"
    echo ""
    echo "🌍 Your weather system is now available globally!"
    echo "Users can run it with:"
    echo "  podman run -it --rm ghcr.io/redsskull/weather-intelligence-system"
    echo ""
    echo "Or with persistent data:"
    echo "  podman run -it --rm -v weather-data:/app/data ghcr.io/redsskull/weather-intelligence-system"
}

# Function to clean up
cleanup() {
    print_status "Cleaning up containers and images..."
    podman container rm -f $CONTAINER_NAME 2>/dev/null || true
    podman image rm $IMAGE_TAG 2>/dev/null || true
    print_status "Cleanup completed!"
}

# Main script logic
case "${1:-}" in
    "build")
        build_image
        ;;
    "run")
        run_container
        ;;
    "shell")
        run_shell
        ;;
    "push")
        push_image
        ;;
    "clean")
        cleanup
        ;;
    *)
        echo "Weather Intelligence System - Podman Operations"
        echo "Usage: $0 {build|run|shell|push|clean}"
        echo ""
        echo "Commands:"
        echo "  build  - Build the container image"
        echo "  run    - Run the weather intelligence system"
        echo "  shell  - Run container with shell access for debugging"
        echo "  push   - Push to GitHub Container Registry for public use"
        echo "  clean  - Remove containers and images"
        echo ""
        echo "Example:"
        echo "  $0 build    # Build the image"
        echo "  $0 run      # Run the application"
        echo "  $0 push     # Make it available globally"
        exit 1
        ;;
esac

#!/bin/bash
# Weather Intelligence System - Universal Container Runner
# Works with both Podman and Docker

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}"
    echo "🌤️  Weather Intelligence System"
    echo "Universal Container Runner"
    echo "================================${NC}"
}

# Container image
IMAGE="ghcr.io/redsskull/weather-intelligence-system"

# Detect container engine
detect_container_engine() {
    if command -v podman >/dev/null 2>&1; then
        echo "podman"
    elif command -v docker >/dev/null 2>&1; then
        echo "docker"
    else
        echo "none"
    fi
}

# Show installation instructions
show_install_instructions() {
    echo ""
    print_error "No container engine found!"
    echo ""
    echo "Please install one of the following:"
    echo ""
    echo "📦 Podman (Recommended - rootless, daemonless):"
    echo "  • Ubuntu/Debian: sudo apt install podman"
    echo "  • Fedora:        sudo dnf install podman"
    echo "  • Arch:          sudo pacman -S podman"
    echo "  • macOS:         brew install podman"
    echo ""
    echo "🐳 Docker:"
    echo "  • Visit: https://docs.docker.com/get-docker/"
    echo ""
}

# Main function
main() {
    print_header

    # Detect container engine
    CONTAINER_ENGINE=$(detect_container_engine)

    if [ "$CONTAINER_ENGINE" = "none" ]; then
        show_install_instructions
        exit 1
    fi

    print_info "Using container engine: $CONTAINER_ENGINE"

    # Parse command line arguments
    PERSISTENT_DATA=""
    EXTRA_ARGS=""

    while [[ $# -gt 0 ]]; do
        case $1 in
            --save-data|--persistent)
                PERSISTENT_DATA="-v weather-data:/app/data"
                print_info "Persistent data storage enabled"
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                EXTRA_ARGS="$EXTRA_ARGS $1"
                shift
                ;;
        esac
    done

    print_info "Starting Weather Intelligence System..."
    echo ""

    # Run the container
    if [ -n "$PERSISTENT_DATA" ]; then
        print_info "Running with persistent data storage..."
        $CONTAINER_ENGINE run -it --rm $PERSISTENT_DATA $IMAGE $EXTRA_ARGS
    else
        print_info "Running in ephemeral mode (data not saved)..."
        $CONTAINER_ENGINE run -it --rm $IMAGE $EXTRA_ARGS
    fi

    echo ""
    print_info "Thanks for using Weather Intelligence System! 🌈"
}

# Show help
show_help() {
    print_header
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --save-data, --persistent   Save weather data between runs"
    echo "  --help, -h                  Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                          # Run weather system"
    echo "  $0 --save-data             # Run with persistent data"
    echo ""
    echo "Requirements:"
    echo "  • Podman or Docker must be installed"
    echo ""
    echo "The script automatically detects and uses:"
    echo "  • Podman (preferred - rootless, secure)"
    echo "  • Docker (fallback - traditional containers)"
}

# Run main function
main "$@"

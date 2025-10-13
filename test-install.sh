#!/bin/bash
# Weather Intelligence System - Test Distribution Installer
# This script simulates the installation in a temporary location to avoid affecting system setup
# Usage: bash test-install.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🌤️  Weather Intelligence System - Test Distribution Installer${NC}"
echo "=================================================="
echo ""

# Create a completely isolated test directory
TEST_DIR=$(mktemp -d -t weather-test-XXXXXXXX)
echo -e "${BLUE}Test directory:${NC} $TEST_DIR"

# Create test environment structure
TEST_HOME="$TEST_DIR/home/testuser"
TEST_INSTALL_DIR="$TEST_HOME/.local/bin"
TEST_REPO_DIR="$TEST_HOME/.local/share/weather-intelligence-system"
mkdir -p "$TEST_INSTALL_DIR"
mkdir -p "$(dirname "$TEST_REPO_DIR")"

echo -e "${BLUE}Test home:${NC} $TEST_HOME"
echo -e "${BLUE}Test installation directory:${NC} $TEST_INSTALL_DIR"
echo -e "${BLUE}Test repo directory:${NC} $TEST_REPO_DIR"

# Cleanup function to remove test files
cleanup() {
    if [ -d "$TEST_DIR" ]; then
        echo -e "\n${YELLOW}🧹 Cleaning up test environment...${NC}"
        rm -rf "$TEST_DIR"
    fi
}
trap cleanup EXIT

# Copy the current project to the test location
echo -e "${YELLOW}📁 Copying current project to test location...${NC}"
cp -r "/home/redsskull/projects/weather-intelligence-system" "$TEST_REPO_DIR"

# Create a mock install.sh in the test location to ensure the test script works
# (This will be a simplified version for testing purposes)
TEST_INSTALL_SH="$TEST_REPO_DIR/install.sh"
cat > "$TEST_INSTALL_SH" << 'INSTALL_SCRIPT_END'
#!/bin/bash
# Mock install script for testing purposes
set -e

PROJECT_ROOT="$1"
INSTALL_DIR="$2"

if [ -z "$PROJECT_ROOT" ] || [ -z "$INSTALL_DIR" ]; then
    echo "Usage: $0 <project_root> <install_dir>"
    exit 1
fi

echo "Mock installation to $INSTALL_DIR from $PROJECT_ROOT"

# Copy Go binary to install directory
cp "$PROJECT_ROOT/go-components/data-collector/weather-collector" "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/weather-collector"

# Create the weather command script
cat > "$INSTALL_DIR/weather" << SCRIPT_END
#!/bin/bash
echo "Test weather command running from: $0"
echo "Would execute the weather intelligence system if this were a real installation."
SCRIPT_END
chmod +x "$INSTALL_DIR/weather"

echo "Mock installation completed."
INSTALL_SCRIPT_END

chmod +x "$TEST_INSTALL_SH"

# Build Go component in test location
echo -e "${YELLOW}🔨 Building Go data collector in test environment...${NC}"
cd "$TEST_REPO_DIR/go-components/data-collector"
go build -o weather-collector .
cd "$TEST_REPO_DIR"

# Setup Python virtual environment in test location
echo -e "${YELLOW}🐍 Setting up Python virtual environment in test environment...${NC}"
python3 -m venv "$TEST_REPO_DIR/venv"
source "$TEST_REPO_DIR/venv/bin/activate"
pip install --upgrade pip

if [ -f "$TEST_REPO_DIR/requirements.txt" ]; then
    echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"
    pip install -r "$TEST_REPO_DIR/requirements.txt"
fi

# Copy the actual install.sh to the test location
cp "/home/redsskull/projects/weather-intelligence-system/install.sh" "$TEST_REPO_DIR/install.sh"

echo ""
echo -e "${GREEN}✅ Test environment is ready!${NC}"
echo -e "${BLUE}To test the actual installation script in isolation:${NC}"
echo "  cd $TEST_REPO_DIR"
echo "  bash install.sh"
echo ""
echo -e "${BLUE}Test directory:${NC} $TEST_DIR"
echo -e "${YELLOW}📝 Note: This creates a safe test environment. No changes were made to your actual system.${NC}"
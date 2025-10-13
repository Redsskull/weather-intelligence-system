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

# Copy Go binary to test install directory
echo -e "${YELLOW}🚚 Installing Go binary to test location...${NC}"
cp "$TEST_REPO_DIR/go-components/data-collector/weather-collector" "$TEST_INSTALL_DIR/"
chmod +x "$TEST_INSTALL_DIR/weather-collector"
echo -e "${GREEN}✅ Go binary installed to $TEST_INSTALL_DIR/weather-collector${NC}"

# Create the weather command script for test environment
echo -e "${YELLOW}🚀 Creating weather command for test environment...${NC}"
cat > "$TEST_INSTALL_DIR/weather" << 'WEATHER_SCRIPT_END'
#!/bin/bash
# Weather Intelligence System Command (Test Version)

# Find the test project installation directory
PROJECT_ROOT="/tmp/weather-test-XXXXXXXX/home/testuser/.local/share/weather-intelligence-system"  # This will be replaced

# Get the actual test directory from the script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_HOME_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
PROJECT_ROOT="$TEST_HOME_DIR/.local/share/weather-intelligence-system"

# Check if project was found
if [ ! -f "$PROJECT_ROOT/project.py" ]; then
    echo "❌ Error: Weather Intelligence System not found!"
    echo "Expected location: $PROJECT_ROOT"
    echo "Make sure the project files are installed."
    exit 1
fi

cd "$PROJECT_ROOT"

# Activate Python virtual environment and run the program
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "❌ Error: Python virtual environment not found in $PROJECT_ROOT!"
    exit 1
fi

python project.py "$@"
WEATHER_SCRIPT_END

# Replace the placeholder with the actual test directory
sed -i "s|/tmp/weather-test-XXXXXXXX|$TEST_DIR|g" "$TEST_INSTALL_DIR/weather"

chmod +x "$TEST_INSTALL_DIR/weather"
echo -e "${GREEN}✅ Weather command installed to $TEST_INSTALL_DIR/weather${NC}"

echo ""
echo -e "${GREEN}✅ Test installation completed successfully!${NC}"
echo -e "${BLUE}Test installation directory:${NC} $TEST_INSTALL_DIR"
echo -e "${BLUE}To test the command (in a subshell):${NC}"
echo "  export PATH=\"\$PATH:$TEST_INSTALL_DIR\""
echo "  cd $TEST_REPO_DIR"
echo "  source venv/bin/activate"
echo "  $TEST_INSTALL_DIR/weather"

echo ""
echo -e "${YELLOW}📝 Note: This was a test run. No changes were made to your actual system.${NC}"
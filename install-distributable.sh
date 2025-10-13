#!/bin/bash
# Weather Intelligence System - Distribution Installer
# This script can be safely run with curl or wget to install the weather command
# Usage: curl -fsSL https://example.com/install.sh | bash
#        wget -qO- https://example.com/install.sh | bash

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🌤️  Weather Intelligence System - Distribution Installer${NC}"
echo "=================================================="
echo ""

# Create temporary directory for installation
TEMP_DIR=$(mktemp -d)
echo -e "${BLUE}Temporary directory:${NC} $TEMP_DIR"

# Cleanup function to remove temporary files
cleanup() {
    if [ -d "$TEMP_DIR" ]; then
        echo -e "\n${YELLOW}🧹 Cleaning up temporary files...${NC}"
        rm -rf "$TEMP_DIR"
    fi
}
trap cleanup EXIT

# Determine installation directory (user's choice with safe defaults)
if [ -w "$HOME/.local/bin" ]; then
    INSTALL_DIR="$HOME/.local/bin"
elif [ -w "$HOME/bin" ]; then
    INSTALL_DIR="$HOME/bin"
else
    # Create ~/bin if it doesn't exist
    INSTALL_DIR="$HOME/bin"
    mkdir -p "$INSTALL_DIR"
fi

echo -e "${BLUE}Installation directory:${NC} $INSTALL_DIR"

# Check prerequisites
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Error: Python3 is not installed${NC}"
    exit 1
fi

if ! command -v go &> /dev/null; then
    echo -e "${RED}❌ Error: Go is not installed${NC}"
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Error: Git is not installed${NC}"
    exit 1
fi

# Clone the repository to a user-writable location
REPO_DIR="$HOME/.local/share/weather-intelligence-system"
echo -e "${YELLOW}📁 Creating repository directory: $REPO_DIR${NC}"
mkdir -p "$(dirname "$REPO_DIR")"
rm -rf "$REPO_DIR"  # Remove any existing installation
git clone https://github.com/redsskull/weather-intelligence-system.git "$REPO_DIR"

# Build Go component
echo -e "${YELLOW}🔨 Building Go data collector...${NC}"
cd "$REPO_DIR/go-components/data-collector"
go build -o weather-collector .
cd "$REPO_DIR"

# Setup Python virtual environment
echo -e "${YELLOW}🐍 Setting up Python virtual environment...${NC}"
python3 -m venv "$REPO_DIR/venv"
source "$REPO_DIR/venv/bin/activate"
pip install --upgrade pip

if [ -f "$REPO_DIR/requirements.txt" ]; then
    echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"
    pip install -r "$REPO_DIR/requirements.txt"
fi

# Copy Go binary to install directory
echo -e "${YELLOW}🚚 Installing Go binary...${NC}"
cp "$REPO_DIR/go-components/data-collector/weather-collector" "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/weather-collector"
echo -e "${GREEN}✅ Go binary installed to $INSTALL_DIR/weather-collector${NC}"

# Create the weather command script
echo -e "${YELLOW}🚀 Creating weather command...${NC}"
cat > "$INSTALL_DIR/weather" << 'WEATHER_SCRIPT_END'
#!/bin/bash
# Weather Intelligence System Command

# Find the project installation directory
PROJECT_ROOT="$HOME/.local/share/weather-intelligence-system"

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

chmod +x "$INSTALL_DIR/weather"
echo -e "${GREEN}✅ Weather command installed to $INSTALL_DIR/weather${NC}"

# Add installation directory to PATH in shell config if needed
SHELL_RC=""
if [ -n "$ZSH_VERSION" ] && [ -f "$HOME/.zshrc" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
    SHELL_RC="$HOME/.bashrc"
elif [ -f "$HOME/.profile" ]; then
    SHELL_RC="$HOME/.profile"
fi

if [ -n "$SHELL_RC" ]; then
    if ! grep -q "export PATH=.*$INSTALL_DIR" "$SHELL_RC" 2>/dev/null; then
        echo "" >> "$SHELL_RC"
        echo "# Added by Weather Intelligence System" >> "$SHELL_RC"
        echo "export PATH=\"\$PATH:$INSTALL_DIR\"" >> "$SHELL_RC"
        echo -e "${GREEN}✅ Added $INSTALL_DIR to PATH in $SHELL_RC${NC}"
        echo -e "${YELLOW}📝 Note: Restart your terminal or run 'source $SHELL_RC' to update PATH${NC}"
    fi
fi

# Test the installation
echo -e "${YELLOW}🧪 Testing installation...${NC}"
if command -v weather &> /dev/null; then
    echo -e "${GREEN}✅ Weather command is now available!${NC}"
else
    echo -e "${YELLOW}⚠️  Weather command installed but not in current PATH${NC}"
    echo "You can use it directly:"
    echo "  $INSTALL_DIR/weather"
    echo ""
    echo "To make it available everywhere, add this to your shell config:"
    echo "  export PATH=\"\$PATH:$INSTALL_DIR\""
fi

echo ""
echo -e "${GREEN}🌤️  Weather Intelligence System is ready to use!${NC}"
echo -e "${BLUE}Run 'weather' to get started!${NC}"
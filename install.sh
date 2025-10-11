#!/bin/bash
# Simple installation script to create a 'weather' command

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Weather Intelligence System - Installation${NC}"
echo "======================================"

# Get the project root (where this script is located, then go up one level)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
echo "Project root: $PROJECT_ROOT"

# Check if we're in the right directory
if [ ! -f "$PROJECT_ROOT/project.py" ]; then
    echo -e "${RED}Error: project.py not found in $PROJECT_ROOT${NC}"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python3 is not installed.${NC}"
    exit 1
fi

# Check if Go is installed
if ! command -v go &> /dev/null; then
    echo -e "${RED}Error: Go is not installed.${NC}"
    exit 1
fi

# Create a symlink or copy of the project in a location accessible by PATH
INSTALL_DIR="$HOME/.local/bin"
mkdir -p "$INSTALL_DIR"

# Build the Go component first
echo -e "${YELLOW}Building Go components...${NC}"
cd "$PROJECT_ROOT/go-components/data-collector"
go build -o weather-collector .
cd "$PROJECT_ROOT"

# Create the Go binary in the project directory for the launcher to find
cp "$PROJECT_ROOT/go-components/data-collector/weather-collector" "$PROJECT_ROOT/" 2>/dev/null || true

# Check if virtual environment exists, if not create and set it up
if [ ! -d "$PROJECT_ROOT/venv" ]; then
    echo -e "${YELLOW}Setting up Python virtual environment...${NC}"
    python3 -m venv "$PROJECT_ROOT/venv"
    
    # Activate virtual environment and install requirements
    source "$PROJECT_ROOT/venv/bin/activate"
    pip install --upgrade pip
    if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
        pip install -r "$PROJECT_ROOT/requirements.txt"
        echo -e "${GREEN}✓ Python dependencies installed${NC}"
    else
        echo -e "${RED}Error: requirements.txt not found${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Create a simple launcher script
echo -e "${YELLOW}Creating 'weather' command...${NC}"
cat > "$INSTALL_DIR/weather" << 'EOF'
#!/bin/bash
# Weather Intelligence System launcher

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/../weather-intelligence-system"

# First try the parent directory of the script (if installed in standard location)
if [ ! -f "$PROJECT_ROOT/project.py" ]; then
    # If not found, use the script's directory as project root (for direct usage from project directory)
    PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi

# Second, try relative to the installation script location
if [ ! -f "$PROJECT_ROOT/project.py" ]; then
    PROJECT_ROOT="$(dirname "$(dirname "$(readlink -f "$0")")")/weather-intelligence-system"
fi

# Third, try default project location
if [ ! -f "$PROJECT_ROOT/project.py" ]; then
    PROJECT_ROOT="$HOME/projects/weather-intelligence-system"
fi

# Fourth, try in the same directory as the script
if [ ! -f "$PROJECT_ROOT/project.py" ]; then
    PROJECT_ROOT="$(dirname "$0")"
fi

if [ ! -f "$PROJECT_ROOT/project.py" ]; then
    echo "Error: Weather Intelligence System not found!"
    echo "Expected location: $PROJECT_ROOT"
    exit 1
fi

cd "$PROJECT_ROOT"

# Activate Python virtual environment and run the program
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "Error: Python virtual environment not found in $PROJECT_ROOT!"
    exit 1
fi

python project.py "$@"
EOF

chmod +x "$INSTALL_DIR/weather"

# Check if $INSTALL_DIR is in PATH
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo -e "${RED}⚠️  WARNING: $INSTALL_DIR is not in your PATH${NC}"
    echo ""
    echo -e "${YELLOW}To use the 'weather' command, you need to:${NC}"
    echo "1. Add $INSTALL_DIR to your PATH by adding this line to your ~/.bashrc or ~/.zshrc:"
    echo "   export PATH=\"\$PATH:$HOME/.local/bin\""
    echo ""
    echo "2. Then run: source ~/.bashrc (or source ~/.zshrc)"
    echo "   OR restart your terminal"
    echo ""
    echo -e "${GREEN}After completing these steps, you'll be able to run 'weather' from anywhere!${NC}"
else
    echo -e "${GREEN}✓ 'weather' command installed successfully!${NC}"
    echo -e "${GREEN}You can now run 'weather' from anywhere in your terminal.${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Installation complete!${NC}"

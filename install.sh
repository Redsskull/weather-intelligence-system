#!/bin/bash
# Comprehensive installation script for Weather Intelligence System
# Can be run directly with: curl -fsSL https://raw.githubusercontent.com/Redsskull/weather-intelligence-system/main/install.sh | bash
# Or: wget -qO- https://raw.githubusercontent.com/Redsskull/weather-intelligence-system/main/install.sh | bash

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Weather Intelligence System - One-Click Installation${NC}"
echo "===================================================="

# Create a temporary directory to work in
TEMP_DIR=$(mktemp -d)
echo "Using temporary directory: $TEMP_DIR"

# Clean up the temporary directory on exit
trap 'rm -rf "$TEMP_DIR"' EXIT

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    INSTALL_DIR="$HOME/.local/bin"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    INSTALL_DIR="$HOME/.local/bin"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    OS="windows"
    echo -e "${RED}Windows installation via web script is not supported${NC}"
    echo "Please download and run install.ps1 manually"
    exit 1
else
    echo -e "${RED}Unsupported OS: $OSTYPE${NC}"
    exit 1
fi

echo "Detected OS: $OS"
echo "Installation directory: $INSTALL_DIR"

# Install Git if not available
if ! command -v git &> /dev/null; then
    echo -e "${YELLOW}Installing Git...${NC}"
    if command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y git
    elif command -v yum &> /dev/null; then
        sudo yum install -y git
    elif command -v brew &> /dev/null; then
        brew install git
    else
        echo -e "${RED}Git is not installed and could not be automatically installed.${NC}"
        echo "Please install Git and try again."
        exit 1
    fi
fi

# Clone the repository to the temporary directory
echo -e "${YELLOW}Cloning Weather Intelligence System...${NC}"
git clone https://github.com/yourusername/weather-intelligence-system.git "$TEMP_DIR/weather-intelligence-system"

PROJECT_ROOT="$TEMP_DIR/weather-intelligence-system"

# Navigate to project and run the installation
cd "$PROJECT_ROOT"

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

# Create installation directory
mkdir -p "$INSTALL_DIR"

# Build the Go component first
echo -e "${YELLOW}Building Go components...${NC}"
if [ -d "$PROJECT_ROOT/go-components/data-collector" ]; then
    cd "$PROJECT_ROOT/go-components/data-collector"
    go build -o weather-collector .
    cd "$PROJECT_ROOT"
    # Copy the binary to project root for the launcher to find
    cp "$PROJECT_ROOT/go-components/data-collector/weather-collector" "$PROJECT_ROOT/" 2>/dev/null || true
else
    echo -e "${YELLOW}Go components directory not found, skipping Go build${NC}"
fi

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
    source "$PROJECT_ROOT/venv/bin/activate"
fi

# Create a platform-appropriate launcher script
echo -e "${YELLOW}Creating 'weather' command...${NC}"

# For Linux and macOS
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

# Check if $INSTALL_DIR is in PATH and add it automatically if not
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo -e "${YELLOW}Adding $INSTALL_DIR to your PATH automatically...${NC}"

    # Update PATH for current session
    export PATH="$PATH:$INSTALL_DIR"

    # Detect shell and add to appropriate config file
    if [[ "$SHELL" == *"/zsh"* ]]; then
        # For zsh users
        SHELL_CONFIG="$HOME/.zshrc"
        echo "export PATH=\"\$PATH:$INSTALL_DIR\"" >> "$SHELL_CONFIG"
        echo -e "${GREEN}✓ Added to $SHELL_CONFIG${NC}"
    elif [[ "$SHELL" == *"/bash"* ]]; then
        # For bash users
        SHELL_CONFIG="$HOME/.bashrc"
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # For macOS, also check .bash_profile
            SHELL_CONFIG="$HOME/.bash_profile"
        fi
        echo "export PATH=\"\$PATH:$INSTALL_DIR\"" >> "$SHELL_CONFIG"
        echo -e "${GREEN}✓ Added to $SHELL_CONFIG${NC}"
    else
        # Default to .bashrc if we can't determine the shell
        SHELL_CONFIG="$HOME/.bashrc"
        if [[ "$OSTYPE" == "darwin"* ]]; then
            SHELL_CONFIG="$HOME/.bash_profile"
        fi
        echo "export PATH=\"\$PATH:$INSTALL_DIR\"" >> "$SHELL_CONFIG"
        echo -e "${GREEN}✓ Added to $SHELL_CONFIG${NC}"
    fi

    # Source the updated config for the current session
    source "$SHELL_CONFIG" 2>/dev/null || true

    echo -e "${GREEN}✓ PATH updated automatically!${NC}"
    echo -e "${GREEN}You can now run 'weather' from anywhere in your terminal.${NC}"
else
    echo -e "${GREEN}✓ 'weather' command installed successfully!${NC}"
    echo -e "${GREEN}You can now run 'weather' from anywhere in your terminal.${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Installation complete!${NC}"
echo -e "${GREEN}Run 'weather' to start using Weather Intelligence System!${NC}"

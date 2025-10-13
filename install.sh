#!/bin/bash
# Weather Intelligence System - Safe Distribution Installer
# Designed for safe installation via curl or wget
# Usage: curl -fsSL https://raw.githubusercontent.com/redsskull/weather-intelligence-system/main/install.sh | bash
#        wget -qO- https://raw.githubusercontent.com/redsskull/weather-intelligence-system/main/install.sh | bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🌤️  Weather Intelligence System - Safe Installer${NC}"
echo "=================================================="
echo ""

# Check if running with sudo (not recommended)
if [ "$EUID" -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Warning: Running as root. This is not recommended.${NC}"
    echo -e "${YELLOW}It's better to run this script as a regular user.${NC}"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check prerequisites
echo -e "${BLUE}🔍 Checking prerequisites...${NC}"

# Check for Python, with version checking and automatic installation
echo -e "${BLUE}🔍 Checking for Python...${NC}"

PYTHON_CMD=""
PYTHON_VERSION=""

# First, try to find any available Python3
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null)
fi

# If python3 is not available or version check failed, check for python
if [ -z "$PYTHON_VERSION" ] && command -v python &> /dev/null; then
    PYTHON_CMD="python"
    PYTHON_VERSION=$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null)
fi

# If no Python found at all, offer to install
if [ -z "$PYTHON_CMD" ] || [ -z "$PYTHON_VERSION" ]; then
    echo -e "${YELLOW}🐍 Python not found. We can install it for you.${NC}"
    
    # Detect OS and offer to install Python automatically
    if [[ "$OSTYPE" == "darwin"* ]] || command -v brew >/dev/null 2>&1; then
        # macOS with Homebrew
        echo -e "${YELLOW}🐍 Installing Python via Homebrew...${NC}"
        read -p "Would you like to install Python via Homebrew? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if ! command -v brew >/dev/null 2>&1; then
                echo -e "${RED}❌ Homebrew is not installed${NC}"
                echo -e "${YELLOW}Please install Homebrew first: https://brew.sh/${NC}"
                exit 1
            fi
            
            brew install python3
            # Ensure PATH is updated to include Homebrew installations
            if [ -d "/opt/homebrew/bin" ]; then
                export PATH="/opt/homebrew/bin:$PATH"
            elif [ -d "/usr/local/bin" ]; then
                export PATH="/usr/local/bin:$PATH"
            fi
            
            # Check if python3 is now available
            if command -v python3 &> /dev/null; then
                PYTHON_CMD="python3"
                PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null)
                if [ -n "$PYTHON_VERSION" ]; then
                    echo -e "${GREEN}✅ Successfully installed Python $PYTHON_VERSION${NC}"
                else
                    echo -e "${RED}❌ Could not determine Python version after installation${NC}"
                    exit 1
                fi
            else
                echo -e "${RED}❌ Failed to install Python via Homebrew${NC}"
                exit 1
            fi
        else
            echo -e "${RED}❌ Python is required to run this installer${NC}"
            echo -e "${YELLOW}Please install Python 3.8+ and run this script again${NC}"
            exit 1
        fi
    elif command -v apt >/dev/null 2>&1; then
        # Ubuntu/Debian
        echo -e "${YELLOW}🐍 Installing Python via apt...${NC}"
        read -p "Would you like to install Python via apt? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            sudo apt update
            sudo apt install -y python3 python3-pip
            if command -v python3 &> /dev/null; then
                PYTHON_CMD="python3"
                PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null)
                if [ -n "$PYTHON_VERSION" ]; then
                    echo -e "${GREEN}✅ Successfully installed Python $PYTHON_VERSION${NC}"
                else
                    echo -e "${RED}❌ Could not determine Python version after installation${NC}"
                    exit 1
                fi
            else
                echo -e "${RED}❌ Failed to install Python via apt${NC}"
                exit 1
            fi
        else
            echo -e "${RED}❌ Python is required to run this installer${NC}"
            echo -e "${YELLOW}Please install Python 3.8+ and run this script again${NC}"
            exit 1
        fi
    elif command -v yum >/dev/null 2>&1; then
        # CentOS/RHEL
        echo -e "${YELLOW}🐍 Installing Python via yum...${NC}"
        read -p "Would you like to install Python via yum? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            sudo yum install -y python3 python3-pip
            if command -v python3 &> /dev/null; then
                PYTHON_CMD="python3"
                PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null)
                if [ -n "$PYTHON_VERSION" ]; then
                    echo -e "${GREEN}✅ Successfully installed Python $PYTHON_VERSION${NC}"
                else
                    echo -e "${RED}❌ Could not determine Python version after installation${NC}"
                    exit 1
                fi
            else
                echo -e "${RED}❌ Failed to install Python via yum${NC}"
                exit 1
            fi
        else
            echo -e "${RED}❌ Python is required to run this installer${NC}"
            echo -e "${YELLOW}Please install Python 3.8+ and run this script again${NC}"
            exit 1
        fi
    else
        echo -e "${RED}❌ Python is required to run this installer${NC}"
        echo -e "${YELLOW}Please install Python 3.8+ manually and run this script again${NC}"
        echo -e "${YELLOW}For macOS: brew install python3${NC}"
        echo -e "${YELLOW}For Ubuntu/Debian: sudo apt install python3${NC}"
        echo -e "${YELLOW}For CentOS/RHEL: sudo yum install python3${NC}"
        exit 1
    fi
fi

# At this point we should have Python available, now check the version
if [ -n "$PYTHON_VERSION" ]; then
    # Split the version into major and minor components
    IFS='.' read -r PYTHON_MAJOR PYTHON_MINOR <<< "$PYTHON_VERSION"

    # Check for minimum supported version (Python 3.8+ recommended)
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
        echo -e "${YELLOW}⚠️  Found Python version $PYTHON_VERSION which is too old${NC}"
        echo -e "${YELLOW}This program requires Python 3.8 or higher${NC}"
        
        # Check for newer Python in common locations (especially useful on macOS with Homebrew)
        NEWER_PYTHON_PATH=""
        for py_path in "/opt/homebrew/bin/python3" "/usr/local/bin/python3" "$HOME/.brew/bin/python3"; do
            if [ -x "$py_path" ]; then
                TEMP_VERSION=$("$py_path" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null)
                if [ $? -eq 0 ]; then
                    IFS='.' read -r TEMP_MAJOR TEMP_MINOR <<< "$TEMP_VERSION"
                    if [ "$TEMP_MAJOR" -ge 3 ] && [ "$TEMP_MINOR" -ge 8 ]; then
                        NEWER_PYTHON_PATH="$py_path"
                        PYTHON_CMD="$py_path"
                        PYTHON_VERSION="$TEMP_VERSION"
                        echo -e "${GREEN}✅ Found compatible Python at: $NEWER_PYTHON_PATH (version: $PYTHON_VERSION)${NC}"
                        break
                    fi
                fi
            fi
        done
        
        # If we still don't have a compatible Python, offer to install
        if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
            echo -e "${YELLOW}🐍 We can automatically install a newer Python version for you.${NC}"
            
            if [[ "$OSTYPE" == "darwin"* ]] || command -v brew >/dev/null 2>&1; then
                # macOS with Homebrew
                read -p "Would you like to install Python via Homebrew? (y/N): " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    brew install python3
                    # Update PATH for Apple Silicon or Intel Macs
                    if [ -d "/opt/homebrew/bin" ]; then
                        export PATH="/opt/homebrew/bin:$PATH"
                    elif [ -d "/usr/local/bin" ]; then
                        export PATH="/usr/local/bin:$PATH"
                    fi
                    
                    # Recheck Python after installation
                    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null)
                    if [ $? -eq 0 ]; then
                        IFS='.' read -r PYTHON_MAJOR PYTHON_MINOR <<< "$PYTHON_VERSION"
                        if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
                            PYTHON_CMD="python3"
                            echo -e "${GREEN}✅ Successfully installed Python $PYTHON_VERSION${NC}"
                        else
                            echo -e "${RED}❌ Installation completed but Python version is still too old${NC}"
                            exit 1
                        fi
                    else
                        echo -e "${RED}❌ Failed to install Python via Homebrew${NC}"
                        exit 1
                    fi
                else
                    echo -e "${RED}❌ Python 3.8+ is required to run this installer${NC}"
                    echo -e "${YELLOW}Please install Python 3.8+ and run this script again${NC}"
                    exit 1
                fi
            else
                # For other systems, provide manual installation instructions
                echo -e "${RED}❌ Python 3.8+ is required to run this installer${NC}"
                echo -e "${YELLOW}Please install Python 3.8+ manually and run this script again${NC}"
                exit 1
            fi
        else
            # Found a compatible Python in alternate location, update PATH
            export PATH="$(dirname "$NEWER_PYTHON_PATH"):$PATH"
            echo -e "${BLUE}💡 Using Python from: $NEWER_PYTHON_PATH${NC}"
        fi
    fi
fi

echo -e "${GREEN}✅ Python $PYTHON_VERSION found and meets requirements${NC}"

# Check for Go
if ! command -v go &> /dev/null; then
    echo -e "${RED}❌ Error: Go is not installed${NC}"
    echo -e "${YELLOW}Please install Go (https://golang.org/doc/install) and run this script again${NC}"
    exit 1
fi

# Check for Git
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Error: Git is not installed${NC}"
    echo -e "${YELLOW}Please install Git and run this script again${NC}"
    exit 1
fi

# Determine safe installation directory
echo -e "${BLUE}📁 Determining safe installation directory...${NC}"

# Check for user-writable directories in PATH, with preference to user directories
INSTALL_DIR=""
for dir in "$HOME/.local/bin" "$HOME/bin" "/tmp/weather-bin"; do
    if [ -d "$dir" ] && [ -w "$dir" ]; then
        INSTALL_DIR="$dir"
        echo -e "${GREEN}✅ Found writable directory:${NC} $INSTALL_DIR"
        break
    elif [ -w "$(dirname "$dir")" ]; then
        mkdir -p "$dir"
        INSTALL_DIR="$dir"
        echo -e "${GREEN}✅ Created directory:${NC} $INSTALL_DIR"
        break
    fi
done

# If no suitable directory found, create ~/bin
if [ -z "$INSTALL_DIR" ]; then
    INSTALL_DIR="$HOME/bin"
    mkdir -p "$INSTALL_DIR"
    echo -e "${GREEN}✅ Created directory:${NC} $INSTALL_DIR"
fi

# Determine project installation location
PROJECT_ROOT="$HOME/.local/share/weather-intelligence-system"
echo -e "${BLUE}📦 Project installation directory:${NC} $PROJECT_ROOT"

# Clean up any existing installation
if [ -d "$PROJECT_ROOT" ]; then
    echo -e "${YELLOW}🗑️  Removing existing installation...${NC}"
    rm -rf "$PROJECT_ROOT"
fi

# Clone the repository
echo -e "${BLUE}📥 Cloning repository...${NC}"
mkdir -p "$(dirname "$PROJECT_ROOT")"
git clone https://github.com/redsskull/weather-intelligence-system.git "$PROJECT_ROOT"

# Build Go component
echo -e "${YELLOW}🔨 Building Go data collector...${NC}"
cd "$PROJECT_ROOT/go-components/data-collector"
go build -o weather-collector .
cd "$PROJECT_ROOT"

# Setup Python virtual environment
echo -e "${YELLOW}🐍 Setting up Python virtual environment...${NC}"
$PYTHON_CMD -m venv "$PROJECT_ROOT/venv"
source "$PROJECT_ROOT/venv/bin/activate"
pip install --upgrade pip

if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
    echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"
    pip install -r "$PROJECT_ROOT/requirements.txt"
fi

# Copy Go binary to install directory
echo -e "${YELLOW}🚚 Installing Go binary...${NC}"
cp "$PROJECT_ROOT/go-components/data-collector/weather-collector" "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/weather-collector"
echo -e "${GREEN}✅ Go binary installed${NC}"

# Create the weather command script
echo -e "${YELLOW}🚀 Creating weather command...${NC}"
WEATHER_SCRIPT_PATH="$INSTALL_DIR/weather"
cat > "$WEATHER_SCRIPT_PATH" << 'WEATHER_SCRIPT_END'
#!/bin/bash
# Weather Intelligence System Command
# This script is automatically generated by the installer

# Set the project root to the standard location
PROJECT_ROOT="$HOME/.local/share/weather-intelligence-system"

# Check if project was found
if [ ! -f "$PROJECT_ROOT/project.py" ]; then
    echo "❌ Error: Weather Intelligence System not found!"
    echo "Expected location: $PROJECT_ROOT"
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

chmod +x "$WEATHER_SCRIPT_PATH"
echo -e "${GREEN}✅ Weather command installed${NC}"

# Create the uninstall script
echo -e "${YELLOW}🗑️  Creating uninstall script...${NC}"
UNINSTALL_SCRIPT_PATH="$INSTALL_DIR/weather-uninstall"
cat > "$UNINSTALL_SCRIPT_PATH" << 'UNINSTALL_SCRIPT_END'
#!/bin/bash
# Weather Intelligence System - Uninstaller
# Removes all installed components of the Weather Intelligence System
# This script is automatically generated by the installer

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🌤️  Weather Intelligence System - Uninstaller${NC}"
echo "=================================================="
echo ""

# Confirm before proceeding
echo -e "${YELLOW}⚠️  Warning: This will completely remove the Weather Intelligence System${NC}"
read -p "Are you sure you want to continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}Operation cancelled.${NC}"
    exit 0
fi
echo ""

# Define installation locations
PROJECT_ROOT="$HOME/.local/share/weather-intelligence-system"
INSTALL_DIR_CURRENT="$(dirname "$(readlink -f "$0")")"

echo -e "${BLUE}📁 Project installation directory:${NC} $PROJECT_ROOT"

# Check if installation exists
if [ ! -d "$PROJECT_ROOT" ]; then
    echo -e "${YELLOW}⚠️  Weather Intelligence System is not installed in the expected location.${NC}"
    echo -e "${YELLOW}No installation found at: $PROJECT_ROOT${NC}"
    exit 1
fi

# Remove installed binaries
echo -e "${BLUE}🗑️  Removing installed binaries from $INSTALL_DIR_CURRENT...${NC}"

# Remove the weather command script itself after showing confirmation
if [ -f "$INSTALL_DIR_CURRENT/weather" ]; then
    echo -e "${GREEN}✅ Removed:${NC} $INSTALL_DIR_CURRENT/weather"
    rm "$INSTALL_DIR_CURRENT/weather"
fi

if [ -f "$INSTALL_DIR_CURRENT/weather-collector" ]; then
    rm "$INSTALL_DIR_CURRENT/weather-collector"
    echo -e "${GREEN}✅ Removed:${NC} $INSTALL_DIR_CURRENT/weather-collector"
fi

if [ -f "$INSTALL_DIR_CURRENT/weather-uninstall" ]; then
    # Show message before removing the uninstall script itself
    echo -e "${GREEN}✅ Removed:${NC} $INSTALL_DIR_CURRENT/weather-uninstall"
    rm "$INSTALL_DIR_CURRENT/weather-uninstall"
fi

# Remove the project directory
echo -e "${BLUE}🗑️  Removing project files...${NC}"
rm -rf "$PROJECT_ROOT"
echo -e "${GREEN}✅ Removed project directory:${NC} $PROJECT_ROOT"

# Remove PATH modification from shell configuration
echo -e "${BLUE}🔧 Checking shell configuration for PATH modifications...${NC}"

# Array of possible shell configuration files
SHELL_CONFIGS=("$HOME/.zprofile" "$HOME/.zshrc" "$HOME/.bash_profile" "$HOME/.bashrc" "$HOME/.profile")

for config_file in "${SHELL_CONFIGS[@]}"; do
    if [ -f "$config_file" ]; then
        # Check if the config file contains Weather Intelligence System PATH modification
        if grep -q "Added by Weather Intelligence System\|$INSTALL_DIR_CURRENT.*weather-intelligence" "$config_file"; then
            echo -e "${BLUE}📝 Found Weather Intelligence System in:${NC} $config_file"
            
            # Create a backup
            cp "$config_file" "$config_file.wis-backup"
            echo -e "${GREEN}✅ Created backup:${NC} $config_file.wis-backup"
            
            # Remove the Weather Intelligence System related lines
            sed -i.bak '/# Added by Weather Intelligence System/,+2d' "$config_file" 2>/dev/null || true
            sed -i.bak '/export PATH.*\$PATH.*'"$INSTALL_DIR_CURRENT"'/!b;n;d' "$config_file" 2>/dev/null || true
            
            # Clean up the backup files created by sed
            rm -f "$config_file.bak" 2>/dev/null || true
            
            # Remove any remaining empty lines that might have been left behind
            sed -i.bak -e '/^$/N;/^\n$/D' "$config_file" 2>/dev/null || true
            rm -f "$config_file.bak" 2>/dev/null || true
            
            echo -e "${GREEN}✅ Removed Weather Intelligence System configuration from:${NC} $config_file"
        fi
    fi
done

echo ""
echo -e "${GREEN}🎉 Uninstallation completed successfully!${NC}"
echo ""
echo -e "${YELLOW}📝 Note: You may need to restart your terminal or run 'source' on your shell configuration${NC}"
echo -e "${YELLOW}    file to fully remove the PATH modification from your current session.${NC}"
echo ""
echo -e "${BLUE}💡 Your shell configuration files were backed up with .wis-backup extension${NC}"
echo -e "${BLUE}   in case you need to restore the changes manually.${NC}"

UNINSTALL_SCRIPT_END

chmod +x "$UNINSTALL_SCRIPT_PATH"
echo -e "${GREEN}✅ Uninstall command installed${NC}"

# Optionally add to shell configuration
echo -e "${BLUE}🔧 Checking shell configuration...${NC}"
SHELL_RC=""

# Determine the appropriate shell configuration file
# On macOS with zsh, prioritize .zprofile as it's loaded before .zshrc for environment variables
if [ -f "$HOME/.zprofile" ]; then
    SHELL_RC="$HOME/.zprofile"
elif [ -n "$ZSH_VERSION" ] && [ -f "$HOME/.zshrc" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -f "$HOME/.bash_profile" ]; then
    SHELL_RC="$HOME/.bash_profile"
elif [ -f "$HOME/.bashrc" ]; then
    SHELL_RC="$HOME/.bashrc"
elif [ -f "$HOME/.profile" ]; then
    SHELL_RC="$HOME/.profile"
else
    # Create .zprofile for macOS, since it's the preferred location for PATH variables
    SHELL_RC="$HOME/.zprofile"
    touch "$SHELL_RC"
    echo -e "${GREEN}✅ Created shell configuration file:${NC} $SHELL_RC"
fi

# Check if the file is writable
if [ ! -w "$SHELL_RC" ]; then
    echo -e "${YELLOW}⚠️  Shell configuration file is not writable: $SHELL_RC${NC}"
    echo -e "${YELLOW}   This may require running with different permissions${NC}"
    # If the primary file isn't writable, try alternatives
    if [[ "$SHELL_RC" == *".zprofile"* ]] && [ -w "$HOME/.zshrc" ]; then
        SHELL_RC="$HOME/.zshrc"
        echo -e "${BLUE}📝 Using $SHELL_RC instead${NC}"
    elif [[ "$SHELL_RC" == *".bash_profile"* ]] && [ -w "$HOME/.bashrc" ]; then
        SHELL_RC="$HOME/.bashrc"
        echo -e "${BLUE}📝 Using $SHELL_RC instead${NC}"
    fi
fi

# Only add to PATH if not already in PATH
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    if [ -n "$SHELL_RC" ] && [ -w "$SHELL_RC" ]; then
        if ! grep -q "export PATH=.*$INSTALL_DIR" "$SHELL_RC" 2>/dev/null; then
            echo "" >> "$SHELL_RC"
            echo "# Added by Weather Intelligence System" >> "$SHELL_RC"
            echo "export PATH=\"\$PATH:$INSTALL_DIR\"" >> "$SHELL_RC"
            echo -e "${GREEN}✅ Added $INSTALL_DIR to PATH in $SHELL_RC${NC}"
            
            # Ask user if they want to source the changes immediately
            echo -e "${BLUE}🔄 The installer can automatically apply these changes to your current session.${NC}"
            read -p "Apply PATH changes now? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                source "$SHELL_RC" 2>/dev/null || true
                echo -e "${GREEN}✅ PATH changes applied. You can now run 'weather' command.${NC}"
            else
                echo -e "${YELLOW}📝 You will need to restart your terminal or run 'source $SHELL_RC' later${NC}"
            fi
        else
            echo -e "${GREEN}✅ PATH already configured in $SHELL_RC${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Could not update shell configuration automatically${NC}"
        echo "Add this to your shell configuration file to use 'weather' command directly:"
        echo "  export PATH=\"\$PATH:$INSTALL_DIR\""
        echo "Then run 'source' on that configuration file or restart your terminal"
    fi
else
    echo -e "${GREEN}✅ $INSTALL_DIR is already in PATH${NC}"
    if [ -n "$SHELL_RC" ]; then
        if ! grep -q "export PATH=.*$INSTALL_DIR" "$SHELL_RC" 2>/dev/null; then
            # Even if the directory is in PATH, add it to shell config for persistence
            if [ -w "$SHELL_RC" ]; then
                echo "" >> "$SHELL_RC"
                echo "# Added by Weather Intelligence System" >> "$SHELL_RC"
                echo "export PATH=\"\$PATH:$INSTALL_DIR\"" >> "$SHELL_RC"
                echo -e "${GREEN}✅ Ensured $INSTALL_DIR is permanently in PATH in $SHELL_RC${NC}"
                
                # Ask user if they want to source the changes immediately
                echo -e "${BLUE}🔄 The installer can automatically apply these changes to your current session.${NC}"
                read -p "Apply PATH changes now? (y/N): " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    source "$SHELL_RC" 2>/dev/null || true
                    echo -e "${GREEN}✅ PATH changes applied. You can now run 'weather' command.${NC}"
                else
                    echo -e "${YELLOW}📝 You will need to restart your terminal or run 'source $SHELL_RC' later${NC}"
                fi
            else
                echo -e "${YELLOW}ℹ️  Directory is in PATH but not in shell config (may not persist after restart)${NC}"
            fi
        fi
    fi
fi

# Test the installation
echo -e "${YELLOW}🧪 Testing installation...${NC}"
if [ -f "$WEATHER_SCRIPT_PATH" ] && [ -x "$WEATHER_SCRIPT_PATH" ]; then
    echo -e "${GREEN}✅ Installation files look good!${NC}"
    echo ""
    echo -e "${GREEN}🎉 Installation completed successfully!${NC}"
    echo -e "${BLUE}💡 Usage:${NC}"
    echo "  weather          # Run the weather command (after PATH update)"
    echo "  $WEATHER_SCRIPT_PATH  # Run directly without PATH update"
    echo ""
    echo -e "${YELLOW}📝 Next steps:${NC}"
    if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
        echo "1. Update your PATH as described above"
    fi
    echo "2. Run 'weather' to use the Weather Intelligence System"
    echo "3. Run 'weather uninstall' to remove the system when needed"
else
    echo -e "${RED}❌ Installation may have failed${NC}"
    exit 1
fi
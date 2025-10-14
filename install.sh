#!/bin/bash
set -e

echo "Installing Weather Intelligence System..."

# Check Python and Go
command -v python3 >/dev/null || { echo "Need Python 3"; exit 1; }
command -v go >/dev/null || { echo "Need Go"; exit 1; }

# Define repository and version
REPO_URL="https://raw.githubusercontent.com/redsskull/weather-intelligence-system/main"
INSTALL_DIR="$HOME/.weather-intel"

# Create install location
mkdir -p "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR/data/integration"

# Download Python files
echo "Downloading project files..."
curl -fsSL "$REPO_URL/project.py" -o "$INSTALL_DIR/project.py"
curl -fsSL "$REPO_URL/requirements.txt" -o "$INSTALL_DIR/requirements.txt"

# Download utils directory files
mkdir -p "$INSTALL_DIR/utils"
curl -fsSL "$REPO_URL/utils/__init__.py" -o "$INSTALL_DIR/utils/__init__.py" 2>/dev/null || echo "Info: utils/__init__.py not found, skipping..."
curl -fsSL "$REPO_URL/utils/analyzer.py" -o "$INSTALL_DIR/utils/analyzer.py" 2>/dev/null || echo "Info: utils/analyzer.py not found, skipping..."
curl -fsSL "$REPO_URL/utils/collection.py" -o "$INSTALL_DIR/utils/collection.py" 2>/dev/null || echo "Info: utils/collection.py not found, skipping..."
curl -fsSL "$REPO_URL/utils/detection.py" -o "$INSTALL_DIR/utils/detection.py" 2>/dev/null || echo "Info: utils/detection.py not found, skipping..."
curl -fsSL "$REPO_URL/utils/errors.py" -o "$INSTALL_DIR/utils/errors.py" 2>/dev/null || echo "Info: utils/errors.py not found, skipping..."
curl -fsSL "$REPO_URL/utils/forecast.py" -o "$INSTALL_DIR/utils/forecast.py" 2>/dev/null || echo "Info: utils/forecast.py not found, skipping..."
curl -fsSL "$REPO_URL/utils/geocoding.py" -o "$INSTALL_DIR/utils/geocoding.py" 2>/dev/null || echo "Info: utils/geocoding.py not found, skipping..."
curl -fsSL "$REPO_URL/utils/intelligence_persistence.py" -o "$INSTALL_DIR/utils/intelligence_persistence.py" 2>/dev/null || echo "Info: utils/intelligence_persistence.py not found, skipping..."
curl -fsSL "$REPO_URL/utils/translations.py" -o "$INSTALL_DIR/utils/translations.py" 2>/dev/null || echo "Info: utils/translations.py not found, skipping..."

# Download data directory structure
mkdir -p "$INSTALL_DIR/data/cache"
mkdir -p "$INSTALL_DIR/data/integration"
mkdir -p "$INSTALL_DIR/data/intelligence"

# Create virtual environment and install Python dependencies
VENV_DIR="$INSTALL_DIR/venv"
echo "Creating virtual environment..."
python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install -r "$INSTALL_DIR/requirements.txt"

# Clone the repository to build Go components
echo "Downloading and building Go components..."
TEMP_DIR=$(mktemp -d)
git clone https://github.com/redsskull/weather-intelligence-system.git "$TEMP_DIR/repo"
cd "$TEMP_DIR/repo/go-components/data-collector" && go build -o "$INSTALL_DIR/data-collector" && cd "$INSTALL_DIR"
cd "$TEMP_DIR/repo/go-components/pattern-engine" && go build -o "$INSTALL_DIR/pattern-engine" && cd "$INSTALL_DIR"

# Make binaries executable
chmod +x "$INSTALL_DIR/data-collector"
chmod +x "$INSTALL_DIR/pattern-engine"

# Cleanup
rm -rf "$TEMP_DIR"

# Create weather command
mkdir -p "$HOME/.local/bin"
cat > "$HOME/.local/bin/weather" << 'EOF'
#!/bin/bash
cd "$HOME/.weather-intel" && "$HOME/.weather-intel/venv/bin/python3" project.py "$@"
EOF
chmod +x "$HOME/.local/bin/weather"

# Create uninstall script
cat > "$HOME/.local/bin/weather-uninstall" << 'EOF'
#!/bin/bash
echo "Uninstalling Weather Intelligence System..."
rm -rf "$HOME/.weather-intel"
rm -f "$HOME/.local/bin/weather"
rm -f "$HOME/.local/bin/weather-uninstall"
echo "Uninstallation complete!"
chmod +x "$HOME/.local/bin/weather-uninstall"

# Attempt to automatically add PATH to the appropriate shell profile
SHELL_PROFILE=""

# Detect the shell and determine the appropriate profile file
if [ -n "$ZSH_VERSION" ] || [ "$SHELL" = "/bin/zsh" ]; then
    # For zsh (default on macOS), try .zprofile first, then .zshrc
    if [ -f "$HOME/.zprofile" ] || [ ! -f "$HOME/.zshrc" ]; then
        SHELL_PROFILE="$HOME/.zprofile"
    else
        SHELL_PROFILE="$HOME/.zshrc"
    fi
elif [ -n "$BASH_VERSION" ] || [ "$SHELL" = "/bin/bash" ]; then
    # For bash, try .bash_profile on macOS, .bashrc on Linux
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS uses .bash_profile by default
        if [ -f "$HOME/.bash_profile" ]; then
            SHELL_PROFILE="$HOME/.bash_profile"
        else
            SHELL_PROFILE="$HOME/.bashrc"
        fi
    else
        # Linux typically uses .bashrc
        SHELL_PROFILE="$HOME/.bashrc"
    fi
else
    # Default fallback - try to detect shell
    if [ -n "$SHELL" ]; then
        case "$SHELL" in
            */zsh)
                if [ -f "$HOME/.zprofile" ] || [ ! -f "$HOME/.zshrc" ]; then
                    SHELL_PROFILE="$HOME/.zprofile"
                else
                    SHELL_PROFILE="$HOME/.zshrc"
                fi
                ;;
            */bash)
                if [[ "$OSTYPE" == "darwin"* ]]; then
                    if [ -f "$HOME/.bash_profile" ]; then
                        SHELL_PROFILE="$HOME/.bash_profile"
                    else
                        SHELL_PROFILE="$HOME/.bashrc"
                    fi
                else
                    SHELL_PROFILE="$HOME/.bashrc"
                fi
                ;;
        esac
    fi
fi

# If we found a shell profile, add the PATH export to it if not already present
if [ -n "$SHELL_PROFILE" ]; then
    if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' "$SHELL_PROFILE" 2>/dev/null; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_PROFILE"
        echo "✅ Added PATH export to $SHELL_PROFILE"
    else
        echo "ℹ️  PATH export already exists in $SHELL_PROFILE"
    fi
else
    echo "⚠️  Could not determine shell profile, you may need to add PATH export manually"
fi

echo "✅ Done! Run: weather"
echo "🗑️  To uninstall: weather-uninstall"

# Show info about shell profile if we couldn't update it automatically
if [ -z "$SHELL_PROFILE" ]; then
    echo "🔄 If command not found, add to your shell profile:"
    echo 'export PATH="$HOME/.local/bin:$PATH"'
    
    # Detect the shell and suggest the appropriate profile file
    if [ -n "$ZSH_VERSION" ] || [ "$SHELL" = "/bin/zsh" ]; then
        echo "For zsh (default on macOS): echo 'export PATH=\\\"\\$HOME/.local/bin:\\$PATH\\\"' >> ~/.zprofile"
        echo "                         Or: echo 'export PATH=\\\"\\$HOME/.local/bin:\\$PATH\\\"' >> ~/.zshrc"
    elif [ -n "$BASH_VERSION" ] || [ "$SHELL" = "/bin/bash" ]; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            echo "For macOS with bash: echo 'export PATH=\\\"\\$HOME/.local/bin:\\$PATH\\\"' >> ~/.bash_profile"
        else
            echo "For Linux with bash: echo 'export PATH=\\\"\\$HOME/.local/bin:\\$PATH\\\"' >> ~/.bashrc"
        fi
    else
        echo "For other shells, add to your appropriate profile file"
    fi
fi
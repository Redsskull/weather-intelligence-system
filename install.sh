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

# Download utils files if they exist
mkdir -p "$INSTALL_DIR/utils"
curl -fsSL "$REPO_URL/utils/__init__.py" -o "$INSTALL_DIR/utils/__init__.py" 2>/dev/null || echo "Info: utils/__init__.py not found, skipping..."
# Download other potential utils files
curl -fsSL "$REPO_URL/utils/data_processor.py" -o "$INSTALL_DIR/utils/data_processor.py" 2>/dev/null || echo "Info: utils/data_processor.py not found, skipping..."
curl -fsSL "$REPO_URL/utils/file_handler.py" -o "$INSTALL_DIR/utils/file_handler.py" 2>/dev/null || echo "Info: utils/file_handler.py not found, skipping..."

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
EOF
chmod +x "$HOME/.local/bin/weather-uninstall"

echo "Done! Run: weather"
echo "To uninstall: weather-uninstall"
echo "If command not found, add to ~/.bashrc:"
echo 'export PATH="$HOME/.local/bin:$PATH"'

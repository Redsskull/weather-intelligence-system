#!/bin/bash
set -e

echo "Installing Weather Intelligence System..."

# Check Python and Go
command -v python3 >/dev/null || { echo "Need Python 3"; exit 1; }
command -v go >/dev/null || { echo "Need Go"; exit 1; }

# Create install location
INSTALL_DIR="$HOME/.weather-intel"
mkdir -p "$INSTALL_DIR/data/integration"

# Copy Python files
cp project.py "$INSTALL_DIR/"
cp requirements.txt "$INSTALL_DIR/"
cp -r utils "$INSTALL_DIR/"
cp -r data "$INSTALL_DIR/"

# Create virtual environment and install Python dependencies
VENV_DIR="$INSTALL_DIR/venv"
echo "Creating virtual environment..."
python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install -r "$INSTALL_DIR/requirements.txt"

# Build and copy Go binaries
cd go-components/data-collector && go build -o "$INSTALL_DIR/data-collector" && cd ../..
cd go-components/pattern-engine && go build -o "$INSTALL_DIR/pattern-engine" && cd ../..

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

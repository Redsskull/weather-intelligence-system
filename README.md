# Weather Intelligence System

A comprehensive weather data collection and analysis system.

## Installation

The Weather Intelligence System can be installed using one of the following methods:

### Quick Install (Recommended)

You can install the Weather Intelligence System directly using curl or wget:

**Using curl:**
```bash
curl -fsSL https://raw.githubusercontent.com/redsskull/weather-intelligence-system/main/install.sh | bash
```

**Using wget:**
```bash
wget -qO- https://raw.githubusercontent.com/redsskull/weather-intelligence-system/main/install.sh | bash
```

### Manual Installation

1. Clone the repository:
```bash
git clone https://github.com/redsskull/weather-intelligence-system.git
cd weather-intelligence-system
```

2. Run the installation script:
```bash
bash install.sh
```

## Safety Features

Our installation script includes several safety measures to protect your system:

1. **No Root Privileges Required**: The installer does not require sudo and installs only to user-writable directories.

2. **Safe Directory Selection**: The installer checks for user-writable directories first (`~/.local/bin`, `~/bin`) before creating any directories.

3. **Isolated Installation**: All application files are installed to `~/.local/share/weather-intelligence-system`, keeping them separate from system files.

4. **PATH Modification Only to User Directories**: The installer only adds entries to your PATH that point to directories in your home folder.

5. **Prerequisite Checks**: The installer verifies that Python, Go, and Git are installed before proceeding.

6. **Cleanup on Failure**: If the installation fails, temporary files are cleaned up automatically.

## Prerequisites

The installation requires:
- Python 3.x
- Go
- Git
- A Unix-like operating system (Linux/macOS)

## What the Installation Does

1. Clones the repository to `~/.local/share/weather-intelligence-system`
2. Builds the Go components
3. Sets up a Python virtual environment
4. Installs the `weather` and `weather-collector` binaries to `~/.local/bin` (or `~/bin` if `~/.local/bin` doesn't exist)
5. Optionally adds the installation directory to your PATH in your shell configuration

## Post-Installation

After installation, you may need to restart your terminal or run `source ~/.bashrc` (or the appropriate shell configuration file) to update your PATH.

Then you can run:
```bash
weather
```

## Uninstall

To uninstall, simply remove:
- The installation directory: `~/.local/share/weather-intelligence-system`
- The installed binaries: `~/.local/bin/weather` and `~/.local/bin/weather-collector` (or in `~/bin` if applicable)
- The PATH entry from your shell configuration file
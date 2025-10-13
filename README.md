# Weather Intelligence System

A comprehensive weather data collection and analysis system.

## Installation

The Weather Intelligence System can be installed using one of the following methods:

### Quick Install (Recommended)

You can install the Weather Intelligence System directly using curl, wget, or PowerShell:

**On Linux/macOS using curl:**
```bash
curl -fsSL https://raw.githubusercontent.com/redsskull/weather-intelligence-system/main/install.sh | bash
```

**On Linux/macOS using wget:**
```bash
wget -qO- https://raw.githubusercontent.com/redsskull/weather-intelligence-system/main/install.sh | bash
```

**On Windows using PowerShell:**
```powershell
iex (iwr https://raw.githubusercontent.com/redsskull/weather-intelligence-system/main/install.ps1 -UseBasicParsing)
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
- **On Linux/macOS:**
  - Python 3.x
  - Go
  - Git
  - A Unix-like operating system (Linux/macOS)
- **On Windows:**
  - PowerShell 5.1 or later
  - Python 3.x
  - Go
  - Git

## What the Installation Does

**On Linux/macOS:**
1. Clones the repository to `~/.local/share/weather-intelligence-system`
2. Builds the Go components
3. Sets up a Python virtual environment
4. Installs the `weather` and `weather-collector` binaries to `~/.local/bin` (or `~/bin` if `~/.local/bin` doesn't exist)
5. Optionally adds the installation directory to your PATH in your shell configuration

**On Windows:**
1. Downloads the repository to `$env:LOCALAPPDATA\weather-intelligence-system`
2. Builds the Go components
3. Sets up a Python virtual environment
4. Installs the `weather` command as a PowerShell script and batch file to `$env:LOCALAPPDATA\Programs\weather-intelligence-system`
5. Automatically adds the installation directory to your user PATH environment variable

## Post-Installation

**On Linux/macOS:**
After installation, you may need to restart your terminal or run `source ~/.bashrc` (or the appropriate shell configuration file) to update your PATH.

**On Windows:**
The installer automatically updates your user PATH environment variable. You may need to restart your PowerShell session to use the `weather` command directly.

Then you can run:
```bash
weather
```

## Uninstall

**On Linux/macOS:**
To uninstall, simply remove:
- The installation directory: `~/.local/share/weather-intelligence-system`
- The installed binaries: `~/.local/bin/weather` and `~/.local/bin/weather-collector` (or in `~/bin` if applicable)
- The PATH entry from your shell configuration file

**On Windows:**
Run the uninstall command:
```powershell
weather uninstall
```
Or manually remove:
- The installation directory: `$env:LOCALAPPDATA\weather-intelligence-system`
- The installed binaries: `$env:LOCALAPPDATA\Programs\weather-intelligence-system`
- The PATH entry from your user environment variables
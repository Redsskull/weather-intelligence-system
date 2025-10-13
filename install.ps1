# PowerShell installation script for Weather Intelligence System
# Can be run directly with: Invoke-WebRequest -Uri https://raw.githubusercontent.com/Redsskull/weather-intelligence-system/main/install.ps1 -OutFile install.ps1; .\install.ps1

# Set error handling
$ErrorActionPreference = "Stop"

Write-Host "Weather Intelligence System - One-Click Installation" -ForegroundColor Green
Write-Host "====================================================="

# Create a temporary directory to work in
$TempDir = [System.IO.Path]::GetTempPath()
$ProjectTempDir = Join-Path $TempDir "weather-intelligence-system-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
New-Item -ItemType Directory -Path $ProjectTempDir -Force
Write-Host "Using temporary directory: $ProjectTempDir"

# Detect OS
$OS = "windows"
Write-Host "Detected OS: $OS"

# Install Git if not available
if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Git..." -ForegroundColor Yellow
    try {
        # Try to use Chocolatey if available
        if (Get-Command choco -ErrorAction SilentlyContinue) {
            choco install git -y
        }
        # Or try winget if available
        elseif (Get-Command winget -ErrorAction SilentlyContinue) {
            winget install --id Git.Git -e --source winget
        }
        else {
            Write-Host "Git is not installed and could not be automatically installed." -ForegroundColor Red
            Write-Host "Please install Git and try again." -ForegroundColor Red
            exit 1
        }
    }
    catch {
        Write-Host "Failed to install Git automatically." -ForegroundColor Red
        Write-Host "Please install Git and try again." -ForegroundColor Red
        exit 1
    }
}

# Clone the repository to the temporary directory
Write-Host "Cloning Weather Intelligence System..." -ForegroundColor Yellow
Set-Location $TempDir
& git clone https://github.com/yourusername/weather-intelligence-system.git $ProjectTempDir

$ProjectRoot = $ProjectTempDir

# Check if we're in the right directory
if (!(Test-Path "$ProjectRoot\project.py")) {
    Write-Host "Error: project.py not found in $ProjectRoot" -ForegroundColor Red
    exit 1
}

# Check if Python is installed
try {
    $PythonVersion = python --version 2>$null
    if (!$PythonVersion) {
        $PythonVersion = python3 --version 2>$null
    }
    if (!$PythonVersion) {
        throw "Python not found"
    }
    Write-Host "Found Python: $PythonVersion"
}
catch {
    Write-Host "Error: Python is not installed." -ForegroundColor Red
    exit 1
}

# Check if Go is installed
try {
    $GoVersion = go version 2>$null
    if (!$GoVersion) {
        throw "Go not found"
    }
    Write-Host "Found Go: $GoVersion"
}
catch {
    Write-Host "Error: Go is not installed." -ForegroundColor Red
    exit 1
}

# Create installation directory in user's home
$InstallDir = "$env:USERPROFILE\bin"
if (!(Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir -Force
}

# Build the Go component first
Write-Host "Building Go components..." -ForegroundColor Yellow
if (Test-Path "$ProjectRoot\go-components\data-collector") {
    Set-Location "$ProjectRoot\go-components\data-collector"
    go build -o weather-collector.exe .
    Set-Location $ProjectRoot
    # Copy the binary to project root for the launcher to find
    Copy-Item "$ProjectRoot\go-components\data-collector\weather-collector.exe" "$ProjectRoot\" -ErrorAction SilentlyContinue
} else {
    Write-Host "Go components directory not found, skipping Go build" -ForegroundColor Yellow
}

# Check if virtual environment exists, if not create and set it up
$VenvPath = "$ProjectRoot\venv"
if (!(Test-Path $VenvPath)) {
    Write-Host "Setting up Python virtual environment..." -ForegroundColor Yellow
    python -m venv $VenvPath

    # Activate virtual environment and install requirements
    $ActivateScript = "$VenvPath\Scripts\Activate.ps1"
    if (Test-Path $ActivateScript) {
        & $ActivateScript
    }

    # Use the correct pip for the current environment
    python -m pip install --upgrade pip
    if (Test-Path "$ProjectRoot\requirements.txt") {
        python -m pip install -r "$ProjectRoot\requirements.txt"
        Write-Host "✓ Python dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "Error: requirements.txt not found" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
    $ActivateScript = "$VenvPath\Scripts\Activate.ps1"
    if (Test-Path $ActivateScript) {
        & $ActivateScript
    }
}

# Create a PowerShell launcher script
Write-Host "Creating 'weather.ps1' command..." -ForegroundColor Yellow
$LauncherPath = "$InstallDir\weather.ps1"
$LauncherContent = @"
# Weather Intelligence System PowerShell launcher
[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = `$true)]
    [String[]]`$WeatherArgs
)

# Get the project root directory
`$ProjectRoot = Split-Path -Parent `$MyInvocation.MyCommand.Path
`$ProjectRoot = Join-Path `$ProjectRoot "..\weather-intelligence-system"

# First try to find in temp directory structure (for first-run)
`$TempProjectPath = `$env:TEMP | Get-ChildItem -Directory -Filter "weather-intelligence-system-*" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (`$TempProjectPath) {
    `$TempProjectPath = Join-Path `$TempProjectPath.FullName "weather-intelligence-system"
    if (Test-Path "`$TempProjectPath\project.py") {
        `$ProjectRoot = `$TempProjectPath
    }
}

# Then try relative to the installation script location
if (!(Test-Path "`$ProjectRoot\project.py")) {
    `$ProjectRoot = "`$env:USERPROFILE\projects\weather-intelligence-system"
}

# Second, try in the same directory as the script
if (!(Test-Path "`$ProjectRoot\project.py")) {
    `$ProjectRoot = Split-Path -Parent `$MyInvocation.MyCommand.Path
}

if (!(Test-Path "`$ProjectRoot\project.py")) {
    Write-Host "Error: Weather Intelligence System not found!"
    Write-Host "Expected location: `$ProjectRoot"
    exit 1
}

# Change to project directory
Set-Location "`$ProjectRoot"

# Activate Python virtual environment and run the program
`$VenvActivate = Join-Path "`$ProjectRoot" "venv\Scripts\Activate.ps1"
if (Test-Path `$VenvActivate) {
    & `$VenvActivate
}

# Run the Python script with any arguments passed to this script
python project.py @`$WeatherArgs
"@

$LauncherContent | Out-File -FilePath $LauncherPath -Encoding UTF8

# Also create a batch file for cmd compatibility
$BatchPath = "$InstallDir\weather.bat"
$BatchContent = "@echo off
setlocal

REM Get the directory where this script is located
set SCRIPT_DIR=%%~dp0

REM Try to find the project directory
set PROJECT_ROOT=%%SCRIPT_DIR%%..\weather-intelligence-system

REM First try to find in temp directory structure (for first-run)
for /f \"delims=\" %%i in ('dir \"%%TEMP%%\weather-intelligence-system-*\" /ad /b /o:-d 2^>nul') do (
    if exist \"%%TEMP%%\%%i\weather-intelligence-system\project.py\" (
        set PROJECT_ROOT=%%TEMP%%\%%i\weather-intelligence-system
        goto :found
    )
)

REM Then try relative to the installation script location
if not exist \"%%PROJECT_ROOT%%\project.py\" (
    set PROJECT_ROOT=%%USERPROFILE%%\projects\weather-intelligence-system
)

REM Second, try in the same directory as the script
if not exist \"%%PROJECT_ROOT%%\project.py\" (
    set PROJECT_ROOT=%%SCRIPT_DIR%%
)

if not exist \"%%PROJECT_ROOT%%\project.py\" (
    echo Error: Weather Intelligence System not found!
    echo Expected location: %%PROJECT_ROOT%%
    exit /b 1
)

:found
REM Change to project directory
cd /d \"%%PROJECT_ROOT%%\"

REM Activate Python virtual environment and run the program
if exist \"venv\Scripts\activate.bat\" (
    call venv\Scripts\activate.bat
)

python project.py %%*
"

$BatchContent | Out-File -FilePath $BatchPath -Encoding ASCII

# Check if $InstallDir is in PATH and add it automatically if not
$PathFolders = $env:PATH -split ';'
$IsInPath = $PathFolders -contains $InstallDir

if (!$IsInPath) {
    Write-Host "Adding $InstallDir to your PATH automatically..." -ForegroundColor Yellow

    # Add to PATH environment variable for current session
    $env:PATH += ";$InstallDir"

    # Add to user PATH environment variable permanently
    [System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ";$InstallDir", 'User')

    Write-Host "✓ PATH updated automatically!" -ForegroundColor Green
    Write-Host "You can now run 'weather' from anywhere in your terminal." -ForegroundColor Green
} else {
    Write-Host "✓ 'weather' command installed successfully!" -ForegroundColor Green
    Write-Host "You can now run 'weather' from anywhere in your terminal." -ForegroundColor Green
}

Write-Host ""
Write-Host "🎉 Installation complete!" -ForegroundColor Green
Write-Host "Run 'weather' to start using Weather Intelligence System!" -ForegroundColor Green

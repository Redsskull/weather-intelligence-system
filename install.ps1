# Weather Intelligence System - Windows Installer
# PowerShell script for installing on Windows systems
# Version 2.0 - Web-compatible installer (works with iwr | iex)

#Requires -Version 5.1

# ============================================================================
# ERROR HANDLING & COMPATIBILITY
# ============================================================================

$ErrorActionPreference = "Continue"
$DebugMode = $true  # Set to $false to disable verbose output

# Detect if running via iwr | iex (web execution)
$IsWebExecution = $MyInvocation.MyCommand.Path -eq $null

function Write-Step {
    param($Message, $Color = "Cyan")
    Write-Host "`n$Message" -ForegroundColor $Color
}

function Write-Success {
    param($Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Info {
    param($Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Blue
}

function Write-Warning-Custom {
    param($Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Error-Custom {
    param($Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Debug-Custom {
    param($Message)
    if ($DebugMode) {
        Write-Host "[DEBUG] $Message" -ForegroundColor Gray
    }
}

function Pause-IfInteractive {
    # Only pause if NOT running via iwr | iex
    if (-not $IsWebExecution) {
        try {
            Write-Host "`nPress any key to continue..." -ForegroundColor Yellow
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        } catch {
            # If ReadKey fails, just use Read-Host
            Read-Host "Press Enter to continue"
        }
    } else {
        Write-Host "`n(Running in web mode - continuing automatically)" -ForegroundColor DarkGray
        Start-Sleep -Seconds 2
    }
}

function Exit-With-Message {
    param($Message, $IsError = $true)

    if ($IsError) {
        Write-Error-Custom $Message
    } else {
        Write-Success $Message
    }

    Write-Host "`n========================================" -ForegroundColor DarkGray
    Pause-IfInteractive

    if ($IsError) {
        throw $Message  # Use throw instead of exit for iwr | iex
    }
}

# Catch all unhandled errors
trap {
    Write-Error-Custom "Unexpected error occurred: $_"
    Write-Debug-Custom $_.ScriptStackTrace
    Pause-IfInteractive
    throw
}

# ============================================================================
# BANNER
# ============================================================================

Clear-Host
Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🌤️  Weather Intelligence System - Windows Installer  ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

if ($IsWebExecution) {
    Write-Info "Running in web-install mode"
    Write-Debug-Custom "Executed via: iwr | iex"
}

# Check if running as administrator
if (([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning-Custom "Running as Administrator. This is not recommended for user-level installation."

    if (-not $IsWebExecution) {
        $continue = Read-Host "Continue anyway? (y/N)"
        if ($continue -notmatch '^[Yy]$') {
            Exit-With-Message "Installation cancelled by user" $false
        }
    } else {
        Write-Warning-Custom "Continuing with admin privileges (web install mode)"
        Start-Sleep -Seconds 2
    }
}

# ============================================================================
# PREREQUISITE CHECKING
# ============================================================================

Write-Step "🔍 Step 1/6: Checking prerequisites"

# -----------------------------
# Check Python
# -----------------------------
Write-Info "Checking for Python..."
Write-Debug-Custom "Looking for python3 and python commands"

$pythonCmd = $null
$pythonVersion = $null
$pythonPath = $null

# Try python3 first
$py3Test = Get-Command python3 -ErrorAction SilentlyContinue
if ($py3Test) {
    Write-Debug-Custom "Found python3 at: $($py3Test.Source)"
    try {
        $versionOutput = & python3 --version 2>&1 | Out-String
        Write-Debug-Custom "Version output: $versionOutput"

        if ($versionOutput -match 'Python (\d+)\.(\d+)\.(\d+)') {
            $pythonCmd = "python3"
            $pythonVersion = "$($matches[1]).$($matches[2])"
            $pythonPath = $py3Test.Source
        }
    } catch {
        Write-Debug-Custom "Error checking python3 version: $_"
    }
}

# Try python if python3 didn't work
if (-not $pythonCmd) {
    $pyTest = Get-Command python -ErrorAction SilentlyContinue
    if ($pyTest) {
        Write-Debug-Custom "Found python at: $($pyTest.Source)"
        try {
            $versionOutput = & python --version 2>&1 | Out-String
            Write-Debug-Custom "Version output: $versionOutput"

            if ($versionOutput -match 'Python (\d+)\.(\d+)\.(\d+)') {
                $pythonCmd = "python"
                $pythonVersion = "$($matches[1]).$($matches[2])"
                $pythonPath = $pyTest.Source
            }
        } catch {
            Write-Debug-Custom "Error checking python version: $_"
        }
    }
}

# If Python not found, provide installation instructions
if (-not $pythonCmd) {
    Write-Error-Custom "Python not found on this system"
    Write-Host ""
    Write-Host "Python 3.8 or higher is required." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To install Python:" -ForegroundColor Cyan
    Write-Host "  Option 1 - Using winget (Windows 10/11):" -ForegroundColor White
    Write-Host "    winget install Python.Python.3.12" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Option 2 - Manual installation:" -ForegroundColor White
    Write-Host "    1. Visit: https://python.org/downloads/" -ForegroundColor Yellow
    Write-Host "    2. Download Python 3.12 or higher" -ForegroundColor Yellow
    Write-Host "    3. Run installer and CHECK 'Add Python to PATH'" -ForegroundColor Yellow
    Write-Host "    4. Restart PowerShell" -ForegroundColor Yellow
    Write-Host "    5. Run this installer again" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "After installing Python, run this command again:" -ForegroundColor Cyan
    Write-Host "  iwr https://raw.githubusercontent.com/redsskull/weather-intelligence-system/main/install.ps1 -UseBasicParsing | iex" -ForegroundColor Yellow
    Write-Host ""

    Exit-With-Message "Python installation required" $true
}

# Verify Python version
$versionParts = $pythonVersion -split '\.'
$major = [int]$versionParts[0]
$minor = [int]$versionParts[1]

if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
    Exit-With-Message "Python version $pythonVersion is too old. Requires Python 3.8+" $true
}

Write-Success "Python $pythonVersion found at: $pythonPath"

# -----------------------------
# Check Git
# -----------------------------
Write-Info "Checking for Git..."
$gitCmd = Get-Command git -ErrorAction SilentlyContinue

if (-not $gitCmd) {
    Write-Error-Custom "Git is not installed"
    Write-Host ""
    Write-Host "To install Git:" -ForegroundColor Cyan
    Write-Host "  Option 1 - Using winget:" -ForegroundColor White
    Write-Host "    winget install Git.Git" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Option 2 - Manual installation:" -ForegroundColor White
    Write-Host "    1. Visit: https://git-scm.com/download/win" -ForegroundColor Yellow
    Write-Host "    2. Download and install Git for Windows" -ForegroundColor Yellow
    Write-Host "    3. Restart PowerShell" -ForegroundColor Yellow
    Write-Host "    4. Run this installer again" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "After installing Git, run this command again:" -ForegroundColor Cyan
    Write-Host "  iwr https://raw.githubusercontent.com/redsskull/weather-intelligence-system/main/install.ps1 -UseBasicParsing | iex" -ForegroundColor Yellow
    Write-Host ""

    Exit-With-Message "Git installation required" $true
}

Write-Success "Git found at: $($gitCmd.Source)"

# -----------------------------
# Check Go (optional)
# -----------------------------
Write-Info "Checking for Go..."
$goCmd = Get-Command go -ErrorAction SilentlyContinue

if (-not $goCmd) {
    Write-Warning-Custom "Go is not installed (optional component)"
    Write-Host ""
    Write-Host "Go is used for the data collector component." -ForegroundColor Yellow
    Write-Host "The system will work without it, but with limited functionality." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To install Go (optional):" -ForegroundColor Cyan
    Write-Host "  winget install GoLang.Go" -ForegroundColor Yellow
    Write-Host ""
    Write-Info "Continuing installation without Go..."
    Start-Sleep -Seconds 2
} else {
    Write-Success "Go found at: $($goCmd.Source)"
}

# ============================================================================
# DIRECTORY SETUP
# ============================================================================

Write-Step "📁 Step 2/6: Setting up directories"

$installDir = "$env:LOCALAPPDATA\Programs\weather-intelligence-system"
$projectRoot = "$env:LOCALAPPDATA\weather-intelligence-system"

Write-Debug-Custom "Install directory: $installDir"
Write-Debug-Custom "Project root: $projectRoot"

# Create directories
try {
    if (-not (Test-Path $installDir)) {
        New-Item -ItemType Directory -Path $installDir -Force | Out-Null
        Write-Success "Created: $installDir"
    } else {
        Write-Info "Directory exists: $installDir"
    }

    if (-not (Test-Path $projectRoot)) {
        New-Item -ItemType Directory -Path $projectRoot -Force | Out-Null
        Write-Success "Created: $projectRoot"
    } else {
        Write-Info "Directory exists: $projectRoot"
    }
} catch {
    Exit-With-Message "Failed to create directories: $_" $true
}

# Clean existing installation
if (Test-Path "$projectRoot\*") {
    Write-Info "Cleaning existing installation..."
    try {
        Remove-Item "$projectRoot\*" -Recurse -Force -ErrorAction Stop
        Write-Success "Cleaned project directory"
    } catch {
        Write-Warning-Custom "Could not clean directory completely: $_"
    }
}

# ============================================================================
# CLONE REPOSITORY
# ============================================================================

Write-Step "📥 Step 3/6: Downloading project files"

$repoUrl = "https://github.com/redsskull/weather-intelligence-system.git"
$tempCloneDir = "$env:TEMP\weather-intelligence-system-clone-$(Get-Random)"

Write-Debug-Custom "Cloning to: $tempCloneDir"
Write-Info "Cloning repository (this may take a minute)..."

try {
    $originalLocation = Get-Location
    Set-Location $env:TEMP

    # Clone repository
    Write-Debug-Custom "Running: git clone $repoUrl $tempCloneDir"
    $gitOutput = git clone $repoUrl $tempCloneDir 2>&1
    Write-Debug-Custom "Git output: $gitOutput"

    if ($LASTEXITCODE -ne 0) {
        throw "Git clone failed with exit code $LASTEXITCODE. Output: $gitOutput"
    }

    if (-not (Test-Path $tempCloneDir)) {
        throw "Clone directory not created at $tempCloneDir"
    }

    Write-Success "Repository cloned successfully"

    # Copy files to project root
    Write-Info "Copying files to installation directory..."
    Copy-Item "$tempCloneDir\*" $projectRoot -Recurse -Force
    Write-Success "Files copied to $projectRoot"

    # Cleanup temp directory
    Remove-Item $tempCloneDir -Recurse -Force -ErrorAction SilentlyContinue

    Set-Location $originalLocation

} catch {
    Set-Location $originalLocation -ErrorAction SilentlyContinue
    Exit-With-Message "Failed to clone repository: $_" $true
}

# Verify critical files exist
$criticalFiles = @("project.py", "requirements.txt")
foreach ($file in $criticalFiles) {
    if (-not (Test-Path "$projectRoot\$file")) {
        Write-Warning-Custom "Expected file not found: $file"
    } else {
        Write-Debug-Custom "Verified: $file exists"
    }
}

# ============================================================================
# BUILD GO COMPONENT
# ============================================================================

Write-Step "🔨 Step 4/6: Building Go component"

if ($goCmd) {
    $goDir = "$projectRoot\go-components\data-collector"

    if (Test-Path $goDir) {
        try {
            Write-Info "Building Go data collector..."
            $originalLocation = Get-Location
            Set-Location $goDir

            Write-Debug-Custom "Running: go build -o weather-collector.exe ."
            $buildOutput = go build -o weather-collector.exe . 2>&1
            Write-Debug-Custom "Build output: $buildOutput"

            if ($LASTEXITCODE -eq 0 -and (Test-Path "weather-collector.exe")) {
                Copy-Item "weather-collector.exe" $installDir -Force
                Write-Success "Go component built and installed"
            } else {
                Write-Warning-Custom "Go build failed (exit code: $LASTEXITCODE)"
                Write-Debug-Custom "Build output: $buildOutput"
                Write-Info "Continuing without Go component..."
            }

            Set-Location $originalLocation
        } catch {
            Set-Location $originalLocation -ErrorAction SilentlyContinue
            Write-Warning-Custom "Error building Go component: $_"
            Write-Info "Continuing installation..."
        }
    } else {
        Write-Info "Go components directory not found at: $goDir"
        Write-Info "Skipping Go component build"
    }
} else {
    Write-Info "Go not available, skipping Go component build"
}

# ============================================================================
# PYTHON VIRTUAL ENVIRONMENT
# ============================================================================

Write-Step "🐍 Step 5/6: Setting up Python environment"

$originalLocation = Get-Location
Set-Location $projectRoot

# Create virtual environment
Write-Info "Creating Python virtual environment..."
$venvPath = "$projectRoot\venv"

try {
    Write-Debug-Custom "Running: $pythonCmd -m venv $venvPath"
    $venvOutput = & $pythonCmd -m venv $venvPath 2>&1
    Write-Debug-Custom "Venv output: $venvOutput"

    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create venv with exit code $LASTEXITCODE. Output: $venvOutput"
    }

    if (-not (Test-Path "$venvPath\Scripts\python.exe")) {
        throw "Virtual environment created but python.exe not found at $venvPath\Scripts\python.exe"
    }

    Write-Success "Virtual environment created at: $venvPath"
} catch {
    Set-Location $originalLocation
    Exit-With-Message "Failed to create Python virtual environment: $_" $true
}

# Install dependencies
$requirementsFile = "$projectRoot\requirements.txt"

if (Test-Path $requirementsFile) {
    Write-Info "Installing Python dependencies (this may take a few minutes)..."

    try {
        $pipExe = "$venvPath\Scripts\pip.exe"

        if (-not (Test-Path $pipExe)) {
            throw "pip.exe not found at $pipExe"
        }

        # Upgrade pip first
        Write-Debug-Custom "Upgrading pip..."
        & $pipExe install --upgrade pip --quiet 2>&1 | Out-Null

        # Install requirements
        Write-Debug-Custom "Installing from requirements.txt..."
        $pipOutput = & $pipExe install -r $requirementsFile 2>&1

        if ($LASTEXITCODE -eq 0) {
            Write-Success "Python dependencies installed successfully"
        } else {
            Write-Warning-Custom "Some pip packages may have failed to install (exit code: $LASTEXITCODE)"
            Write-Debug-Custom "Pip output: $pipOutput"
            Write-Info "Attempting to continue..."
        }
    } catch {
        Set-Location $originalLocation
        Exit-With-Message "Failed to install Python dependencies: $_" $true
    }
} else {
    Write-Warning-Custom "requirements.txt not found at: $requirementsFile"
    Write-Info "Continuing anyway..."
}

Set-Location $originalLocation

# ============================================================================
# CREATE LAUNCHER SCRIPTS
# ============================================================================

Write-Step "🚀 Step 6/6: Creating launcher commands"

# Create PowerShell script
$weatherScriptPath = "$installDir\weather.ps1"
$weatherScriptContent = @"
# Weather Intelligence System Launcher
# Auto-generated by installer

`$ErrorActionPreference = "Stop"
`$projectRoot = "$projectRoot"

if (-not (Test-Path "`$projectRoot\project.py")) {
    Write-Host "Error: Weather Intelligence System not found!" -ForegroundColor Red
    Write-Host "Expected at: `$projectRoot" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Try reinstalling:" -ForegroundColor Cyan
    Write-Host "  iwr https://raw.githubusercontent.com/redsskull/weather-intelligence-system/main/install.ps1 -UseBasicParsing | iex" -ForegroundColor Yellow
    exit 1
}

Set-Location `$projectRoot

`$pythonExe = "`$projectRoot\venv\Scripts\python.exe"
if (-not (Test-Path `$pythonExe)) {
    Write-Host "Error: Python virtual environment not found!" -ForegroundColor Red
    Write-Host "Try reinstalling the system." -ForegroundColor Yellow
    exit 1
}

& `$pythonExe project.py `$args
"@

try {
    Set-Content -Path $weatherScriptPath -Value $weatherScriptContent -ErrorAction Stop
    Write-Success "Created PowerShell launcher at: $weatherScriptPath"
} catch {
    Exit-With-Message "Failed to create launcher script: $_" $true
}

# Create batch file for CMD
$batchScriptPath = "$installDir\weather.bat"
$batchContent = @"
@echo off
powershell.exe -ExecutionPolicy Bypass -File "$weatherScriptPath" %*
"@

try {
    Set-Content -Path $batchScriptPath -Value $batchContent -ErrorAction Stop
    Write-Success "Created batch launcher (for CMD)"
} catch {
    Write-Warning-Custom "Failed to create batch file: $_"
}

# Create uninstaller
$uninstallScriptPath = "$installDir\uninstall.ps1"
$uninstallContent = @"
# Weather Intelligence System - Uninstaller

Write-Host ""
Write-Host "Weather Intelligence System - Uninstaller" -ForegroundColor Red
Write-Host "=========================================="
Write-Host ""

Write-Host "This will remove:" -ForegroundColor Yellow
Write-Host "  - $projectRoot" -ForegroundColor White
Write-Host "  - $installDir" -ForegroundColor White
Write-Host ""

`$confirm = Read-Host "Continue? (y/N)"
if (`$confirm -notmatch '^[Yy]$') {
    Write-Host "Cancelled." -ForegroundColor Blue
    exit 0
}

Write-Host ""
Write-Host "Removing files..." -ForegroundColor Yellow

if (Test-Path "$projectRoot") {
    Remove-Item "$projectRoot" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "Removed: $projectRoot" -ForegroundColor Green
}

if (Test-Path "$installDir") {
    Remove-Item "$installDir" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "Removed: $installDir" -ForegroundColor Green
}

Write-Host ""
Write-Host "Uninstallation complete!" -ForegroundColor Green
Write-Host ""
Read-Host "Press Enter to exit"
"@

try {
    Set-Content -Path $uninstallScriptPath -Value $uninstallContent -ErrorAction Stop
    Write-Success "Created uninstaller"
} catch {
    Write-Warning-Custom "Failed to create uninstaller: $_"
}

# Add to PATH
Write-Info "Adding to system PATH..."
$currentPath = [System.Environment]::GetEnvironmentVariable("Path", "User")

if ($currentPath -notlike "*$installDir*") {
    try {
        $newPath = "$currentPath;$installDir"
        [System.Environment]::SetEnvironmentVariable("Path", $newPath, "User")
        $env:Path += ";$installDir"
        Write-Success "Added to PATH: $installDir"
    } catch {
        Write-Warning-Custom "Could not add to PATH: $_"
        Write-Info "You can manually add this directory to PATH later"
    }
} else {
    Write-Info "Already in PATH"
}

# Add PowerShell function to profile (if not web execution)
if (-not $IsWebExecution) {
    Write-Host ""
    $addToProfile = Read-Host "Add 'weather' command to PowerShell profile? (Recommended) (Y/n)"
    $shouldAddProfile = $addToProfile -notmatch '^[Nn]$'
} else {
    Write-Info "Adding 'weather' command to PowerShell profile..."
    $shouldAddProfile = $true
}

if ($shouldAddProfile) {
    try {
        $profilePath = $PROFILE.CurrentUserAllHosts

        if (-not (Test-Path $profilePath)) {
            $profileDir = Split-Path $profilePath -Parent
            if (-not (Test-Path $profileDir)) {
                New-Item -Path $profileDir -ItemType Directory -Force | Out-Null
            }
            New-Item -Path $profilePath -Type File -Force | Out-Null
        }

        $functionDef = @"

# Weather Intelligence System
function weather {
    & "$weatherScriptPath" @args
}
"@

        $profileContent = Get-Content $profilePath -Raw -ErrorAction SilentlyContinue
        if ($profileContent -notlike "*function weather*") {
            Add-Content -Path $profilePath -Value $functionDef
            Write-Success "Added 'weather' function to PowerShell profile"
        } else {
            Write-Info "'weather' function already in profile"
        }
    } catch {
        Write-Warning-Custom "Could not update PowerShell profile: $_"
        Write-Info "You can still use: weather.bat"
    }
}

# ============================================================================
# INSTALLATION COMPLETE
# ============================================================================

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  🎉 Installation completed successfully!          ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

Write-Host "📝 How to use:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Close and reopen PowerShell, then type:" -ForegroundColor White
Write-Host "    weather" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Or use immediately:" -ForegroundColor White
Write-Host "    weather.bat" -ForegroundColor Yellow
Write-Host ""

Write-Host "📂 Installed to:" -ForegroundColor Cyan
Write-Host "    $projectRoot" -ForegroundColor White
Write-Host ""

Write-Host "🗑️  To uninstall:" -ForegroundColor Cyan
Write-Host "    powershell $uninstallScriptPath" -ForegroundColor Yellow
Write-Host ""

Write-Host "⚠️  IMPORTANT:" -ForegroundColor Yellow
Write-Host "    Open a NEW PowerShell window to use the 'weather' command" -ForegroundColor White
Write-Host ""

Pause-IfInteractive

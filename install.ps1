# Weather Intelligence System - Windows Installer
# PowerShell script for installing on Windows systems

#Requires -Version 5.1

Write-Host "🌤️  Weather Intelligence System - Windows Installer" -ForegroundColor Green
Write-Host "==================================================" 
Write-Host ""

# Check if running as administrator (not recommended for this script)
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "✅ Running as regular user (recommended)" -ForegroundColor Green
}
else {
    Write-Host "⚠️  Running as Administrator. This is not recommended." -ForegroundColor Yellow
    $continue = Read-Host "Continue anyway? (y/N)"
    if ($continue -notmatch '^[Yy]$') {
        exit 0
    }
}

Write-Host "`n🔍 Checking prerequisites..." -ForegroundColor Blue

# Check for Python
Write-Host "🔍 Checking for Python..." -ForegroundColor Blue

$pythonCmd = $null
$pythonVersion = $null

# Try to find Python
$py3 = Get-Command python3 -ErrorAction SilentlyContinue
$py = Get-Command python -ErrorAction SilentlyContinue

if ($py3) {
    $pythonCmd = "python3"
    $pythonVersionOutput = & python3 --version 2>&1
    if ($pythonVersionOutput -match 'Python (\d+)\.(\d+)') {
        $major = $matches[1]
        $minor = $matches[2]
        $pythonVersion = "$major.$minor"
    }
}
elseif ($py) {
    $pythonCmd = "python"
    $pythonVersionOutput = & python --version 2>&1
    if ($pythonVersionOutput -match 'Python (\d+)\.(\d+)') {
        $major = $matches[1]
        $minor = $matches[2]
        $pythonVersion = "$major.$minor"
    }
}

# If no Python found, offer to install
if (-not $pythonCmd -or -not $pythonVersion) {
    Write-Host "🐍 Python not found. We can install it for you." -ForegroundColor Yellow
    
    $installPython = Read-Host "Would you like to install Python? (y/N)"
    if ($installPython -match '^[Yy]$') {
        # Try winget first (Windows 10/11)
        $winget = Get-Command winget -ErrorAction SilentlyContinue
        if ($winget) {
            Write-Host "Installing Python via winget..." -ForegroundColor Yellow
            winget install --id Python.Python.3 -e
        }
        else {
            # Try Chocolatey
            $choco = Get-Command choco -ErrorAction SilentlyContinue
            if ($choco) {
                Write-Host "Installing Python via Chocolatey..." -ForegroundColor Yellow
                choco install python -y
            }
            else {
                Write-Host "❌ No package manager found (winget or choco)" -ForegroundColor Red
                Write-Host "Please install Python 3.8+ manually from https://python.org and run this script again" -ForegroundColor Yellow
                exit 1
            }
        }
        
        # Refresh environment to find the newly installed Python
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        # Try to find Python again after installation
        $py3 = Get-Command python3 -ErrorAction SilentlyContinue
        $py = Get-Command python -ErrorAction SilentlyContinue
        
        if ($py3) {
            $pythonCmd = "python3"
            $pythonVersionOutput = & python3 --version 2>&1
            if ($pythonVersionOutput -match 'Python (\d+)\.(\d+)') {
                $major = $matches[1]
                $minor = $matches[2]
                $pythonVersion = "$major.$minor"
            }
        }
        elseif ($py) {
            $pythonCmd = "python"
            $pythonVersionOutput = & python --version 2>&1
            if ($pythonVersionOutput -match 'Python (\d+)\.(\d+)') {
                $major = $matches[1]
                $minor = $matches[2]
                $pythonVersion = "$major.$minor"
            }
        }
        
        if ($pythonCmd -and $pythonVersion) {
            Write-Host "✅ Successfully installed Python $pythonVersion" -ForegroundColor Green
        }
        else {
            Write-Host "❌ Failed to install Python or couldn't find it" -ForegroundColor Red
            exit 1
        }
    }
    else {
        Write-Host "❌ Python is required to run this installer" -ForegroundColor Red
        Write-Host "Please install Python 3.8+ and run this script again" -ForegroundColor Yellow
        exit 1
    }
}

# Check Python version
if ($pythonVersion) {
    $versionParts = $pythonVersion -split '\.'
    $major = [int]$versionParts[0]
    $minor = [int]$versionParts[1]
    
    if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
        Write-Host "❌ Python version $pythonVersion is too old. This program requires Python 3.8 or higher." -ForegroundColor Red
        Write-Host "Please install Python 3.8+ and run this script again" -ForegroundColor Yellow
        exit 1
    }
    else {
        Write-Host "✅ Python $pythonVersion found and meets requirements" -ForegroundColor Green
    }
}

# Check for Git
Write-Host "🔍 Checking for Git..." -ForegroundColor Blue
$gitCmd = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitCmd) {
    Write-Host "❌ Git is not installed" -ForegroundColor Red
    Write-Host "Please install Git for Windows (https://git-scm.com/download/win) and run this script again" -ForegroundColor Yellow
    exit 1
}
else {
    Write-Host "✅ Git found" -ForegroundColor Green
}

# Check for Go
Write-Host "🔍 Checking for Go..." -ForegroundColor Blue
$goCmd = Get-Command go -ErrorAction SilentlyContinue
if (-not $goCmd) {
    Write-Host "❌ Go is not installed" -ForegroundColor Red
    $installGo = Read-Host "Would you like to install Go? (y/N)"
    if ($installGo -match '^[Yy]$') {
        # Try winget first
        $winget = Get-Command winget -ErrorAction SilentlyContinue
        if ($winget) {
            Write-Host "Installing Go via winget..." -ForegroundColor Yellow
            winget install --id GoLang.Go -e
        }
        else {
            # Try Chocolatey
            $choco = Get-Command choco -ErrorAction SilentlyContinue
            if ($choco) {
                Write-Host "Installing Go via Chocolatey..." -ForegroundColor Yellow
                choco install golang -y
            }
            else {
                Write-Host "❌ No package manager found (winget or choco)" -ForegroundColor Red
                Write-Host "Please install Go manually from https://golang.org/dl/ and run this script again" -ForegroundColor Yellow
                exit 1
            }
        }
        
        # Refresh environment
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        # Check for Go again
        $goCmd = Get-Command go -ErrorAction SilentlyContinue
        if ($goCmd) {
            Write-Host "✅ Go installed successfully" -ForegroundColor Green
        }
        else {
            Write-Host "❌ Failed to install Go" -ForegroundColor Red
            exit 1
        }
    }
    else {
        Write-Host "❌ Go is required to build the application" -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Host "✅ Go found" -ForegroundColor Green
}

# Determine installation directory
Write-Host "`n📁 Determining installation directory..." -ForegroundColor Blue
$installDir = "$env:LOCALAPPDATA\Programs\weather-intelligence-system"
$projectRoot = "$env:LOCALAPPDATA\weather-intelligence-system"

if (-not (Test-Path $installDir)) {
    New-Item -ItemType Directory -Path $installDir -Force | Out-Null
    Write-Host "✅ Created installation directory: $installDir" -ForegroundColor Green
}

if (-not (Test-Path $projectRoot)) {
    New-Item -ItemType Directory -Path $projectRoot -Force | Out-Null
    Write-Host "✅ Created project directory: $projectRoot" -ForegroundColor Green
}

# Clean up any existing installation
if (Test-Path $projectRoot) {
    Write-Host "🗑️  Removing existing installation..." -ForegroundColor Yellow
    Remove-Item "$projectRoot\*" -Recurse -Force
}

# Clone the repository
Write-Host "`n📥 Cloning repository..." -ForegroundColor Blue
Set-Location $env:TEMP
$repoDir = "$env:TEMP\weather-intelligence-system-clone"
if (Test-Path $repoDir) {
    Remove-Item $repoDir -Recurse -Force
}
git clone https://github.com/redsskull/weather-intelligence-system.git $repoDir

# Copy project files to project root
Copy-Item "$repoDir\*" $projectRoot -Recurse -Force
Write-Host "✅ Repository cloned and files copied" -ForegroundColor Green

# Build Go component if Go is available
Write-Host "`n🔨 Building Go data collector..." -ForegroundColor Yellow
$goDir = "$projectRoot\go-components\data-collector"
if (Test-Path $goDir) {
    Set-Location $goDir
    go build -o weather-collector.exe .
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Go component built successfully" -ForegroundColor Green
        # Copy to install directory
        Copy-Item "weather-collector.exe" $installDir
    }
    else {
        Write-Host "⚠️  Failed to build Go component, proceeding anyway" -ForegroundColor Yellow
    }
}
else {
    Write-Host "⚠️  Go components directory not found" -ForegroundColor Yellow
}

# Setup Python virtual environment
Write-Host "`n🐍 Setting up Python virtual environment..." -ForegroundColor Yellow
$venvPath = "$projectRoot\venv"
& $pythonCmd -m venv $venvPath
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
}
else {
    Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
    exit 1
}

# Activate virtual environment and install dependencies
$activateScript = "$venvPath\Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    & $activateScript
    Write-Host "✅ Virtual environment activated" -ForegroundColor Green
}
else {
    Write-Host "❌ Virtual environment activation script not found" -ForegroundColor Red
    exit 1
}

$requirementsFile = "$projectRoot\requirements.txt"
if (Test-Path $requirementsFile) {
    Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
    pip install --upgrade pip
    pip install -r $requirementsFile
    Write-Host "✅ Python dependencies installed" -ForegroundColor Green
}
else {
    Write-Host "⚠️  requirements.txt not found, continuing..." -ForegroundColor Yellow
}

# Create PowerShell script for weather command
Write-Host "`n🚀 Creating weather command..." -ForegroundColor Yellow
$weatherScriptPath = "$installDir\weather.ps1"
$weatherScriptContent = @"
# Weather Intelligence System Command
# This script is automatically generated by the installer

`$projectRoot = "$projectRoot"

if (-not (Test-Path "`$projectRoot\project.py")) {
    Write-Host "❌ Error: Weather Intelligence System not found!" -ForegroundColor Red
    Write-Host "Expected location: `$projectRoot"
    exit 1
}

Set-Location `$projectRoot

# Activate Python virtual environment and run the program
`$venvActivate = "`$projectRoot\venv\Scripts\Activate.ps1"
if (Test-Path `$venvActivate) {
    & `$venvActivate
}
else {
    Write-Host "❌ Error: Python virtual environment not found in `$projectRoot!" -ForegroundColor Red
    exit 1
}

`$pythonExe = "`$projectRoot\venv\Scripts\python.exe"
if (Test-Path `$pythonExe) {
    & `$pythonExe project.py `$args
}
else {
    # Fallback to global python
    & $pythonCmd project.py `$args
}
"@

Set-Content -Path $weatherScriptPath -Value $weatherScriptContent
Write-Host "✅ Weather PowerShell script created" -ForegroundColor Green

# Create uninstall script
Write-Host "`n🗑️  Creating uninstall script..." -ForegroundColor Yellow
$uninstallScriptPath = "$installDir\weather-uninstall.ps1"
$uninstallScriptContent = @"
# Weather Intelligence System - Uninstaller
# Removes all installed components of the Weather Intelligence System

Write-Host "🌤️  Weather Intelligence System - Uninstaller" -ForegroundColor Green
Write-Host "=================================================="
Write-Host ""

$confirmation = Read-Host "⚠️  Warning: This will completely remove the Weather Intelligence System. Continue? (y/N)"
if ($confirmation -notmatch '^[Yy]$') {
    Write-Host "Operation cancelled." -ForegroundColor Blue
    exit 0
}

`$projectRoot = "$projectRoot"
`$installDir = "$installDir"

Write-Host "`n🗑️  Removing installed files..." -ForegroundColor Blue

# Remove project directory
if (Test-Path `$projectRoot) {
    Remove-Item `$projectRoot -Recurse -Force
    Write-Host "✅ Removed project directory: `$projectRoot" -ForegroundColor Green
}

# Remove install directory
if (Test-Path `$installDir) {
    Remove-Item `$installDir -Recurse -Force
    Write-Host "✅ Removed install directory: `$installDir" -ForegroundColor Green
}

Write-Host "`n🎉 Uninstallation completed successfully!" -ForegroundColor Green
Write-Host "`n💡 You may need to restart your PowerShell session for PATH changes to take effect." -ForegroundColor Yellow
"@

Set-Content -Path $uninstallScriptPath -Value $uninstallScriptContent
Write-Host "✅ Uninstall script created" -ForegroundColor Green

# Add to PATH (user level)
Write-Host "`n🔧 Adding to PATH..." -ForegroundColor Blue
$currentPath = [System.Environment]::GetEnvironmentVariable("Path", "User")
if ($currentPath -notlike "*$installDir*") {
    $newPath = "$currentPath;$installDir"
    [System.Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    
    # Update current session PATH too
    $env:Path += ";$installDir"
    
    Write-Host "✅ Added $installDir to user PATH" -ForegroundColor Green
    Write-Host "💡 You may need to restart PowerShell to use 'weather' command" -ForegroundColor Yellow
}
else {
    Write-Host "✅ $installDir is already in PATH" -ForegroundColor Green
}

# Create batch file for CMD compatibility
$batchScriptPath = "$installDir\weather.bat"
$batchContent = "@echo off
powershell -ExecutionPolicy Bypass -File `"$installDir\weather.ps1`" %*"
Set-Content -Path $batchScriptPath -Value $batchContent
Write-Host "✅ Created CMD compatibility batch file" -ForegroundColor Green

Write-Host "`n🧪 Testing installation..." -ForegroundColor Yellow

if (Test-Path $weatherScriptPath) {
    Write-Host "✅ Installation files look good!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎉 Installation completed successfully!" -ForegroundColor Green
    Write-Host "💡 Usage:" -ForegroundColor Blue
    Write-Host "  weather          # Run the weather command (after PowerShell restart)"
    Write-Host "  weather uninstall # Remove the system"
    Write-Host ""
    Write-Host "📝 Next steps:" -ForegroundColor Yellow
    Write-Host "1. Restart your PowerShell session to use the 'weather' command directly"
    Write-Host "2. Run 'weather' to use the Weather Intelligence System"
}
else {
    Write-Host "❌ Installation may have failed" -ForegroundColor Red
    exit 1
}
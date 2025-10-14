# PowerShell Installation Script for Weather Intelligence System
# This script installs the Weather Intelligence System on Windows

Write-Host "Installing Weather Intelligence System..." -ForegroundColor Green

# Check for Python, Go, and Git
$pythonExists = Get-Command python -ErrorAction SilentlyContinue
$goExists = Get-Command go -ErrorAction SilentlyContinue
$gitExists = Get-Command git -ErrorAction SilentlyContinue

if (-not $pythonExists) {
    Write-Host "Error: Python is required but not found." -ForegroundColor Red
    exit 1
}

if (-not $goExists) {
    Write-Host "Error: Go is required but not found." -ForegroundColor Red
    exit 1
}

if (-not $gitExists) {
    Write-Host "Error: Git is required but not found." -ForegroundColor Red
    exit 1
}

# Define repository URL
$repoUrl = "https://raw.githubusercontent.com/redsskull/weather-intelligence-system/main"

# Create install location
$installDir = "$env:USERPROFILE\.weather-intel"
$dataIntegrationDir = Join-Path $installDir "data\integration"
New-Item -ItemType Directory -Path $dataIntegrationDir -Force

# Download Python files
Write-Host "Downloading project files..." -ForegroundColor Yellow
$projectPyPath = Join-Path $installDir "project.py"
$requirementsPath = Join-Path $installDir "requirements.txt"

Invoke-WebRequest -Uri "$repoUrl/project.py" -OutFile $projectPyPath
Invoke-WebRequest -Uri "$repoUrl/requirements.txt" -OutFile $requirementsPath

# Create directory structure and download utils files if they exist
$utilsDir = Join-Path $installDir "utils"
New-Item -ItemType Directory -Path $utilsDir -Force

# Download utils files
$utilsBaseUrl = "$repoUrl/utils"
$utilsFiles = @("__init__.py", "analyzer.py", "collection.py", "detection.py", "errors.py", "forecast.py", "geocoding.py", "intelligence_persistence.py", "translations.py")

foreach ($file in $utilsFiles) {
    try {
        Invoke-WebRequest -Uri "$utilsBaseUrl/$file" -OutFile (Join-Path $utilsDir $file) -ErrorAction Stop
    } catch {
        Write-Host "Info: utils/$file not found, skipping..." -ForegroundColor Yellow
    }
}

New-Item -ItemType Directory -Path (Join-Path $installDir "data\cache") -Force
New-Item -ItemType Directory -Path (Join-Path $installDir "data\integration") -Force
New-Item -ItemType Directory -Path (Join-Path $installDir "data\intelligence") -Force

# Create virtual environment and install Python dependencies
$venvPath = Join-Path $installDir "venv"
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv $venvPath
$venvPython = Join-Path $venvPath "Scripts\python.exe"
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r (Join-Path $installDir "requirements.txt")

# Clone the repository to build Go components
Write-Host "Downloading and building Go components..." -ForegroundColor Yellow
$tempDir = Join-Path $env:TEMP "weather-intel-install-$(Get-Random)"
New-Item -ItemType Directory -Path $tempDir -Force
git clone https://github.com/redsskull/weather-intelligence-system.git (Join-Path $tempDir "repo")

# Build Go binaries
$dataCollectorDir = Join-Path $tempDir "repo\go-components\data-collector"
$patternEngineDir = Join-Path $tempDir "repo\go-components\pattern-engine"
$collectorExe = Join-Path $installDir "data-collector.exe"
$engineExe = Join-Path $installDir "pattern-engine.exe"

Set-Location $dataCollectorDir
go build -o $collectorExe
Set-Location $installDir

Set-Location $patternEngineDir
go build -o $engineExe
Set-Location $installDir

# On Windows, executable permissions are handled by the system
# The .exe files should be executable by default

# Cleanup
Remove-Item -Path $tempDir -Recurse -Force

# Create weather command script
$localBinDir = Join-Path $env:USERPROFILE ".local\bin"
New-Item -ItemType Directory -Path $localBinDir -Force

$weatherScriptPath = Join-Path $localBinDir "weather.ps1"
$weatherScriptContent = @"
cd '$installDir'
& '$venvPython' project.py `$args
"@

Set-Content -Path $weatherScriptPath -Value $weatherScriptContent

# Create uninstall script for Windows
$uninstallScriptPath = Join-Path $localBinDir "weather-uninstall.ps1"
$uninstallScriptContent = @"
`$installDir = "`$env:USERPROFILE\.weather-intel"
`$localBinDir = Join-Path `$env:USERPROFILE ".local`bin"

Write-Host "Uninstalling Weather Intelligence System..." -ForegroundColor Red
Remove-Item -Path `$installDir -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path `$weatherScriptPath -Force -ErrorAction SilentlyContinue
Remove-Item -Path `$uninstallScriptPath -Force -ErrorAction SilentlyContinue

# Remove from PATH
`$currentUserPath = [Environment]::GetEnvironmentVariable("PATH", "User")
`$newPath = (`$currentUserPath -split ';' | Where-Object { `$_ -ne `$localBinDir }) -join ';'
[Environment]::SetEnvironmentVariable("PATH", `$newPath, "User")

Write-Host "Uninstallation complete!" -ForegroundColor Green
"@

Set-Content -Path $uninstallScriptPath -Value $uninstallScriptContent

# Add to PATH if not already there
$userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if (-not $userPath.Contains($localBinDir)) {
    [Environment]::SetEnvironmentVariable("PATH", "$localBinDir;$userPath", "User")
    Write-Host "Added $localBinDir to PATH. You may need to restart your terminal." -ForegroundColor Yellow
}

Write-Host "✅ Installation complete!" -ForegroundColor Green
Write-Host "🏃 Run: weather or weather.ps1" -ForegroundColor Green  
Write-Host "🗑️  To uninstall: weather-uninstall or weather-uninstall.ps1" -ForegroundColor Green
Write-Host "🔄 If command not found, you may need to restart your terminal." -ForegroundColor Yellow
# PowerShell Installation Script for Weather Intelligence System
# This script installs the Weather Intelligence System on Windows

Write-Host "Installing Weather Intelligence System..." -ForegroundColor Green

# Check for Python and Go
$pythonExists = Get-Command python -ErrorAction SilentlyContinue
$goExists = Get-Command go -ErrorAction SilentlyContinue

if (-not $pythonExists) {
    Write-Host "Error: Python is required but not found." -ForegroundColor Red
    exit 1
}

if (-not $goExists) {
    Write-Host "Error: Go is required but not found." -ForegroundColor Red
    exit 1
}

# Create install location
$installDir = "$env:USERPROFILE\.weather-intel"
$dataIntegrationDir = Join-Path $installDir "data\integration"
New-Item -ItemType Directory -Path $dataIntegrationDir -Force

# Copy Python files
Copy-Item "project.py" $installDir -Force
Copy-Item "requirements.txt" $installDir -Force
Copy-Item "utils" $installDir -Recurse -Force
Copy-Item "data" $installDir -Recurse -Force

# Create virtual environment and install Python dependencies
$venvPath = Join-Path $installDir "venv"
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv $venvPath
$venvPython = Join-Path $venvPath "Scripts\python.exe"
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r (Join-Path $installDir "requirements.txt")

# Build and copy Go binaries
Set-Location (Join-Path $PSScriptRoot "go-components/data-collector")
$collectorExe = Join-Path $installDir "data-collector.exe"
go build -o $collectorExe
Set-Location $PSScriptRoot

Set-Location (Join-Path $PSScriptRoot "go-components/pattern-engine")
$engineExe = Join-Path $installDir "pattern-engine.exe"
go build -o $engineExe
Set-Location $PSScriptRoot

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

Write-Host "Installation complete!" -ForegroundColor Green
Write-Host "Run: weather or weather.ps1" -ForegroundColor Green
Write-Host "To uninstall: weather-uninstall or weather-uninstall.ps1" -ForegroundColor Green
Write-Host "If command not found, you may need to restart your terminal." -ForegroundColor Yellow
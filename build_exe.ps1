# PowerShell script to build executable from Python program
# Read version info from metadata.json and generate executable name

# Get script directory and set location
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

Write-Host "Activating virtual environment..." -ForegroundColor Green

# Activate virtual environment
$venvPath = Join-Path $scriptDir "venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    & $venvPath
    Write-Host "Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "Virtual environment not found: $venvPath" -ForegroundColor Red
    exit 1
}

Write-Host "Reading version information..." -ForegroundColor Green

# Read version information
$metadataPath = Join-Path $scriptDir "medatada.json"
if (Test-Path $metadataPath) {
    $metadata = Get-Content $metadataPath -Raw | ConvertFrom-Json
    $version = $metadata.version
    $date = $metadata.data
    
    Write-Host "Version: $version" -ForegroundColor Cyan
    Write-Host "Date: $date" -ForegroundColor Cyan
} else {
    Write-Host "medatada.json file not found: $metadataPath" -ForegroundColor Red
    exit 1
}

# Generate executable name
$exeName = "${date}${version}_watch_hntxtfile"
Write-Host "Executable name: $exeName.exe" -ForegroundColor Cyan

# Switch to gui directory
$guiDir = Join-Path $scriptDir "gui"
if (Test-Path $guiDir) {
    Set-Location $guiDir
    Write-Host "Switched to gui directory" -ForegroundColor Green
} else {
    Write-Host "gui directory not found: $guiDir" -ForegroundColor Red
    exit 1
}

Write-Host "Running PyInstaller..." -ForegroundColor Green

# Execute PyInstaller command
$pyinstallerCmd = "pyinstaller --onefile --windowed --icon=assets/logo.ico --add-data `"assets;assets`" --name=$exeName main.py"

Write-Host "Command: $pyinstallerCmd" -ForegroundColor Yellow

try {
    Invoke-Expression $pyinstallerCmd
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Build successful!" -ForegroundColor Green
        
        $exePath = Join-Path (Get-Location) "dist\$exeName.exe"
        if (Test-Path $exePath) {
            $fileSize = (Get-Item $exePath).Length / 1MB
            Write-Host "Executable location: $exePath" -ForegroundColor Green
            Write-Host "File size: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Cyan
        }
    } else {
        Write-Host "Build failed with exit code: $LASTEXITCODE" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Error during build: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "Script completed successfully!" -ForegroundColor Green
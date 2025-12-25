# Setup script for SEFCNet development environment
# Run from the repository root with:
#   .\scripts\setup_venv.ps1

# Fail on error
$ErrorActionPreference = "Stop"

Write-Host "Creating Python virtual environment..." -ForegroundColor Green

# Create venv if it doesn't exist
if (-not (Test-Path ".\venv")) {
    python -m venv venv
}

# Allow script execution for this process
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# Activate venv
& '.\venv\Scripts\Activate.ps1'

# Upgrade pip
python -m pip install --upgrade pip

Write-Host "Installing dependencies from requirements.txt..." -ForegroundColor Green

# Install dependencies from both requirements files
pip install -r requirements.txt
pip install -r SEFCNet/requirements.txt

Write-Host "Virtual environment setup complete." -ForegroundColor Green
Write-Host ""
Write-Host "To activate the environment:" -ForegroundColor Yellow
Write-Host "  .\venv\Scripts\Activate.ps1"
Write-Host ""
Write-Host "To deactivate:" -ForegroundColor Yellow
Write-Host "  deactivate"
Write-Host ""
Write-Host "To run the main script:" -ForegroundColor Yellow
Write-Host "  cd SEFCNet"
Write-Host "  python main.py"

# PowerShell script to set up virtual environment
Write-Host "Setting up Python virtual environment for SEFCNet..."

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

Write-Host "Setup complete! Virtual environment is now ready."
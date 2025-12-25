# SEFCNet Server Startup Script for Windows
# =========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SEFCNet Server Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
& .\venv\Scripts\Activate.ps1

# Check if requirements are installed
Write-Host "Checking dependencies..." -ForegroundColor Green
pip install -q -r requirements.txt

# Load environment variables
if (Test-Path ".env") {
    Write-Host "Loading environment variables from .env..." -ForegroundColor Green
} else {
    Write-Host "Warning: .env file not found. Using defaults." -ForegroundColor Yellow
    Write-Host "Copy .env.example to .env and configure it." -ForegroundColor Yellow
}

# Start the server
Write-Host "Starting SEFCNet server..." -ForegroundColor Green
Write-Host "Server will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

python start.py


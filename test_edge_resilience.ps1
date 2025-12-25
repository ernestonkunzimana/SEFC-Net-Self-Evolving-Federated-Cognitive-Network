#!/usr/bin/env pwsh
# PowerShell script to test edge resilience module
# Usage: .\test_edge_resilience.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SEFC-Net Edge Resilience Test Runner" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Save current location
Push-Location

try {
    # Change to SEFCNet directory
    Set-Location "C:\Users\ADMIN\OneDrive\Desktop\SEFCNet\SEFCNet"
    
    Write-Host "Running tests from: $(Get-Location)" -ForegroundColor Yellow
    Write-Host ""
    
    # Activate virtual environment if it exists
    $venvActivate = "..\..\.venv\Scripts\Activate.ps1"
    if (Test-Path $venvActivate) {
        Write-Host "Activating virtual environment..." -ForegroundColor Green
        & $venvActivate
    }
    
    # Run tests
    python edge_resilience\test_edge_resilience.py
    
    $exitCode = $LASTEXITCODE
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    if ($exitCode -eq 0) {
        Write-Host "✅ All tests passed!" -ForegroundColor Green
    } else {
        Write-Host "❌ Some tests failed" -ForegroundColor Red
    }
    Write-Host "========================================" -ForegroundColor Cyan
    
    exit $exitCode
    
} finally {
    # Restore original location
    Pop-Location
}

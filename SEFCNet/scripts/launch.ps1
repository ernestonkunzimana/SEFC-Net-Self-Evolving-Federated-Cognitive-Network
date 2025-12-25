Write-Host "?? Launching SEFCNet..."

# Create and activate virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
}

# Activate virtual environment
.\venv\Scripts\Activate

# Install specific versions of dependencies
Write-Host "Installing dependencies..."
pip install --upgrade pip
pip install protobuf==3.20.0
pip install tensorflow==2.12.0
pip install flwr==1.6.0
pip install -r requirements.txt

# Start the system
try {
    Write-Host "Starting SEFCNet..."
    python main.py --dashboard
} catch {
    Write-Host "Error starting SEFCNet: $_"
} finally {
    deactivate
}

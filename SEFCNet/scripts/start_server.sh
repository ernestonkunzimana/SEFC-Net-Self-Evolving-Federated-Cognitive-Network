#!/bin/bash
# SEFCNet Server Startup Script for Linux/macOS
# =============================================

echo "========================================"
echo "SEFCNet Server Startup"
echo "========================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if requirements are installed
echo "Checking dependencies..."
pip install -q -r requirements.txt

# Load environment variables
if [ -f ".env" ]; then
    echo "Loading environment variables from .env..."
else
    echo "Warning: .env file not found. Using defaults."
    echo "Copy .env.example to .env and configure it."
fi

# Start the server
echo "Starting SEFCNet server..."
echo "Server will be available at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo "========================================"

python start.py


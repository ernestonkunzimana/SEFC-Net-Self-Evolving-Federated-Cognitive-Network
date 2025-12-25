# Dependency Fixes for SEFCNet

This file provides the exact changes needed to fix dependency conflicts.

## Issue Summary

**Problem**: TensorFlow 2.12 requires `numpy<1.24`, but modern packages (scikit-learn 1.8+, pandas 2.3+) require `numpy>=2.4`

**Impact**: Cannot install all dependencies, tests cannot run, system cannot start

---

## Solution 1: Pin to Compatible Versions (QUICKEST)

### Changes to requirements.txt

Replace these lines:

```diff
- numpy>=1.21.0,<1.24
+ numpy==1.23.5

- pandas>=2.0.0
+ pandas==2.0.3

Add this line after deap:
+ scikit-learn==1.3.2

Comment out problematic dependency:
- crypten>=0.4.0
+ # crypten>=0.4.0  # OPTIONAL: Advanced MPC (deprecated sklearn dependency)
```

### Full Updated requirements.txt (Lines 25-48)

```python
# Monitoring & Analytics
plotly>=5.17.0
pandas==2.0.3
numpy==1.23.5
dash>=2.14.0
dash-bootstrap-components>=1.5.0

# Optional but recommended
psutil>=5.9.0
tenacity>=8.2.0
aiohttp>=3.8.0

# MANDATORY: Quantum-RIS Integration
qiskit>=0.45.0
cirq>=1.3.0

# MANDATORY: Cognitive Network
networkx>=3.2.0

# MANDATORY: Biological Evolution
deap>=1.4.0
scikit-learn==1.3.2

# MANDATORY: Privacy Layer
tenseal>=0.3.0
# crypten>=0.4.0  # OPTIONAL: Advanced MPC (deprecated sklearn dependency)

# MANDATORY: Cross-Modal Learning
torch>=2.0.0
transformers>=4.30.0
```

### Install Command

```powershell
cd c:\Users\ADMIN\OneDrive\Desktop\SEFCNet\SEFCNet
$prev=$env:CURL_CA_BUNDLE
$env:CURL_CA_BUNDLE=""
C:/Users/ADMIN/OneDrive/Desktop/SEFCNet/.venv/Scripts/python.exe -m pip install -r requirements.txt
$env:CURL_CA_BUNDLE=$prev
```

---

## Solution 2: Upgrade to Modern Stack (RECOMMENDED)

### Changes to requirements.txt

```diff
- tensorflow==2.12.0
+ tensorflow>=2.17.0

- flwr==1.6.0
+ flwr>=1.10.0

- numpy>=1.21.0,<1.24
+ numpy>=1.26.0,<3.0.0

- pandas>=2.0.0
+ pandas>=2.3.0

Comment out:
- crypten>=0.4.0
+ # crypten>=0.4.0  # OPTIONAL: Use pysyft instead for privacy

Add:
+ pysyft>=0.8.0  # Modern privacy-preserving ML
```

### Potential Code Changes Required

If you upgrade TensorFlow, you may need to update code:

**File**: `SEFCNet/models/base_model.py`
```python
# Old (TF 2.12)
import tensorflow as tf
from tensorflow.keras import layers

# New (TF 2.17+) - No changes needed, fully backward compatible
import tensorflow as tf
from tensorflow.keras import layers
```

**File**: `SEFCNet/privacy/privacy_fl.py` (if using crypten)
```python
# Old
import crypten

# New
import syft as sy
# Update privacy methods to use PySyft API
```

---

## Solution 3: Docker-Based Installation (ISOLATION)

Create a Docker image with all dependencies pre-installed:

**File**: `Dockerfile.fixed`

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies with fixed versions
RUN pip install --no-cache-dir \
    numpy==1.23.5 \
    pandas==2.0.3 \
    scikit-learn==1.3.2 && \
    pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose ports
EXPOSE 8000 8501

# Run application
CMD ["python", "main.py"]
```

Build and run:
```powershell
docker build -t sefcnet:fixed -f Dockerfile.fixed .
docker run -p 8000:8000 -p 8501:8501 sefcnet:fixed
```

---

## Verification Steps

After applying fixes:

```powershell
# 1. Verify installation
C:/Users/ADMIN/OneDrive/Desktop/SEFCNet/.venv/Scripts/python.exe -m pip list | Select-String "numpy|tensorflow|pandas|scikit-learn"

# Expected output:
# numpy        1.23.5
# tensorflow   2.12.0
# pandas       2.0.3
# scikit-learn 1.3.2

# 2. Test imports
C:/Users/ADMIN/OneDrive/Desktop/SEFCNet/.venv/Scripts/python.exe -c "import numpy; import tensorflow; import pandas; import sklearn; print('All imports successful')"

# 3. Run tests
cd c:\Users\ADMIN\OneDrive\Desktop\SEFCNet\SEFCNet
$prev=$env:CURL_CA_BUNDLE
$env:CURL_CA_BUNDLE=""
C:/Users/ADMIN/OneDrive/Desktop/SEFCNet/.venv/Scripts/python.exe -m pytest tests/test_mandatory_core.py -v
$env:CURL_CA_BUNDLE=$prev
```

---

## Manual Fix Script (PowerShell)

Save as `fix_dependencies.ps1`:

```powershell
# SEFCNet Dependency Fix Script
Write-Host "Fixing SEFCNet Dependencies..." -ForegroundColor Green

# Navigate to project
cd c:\Users\ADMIN\OneDrive\Desktop\SEFCNet\SEFCNet

# Backup original requirements
Copy-Item requirements.txt requirements.txt.backup

# Apply fixes
(Get-Content requirements.txt) | ForEach-Object {
    $_ -replace 'numpy>=1.21.0,<1.24', 'numpy==1.23.5' `
       -replace 'pandas>=2.0.0', 'pandas==2.0.3' `
       -replace '^crypten>=0.4.0', '# crypten>=0.4.0  # OPTIONAL: deprecated sklearn dependency'
} | Set-Content requirements.txt.fixed

# Add scikit-learn
Add-Content requirements.txt.fixed "`nscikit-learn==1.3.2"

# Replace original
Move-Item -Force requirements.txt.fixed requirements.txt

Write-Host "Requirements.txt updated!" -ForegroundColor Green

# Clear SSL env var and install
$prev=$env:CURL_CA_BUNDLE
$env:CURL_CA_BUNDLE=""

Write-Host "Installing dependencies..." -ForegroundColor Yellow
C:/Users/ADMIN/OneDrive/Desktop/SEFCNet/.venv/Scripts/python.exe -m pip install -r requirements.txt

$env:CURL_CA_BUNDLE=$prev

Write-Host "Done! Run tests with: pytest tests/ -v" -ForegroundColor Green
```

Run with:
```powershell
.\fix_dependencies.ps1
```

---

## Alternative: Conda Environment

If pip continues to have issues, use conda:

```powershell
# Create conda environment
conda create -n sefcnet python=3.11 -y
conda activate sefcnet

# Install dependencies
conda install -c conda-forge numpy=1.23.5 pandas=2.0.3 scikit-learn=1.3.2 -y
conda install -c conda-forge tensorflow=2.12.0 -y

# Install remaining with pip
pip install flwr qiskit cirq deap torch transformers shap lime codecarbon
```

---

## Updated Requirements File (Complete)

Save as `requirements-fixed.txt`:

```txt
# Core ML/FL dependencies
tensorflow==2.12.0
flwr==1.6.0
protobuf>=3.20.3,<5.0.0dev
streamlit>=1.22.0
fastapi>=0.95.0
uvicorn[standard]>=0.21.0
httpx>=0.24.0
PyJWT>=2.0.0
optuna>=3.0.0
kubernetes>=25.3.0
prometheus_client>=0.16.0
pyyaml>=6.0.0
python-dotenv>=1.0.0

# Database
aiosqlite>=0.19.0

# Security & Authentication
passlib[bcrypt]>=1.7.4
cryptography>=41.0.0
email-validator>=2.0.0

# Monitoring & Analytics
plotly>=5.17.0
pandas==2.0.3
numpy==1.23.5
dash>=2.14.0
dash-bootstrap-components>=1.5.0

# Optional but recommended
psutil>=5.9.0
tenacity>=8.2.0
aiohttp>=3.8.0

# MANDATORY: Quantum-RIS Integration
qiskit>=0.45.0
cirq>=1.3.0

# MANDATORY: Cognitive Network
networkx>=3.2.0

# MANDATORY: Biological Evolution
deap>=1.4.0
scikit-learn==1.3.2

# MANDATORY: Privacy Layer
tenseal>=0.3.0
# crypten>=0.4.0  # OPTIONAL: Advanced MPC (deprecated sklearn dependency)

# MANDATORY: Cross-Modal Learning
torch>=2.0.0
transformers>=4.30.0

# MANDATORY: Explainable FL
shap>=0.42.0
lime>=0.2.0

# MANDATORY: Sustainable FL
codecarbon>=2.3.0

# Testing
pytest>=7.3.0
pytest-asyncio>=0.21.0
```

---

## Contact & Support

- **Repository**: https://github.com/ernestonkunzimana/SEFC-Net-Self-Evolving-Federated-Cognitive-Network
- **Issues**: Create GitHub issue for problems
- **Documentation**: See PROJECT_AUDIT_REPORT.md for details

---

**Status**: Ready to apply  
**Last Updated**: December 25, 2025

"""Integration tests for the analytics system"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import sys
from pathlib import Path

from SEFCNet.analytics.routes import router
from SEFCNet.auth.security import create_access_token
from SEFCNet.analytics.performance_analyzer import PerformanceAnalyzer
from SEFCNet.analytics.metrics_collector import MetricsCollector

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture
def client():
    """Create test client"""
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)

@pytest.fixture
def admin_token():
    """Create admin token for testing"""
    return create_access_token(
        data={"sub": "test_admin", "permissions": ["READ", "WRITE", "MANAGE"]},
        expires_delta=timedelta(minutes=30)
    )

@pytest.fixture
def read_token():
    """Create read-only token for testing"""
    return create_access_token(
        data={"sub": "test_user", "permissions": ["READ"]},
        expires_delta=timedelta(minutes=30)
    )

@pytest.fixture
def performance_analyzer():
    config = {
        'analytics': {
            'metrics_window': 10,
            'performance_threshold': 0.8
        }
    }
    return PerformanceAnalyzer(config)

def test_register_model(client, admin_token):
    """Test model registration endpoint"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    metadata = {
        "name": "test_model",
        "version": "1.0.0",
        "architecture": "CNN",
        "created_at": datetime.now().isoformat()
    }
    
    response = client.post("/analytics/models", json=metadata, headers=headers)
    assert response.status_code == 200
    assert "model_id" in response.json()

def test_create_experiment(client, admin_token):
    """Test experiment creation endpoint"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    config = {
        "name": "test_experiment",
        "model_id": "test_model_1",
        "hyperparameters": {
            "learning_rate": 0.001,
            "batch_size": 32
        }
    }
    
    response = client.post("/analytics/experiments", json=config, headers=headers)
    assert response.status_code == 200
    assert "experiment_id" in response.json()

def test_log_metrics(client, admin_token):
    """Test metric logging endpoint"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    metrics = {
        "accuracy": 0.95,
        "loss": 0.05
    }
    
    response = client.post(
        "/analytics/models/test_model_1/metrics",
        json=metrics,
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_get_model_analytics(client, read_token):
    """Test model analytics retrieval endpoint"""
    headers = {"Authorization": f"Bearer {read_token}"}
    response = client.get("/analytics/models/test_model_1", headers=headers)
    assert response.status_code == 200
    assert "metrics" in response.json()

def test_get_experiment_results(client, read_token):
    """Test experiment results retrieval endpoint"""
    headers = {"Authorization": f"Bearer {read_token}"}
    response = client.get("/analytics/experiments/test_exp_1", headers=headers)
    assert response.status_code == 200
    assert "results" in response.json()

def test_analytics_lifecycle(client, admin_token):
    """Test analytics manager lifecycle endpoints"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Start analytics
    response = client.post("/analytics/start", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "started"
    
    # Stop analytics
    response = client.post("/analytics/stop", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "stopped"

def test_permission_denied(client, read_token):
    """Test permission enforcement"""
    headers = {"Authorization": f"Bearer {read_token}"}
    
    # Try to register model with read-only token
    metadata = {
        "name": "test_model",
        "version": "1.0.0"
    }
    response = client.post("/analytics/models", json=metadata, headers=headers)
    assert response.status_code == 403

def test_invalid_input(client, admin_token):
    """Test input validation"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Try to register model with invalid metadata
    metadata = {
        "name": "",  # Invalid empty name
        "version": "1.0.0"
    }
    response = client.post("/analytics/models", json=metadata, headers=headers)
    assert response.status_code == 400

def test_error_handling(client, admin_token):
    """Test error handling"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Try to get non-existent model
    response = client.get("/analytics/models/non_existent", headers=headers)
    assert response.status_code == 500
    assert "failed" in response.json()["detail"]

def test_analyze_performance(performance_analyzer):
    metrics = {
        'accuracy': 0.85,
        'loss': 0.15,
        'training_time': 10.5
    }
    result = performance_analyzer.analyze_round(metrics)
    assert result.accuracy == 0.85
    assert result.loss == 0.15
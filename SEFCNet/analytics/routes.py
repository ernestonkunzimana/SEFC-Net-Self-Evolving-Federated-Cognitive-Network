"""
Analytics API Routes for SEFCNet
============================

This module provides RESTful API endpoints for:
- Model analytics
- Experiment tracking
- Performance monitoring
- Drift detection
- Optimization results
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from auth.security import get_current_user, check_permission, Permission, TokenData
from .analytics_manager import analytics_manager

class ModelRegistration(BaseModel):
    name: str
    version: str
    architecture: Any | None = None
    created_at: Optional[datetime] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    metrics: Dict[str, float] = Field(default_factory=dict)
    type: Optional[str] = None


class ExperimentCreate(BaseModel):
    name: str
    model_id: str
    description: Optional[str] = ""
    hyperparameters: Dict[str, Any] = Field(default_factory=dict)
    metrics: Optional[List[str]] = None
    tags: Dict[str, str] = Field(default_factory=dict)


router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.post("/models")
async def register_model(
    metadata: ModelRegistration,
    token_data: TokenData = Depends(get_current_user)
) -> Dict[str, Any]:
    """Register a new model for analytics tracking."""
    if not check_permission([Permission.WRITE], token_data):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    try:
        result = await analytics_manager.register_model(metadata.model_dump(exclude_none=True))
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Model registration failed: {str(e)}"
        )

@router.post("/experiments")
async def create_experiment(
    config: ExperimentCreate,
    token_data: TokenData = Depends(get_current_user)
) -> Dict[str, Any]:
    """Create a new experiment."""
    if not check_permission([Permission.WRITE], token_data):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    try:
        payload = config.model_dump(exclude_none=True)
        # Experiments API uses "hyperparameters" naming; align with manager expectation
        payload.setdefault("parameters", payload.pop("hyperparameters", {}))
        result = await analytics_manager.create_experiment(payload)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Experiment creation failed: {str(e)}"
        )

@router.post("/models/{model_id}/metrics")
async def log_metrics(
    model_id: str,
    metrics: Dict[str, float],
    token_data: TokenData = Depends(get_current_user)
):
    """Log metrics for a model."""
    if not check_permission([Permission.WRITE], token_data):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    try:
        await analytics_manager.log_metrics(model_id, metrics)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Metric logging failed: {str(e)}"
        )

@router.get("/models/{model_id}")
async def get_model_analytics(
    model_id: str,
    token_data: TokenData = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get analytics for a specific model."""
    if not check_permission([Permission.READ], token_data):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    try:
        return await analytics_manager.get_model_analytics(model_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analytics retrieval failed: {str(e)}"
        )

@router.get("/experiments/{experiment_id}")
async def get_experiment_results(
    experiment_id: str,
    token_data: TokenData = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get results for a specific experiment."""
    if not check_permission([Permission.READ], token_data):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    try:
        return await analytics_manager.get_experiment_results(experiment_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Results retrieval failed: {str(e)}"
        )

@router.post("/start")
async def start_analytics(
    token_data: TokenData = Depends(get_current_user)
):
    """Start the analytics manager."""
    if not check_permission([Permission.MANAGE], token_data):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    await analytics_manager.start()
    return {"status": "started"}

@router.post("/stop")
async def stop_analytics(
    token_data: TokenData = Depends(get_current_user)
):
    """Stop the analytics manager."""
    if not check_permission([Permission.MANAGE], token_data):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    await analytics_manager.stop()
    return {"status": "stopped"}
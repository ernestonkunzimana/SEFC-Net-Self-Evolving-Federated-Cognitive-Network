"""
Monitoring API Routes for SEFCNet
===============================

This module provides RESTful API endpoints for:
- Metrics access and management
- Alert management
- Health checks
- System monitoring
"""

from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from auth.security import get_current_user, check_permission, Permission, TokenData
from .metrics_collector import metrics_collector
from .monitoring_service import monitoring_service, Alert, HealthCheck

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

@router.get("/metrics")
async def get_metrics(
    format: str = Query("prometheus", enum=["prometheus", "json"]),
    token_data: TokenData = Depends(get_current_user)
):
    """Get current metrics in specified format."""
    if not check_permission([Permission.READ], token_data):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    if format == "prometheus":
        return metrics_collector.export_metrics(format="prometheus")
    else:
        return metrics_collector.get_metrics_snapshot()

@router.get("/alerts/active")
async def get_active_alerts(
    severity: Optional[str] = Query(
        None,
        enum=["critical", "warning", "info"]
    ),
    token_data: TokenData = Depends(get_current_user)
) -> List[Alert]:
    """Get active alerts, optionally filtered by severity."""
    if not check_permission([Permission.READ], token_data):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    return monitoring_service.get_active_alerts(severity=severity)

@router.get("/alerts/history")
async def get_alert_history(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    token_data: TokenData = Depends(get_current_user)
) -> List[Alert]:
    """Get historical alerts within a time range."""
    if not check_permission([Permission.READ], token_data):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    return monitoring_service.get_alert_history(
        start_time=start_time,
        end_time=end_time
    )

@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    token_data: TokenData = Depends(get_current_user)
) -> Dict[str, str]:
    """Acknowledge an active alert."""
    if not check_permission([Permission.WRITE], token_data):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    if monitoring_service.acknowledge_alert(alert_id):
        return {"status": "acknowledged", "alert_id": alert_id}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Alert not found or not active"
    )

@router.post("/health-checks")
async def register_health_check(
    check: HealthCheck,
    token_data: TokenData = Depends(get_current_user)
):
    """Register a new health check."""
    if not check_permission([Permission.MANAGE], token_data):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    monitoring_service.register_health_check(check)
    return {"status": "registered", "check": check.name}

@router.get("/health", response_model=dict)
async def health():
    """
    Health endpoint returns a simple dict; avoid using non-Pydantic return annotations
    which FastAPI tries to convert into response models.
    """
    try:
        # collect minimal health info (adjust to your implementation)
        return {
            "status": "ok",
            "components": {
                "monitoring": True,
                "federation": True
            }
        }
    except Exception:
        return {"status": "error"}

@router.post("/start")
async def start_monitoring(
    token_data: TokenData = Depends(get_current_user)
):
    """Start the monitoring service."""
    if not check_permission([Permission.MANAGE], token_data):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    await monitoring_service.start_monitoring()
    return {"status": "started"}

@router.post("/stop")
async def stop_monitoring(
    token_data: TokenData = Depends(get_current_user)
):
    """Stop the monitoring service."""
    if not check_permission([Permission.MANAGE], token_data):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    await monitoring_service.stop_monitoring()
    return {"status": "stopped"}
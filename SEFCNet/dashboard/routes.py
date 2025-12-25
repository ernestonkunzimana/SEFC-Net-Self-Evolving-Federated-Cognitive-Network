"""
Dashboard API Routes for SEFCNet
=============================

This module provides RESTful API endpoints for:
- Dashboard configuration and management
- Real-time data streaming
- Visualization controls
- Analytics endpoints
"""

from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, WebSocket, status
from fastapi.responses import JSONResponse

from auth.security import get_current_user, check_permission, Permission, TokenData
from .dashboard_manager import dashboard_manager, DashboardConfig

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/configs")
async def get_available_dashboards(
    token_data: TokenData = Depends(get_current_user)
) -> List[Dict[str, str]]:
    """Get list of available dashboards."""
    if not check_permission([Permission.READ], token_data):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    return dashboard_manager.get_available_dashboards()

@router.get("/config/{dashboard_id}")
async def get_dashboard_config(
    dashboard_id: str,
    token_data: TokenData = Depends(get_current_user)
) -> Optional[DashboardConfig]:
    """Get specific dashboard configuration."""
    if not check_permission([Permission.READ], token_data):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    config = await dashboard_manager.get_dashboard_config(dashboard_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard configuration not found"
        )
    return config

@router.post("/start")
async def start_dashboard_updates(
    token_data: TokenData = Depends(get_current_user)
):
    """Start dashboard update broadcasting."""
    if not check_permission([Permission.MANAGE], token_data):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    await dashboard_manager.start_broadcasting()
    return {"status": "started"}

@router.post("/stop")
async def stop_dashboard_updates(
    token_data: TokenData = Depends(get_current_user)
):
    """Stop dashboard update broadcasting."""
    if not check_permission([Permission.MANAGE], token_data):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    await dashboard_manager.stop_broadcasting()
    return {"status": "stopped"}

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time dashboard updates."""
    await dashboard_manager.add_connection(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except Exception as e:
        dashboard_manager.remove_connection(websocket)
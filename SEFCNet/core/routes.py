"""
Core System API Routes for SEFCNet
==============================

This module provides RESTful API endpoints for:
- System management
- Service deployment
- Resource orchestration
- Health monitoring
- System operations
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from auth.security import get_current_user, check_permission, Permission, TokenData
from .system_manager import system_manager, ServiceConfig, SystemState

router = APIRouter(prefix="/system", tags=["system"])

@router.get("/state")
async def get_system_state(
    token_data: TokenData = Depends(get_current_user)
) -> SystemState:
    """Get current system state."""
    if not check_permission([Permission.READ], token_data):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    return await system_manager.get_system_state()

@router.post("/services")
async def deploy_service(
    service_config: ServiceConfig,
    token_data: TokenData = Depends(get_current_user)
) -> Dict[str, str]:
    """Deploy a new service."""
    if not check_permission([Permission.MANAGE], token_data):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    try:
        result = await system_manager.deploy_service(service_config)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Deployment failed: {str(e)}"
        )

@router.post("/start")
async def start_system(
    token_data: TokenData = Depends(get_current_user)
):
    """Start the system manager."""
    if not check_permission([Permission.MANAGE], token_data):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    await system_manager.start()
    return {"status": "started"}

@router.post("/stop")
async def stop_system(
    token_data: TokenData = Depends(get_current_user)
):
    """Stop the system manager."""
    if not check_permission([Permission.MANAGE], token_data):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    await system_manager.stop()
    return {"status": "stopped"}

@router.get("/health")
async def get_system_health(
    token_data: TokenData = Depends(get_current_user)
) -> Dict[str, bool]:
    """Get system health status."""
    if not check_permission([Permission.READ], token_data):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    state = await system_manager.get_system_state()
    return state.health

@router.get("/resources")
async def get_resource_states(
    token_data: TokenData = Depends(get_current_user)
) -> Dict[str, Dict[str, Any]]:
    """Get current resource states."""
    if not check_permission([Permission.READ], token_data):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    state = await system_manager.get_system_state()
    return state.resources

@router.get("/services/status")
async def get_service_states(
    token_data: TokenData = Depends(get_current_user)
) -> Dict[str, Dict[str, Any]]:
    """Get current service states."""
    if not check_permission([Permission.READ], token_data):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    state = await system_manager.get_system_state()
    return state.services

@router.get("/alerts")
async def get_system_alerts(
    token_data: TokenData = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get current system alerts."""
    if not check_permission([Permission.READ], token_data):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    state = await system_manager.get_system_state()
    return state.alerts
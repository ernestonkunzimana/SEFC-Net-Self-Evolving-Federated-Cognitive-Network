"""
Orchestration API Routes for SEFCNet
================================

This module provides RESTful API endpoints for:
- Node management
- Task scheduling
- Resource allocation
- Federation control
- Coordination services
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from auth.security import get_current_user, check_permission, Permission, TokenData
from .orchestration_manager import (
    orchestration_manager,
    NodeConfig,
    TaskDefinition
)

router = APIRouter(prefix="/orchestration", tags=["orchestration"])

@router.post("/nodes")
async def register_node(
    config: NodeConfig,
    token_data: TokenData = Depends(get_current_user)
) -> Dict[str, Any]:
    """Register a new node in the federation."""
    if not check_permission([Permission.MANAGE], token_data):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    try:
        result = await orchestration_manager.register_node(config)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Node registration failed: {str(e)}"
        )

@router.post("/tasks")
async def submit_task(
    task: TaskDefinition,
    token_data: TokenData = Depends(get_current_user)
) -> Dict[str, Any]:
    """Submit a new task for execution."""
    if not check_permission([Permission.WRITE], token_data):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    try:
        result = await orchestration_manager.submit_task(task)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Task submission failed: {str(e)}"
        )

@router.get("/state")
async def get_federation_state(
    token_data: TokenData = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get current federation state."""
    if not check_permission([Permission.READ], token_data):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    return await orchestration_manager.get_federation_state()

@router.post("/start")
async def start_orchestration(
    token_data: TokenData = Depends(get_current_user)
):
    """Start the orchestration manager."""
    if not check_permission([Permission.MANAGE], token_data):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    await orchestration_manager.start()
    return {"status": "started"}

@router.post("/stop")
async def stop_orchestration(
    token_data: TokenData = Depends(get_current_user)
):
    """Stop the orchestration manager."""
    if not check_permission([Permission.MANAGE], token_data):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    await orchestration_manager.stop()
    return {"status": "stopped"}

@router.get("/nodes")
async def get_registered_nodes(
    token_data: TokenData = Depends(get_current_user)
) -> Dict[str, NodeConfig]:
    """Get list of registered nodes."""
    if not check_permission([Permission.READ], token_data):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    state = await orchestration_manager.get_federation_state()
    return state['nodes']

@router.get("/tasks")
async def get_active_tasks(
    token_data: TokenData = Depends(get_current_user)
) -> Dict[str, TaskDefinition]:
    """Get list of active tasks."""
    if not check_permission([Permission.READ], token_data):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    state = await orchestration_manager.get_federation_state()
    return state['tasks']

@router.get("/topology")
async def get_federation_topology(
    token_data: TokenData = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get current federation topology."""
    if not check_permission([Permission.READ], token_data):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    state = await orchestration_manager.get_federation_state()
    return state['topology']
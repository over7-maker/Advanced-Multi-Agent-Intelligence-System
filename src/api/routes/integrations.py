# src/api/routes/integrations.py (COMPLETE INTEGRATION API)
from fastapi import APIRouter, Depends, HTTPException, Query, Body, Header, Request
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from src.amas.integration.integration_manager import (
    get_integration_manager,
    IntegrationManager,
    IntegrationPlatform,
    IntegrationStatus
)
from pydantic import BaseModel

router = APIRouter(prefix="/integrations", tags=["integrations"])
logger = logging.getLogger(__name__)

# Pydantic models
class IntegrationCreateRequest(BaseModel):
    platform: str
    credentials: Dict[str, Any]
    configuration: Optional[Dict[str, Any]] = None

class IntegrationTriggerRequest(BaseModel):
    event_type: str
    data: Dict[str, Any]

class IntegrationResponse(BaseModel):
    integration_id: str
    platform: str
    status: str
    created_at: str
    last_sync: Optional[str] = None
    sync_count: int
    error_count: int

class IntegrationListResponse(BaseModel):
    integrations: List[IntegrationResponse]
    total: int

class WebhookEventResponse(BaseModel):
    status: str
    event_type: Optional[str] = None

# Helper function for authentication (placeholder - should use actual auth)
async def get_current_user():
    """Get current user - placeholder for actual authentication"""
    return {"user_id": "default_user"}

@router.post("", response_model=IntegrationResponse)
@router.post("/", response_model=IntegrationResponse)
async def create_integration(
    integration_request: IntegrationCreateRequest,
    current_user = Depends(get_current_user),
    integration_manager: IntegrationManager = Depends(get_integration_manager)
):
    """
    Register new integration
    
    ✅ Platform credential validation
    ✅ Configuration setup
    ✅ Webhook URL generation
    ✅ Database persistence
    """
    
    try:
        # Validate platform
        try:
            platform = IntegrationPlatform(integration_request.platform)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid platform: {integration_request.platform}"
            )
        
        # Register integration
        integration_id = await integration_manager.register_integration(
            user_id=current_user["user_id"],
            platform=platform,
            credentials=integration_request.credentials,
            configuration=integration_request.configuration
        )
        
        # Get integration status
        status = await integration_manager.get_integration_status(integration_id)
        
        return IntegrationResponse(
            integration_id=status["integration_id"],
            platform=status["platform"],
            status=status["status"],
            created_at=status["created_at"],
            last_sync=status["last_sync"],
            sync_count=status["sync_count"],
            error_count=status["error_count"]
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create integration: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create integration")

@router.get("", response_model=IntegrationListResponse)
@router.get("/", response_model=IntegrationListResponse)
async def list_integrations(
    user_id: Optional[str] = Query(None),
    platform: Optional[str] = Query(None),
    current_user = Depends(get_current_user),
    integration_manager: IntegrationManager = Depends(get_integration_manager)
):
    """
    List integrations
    
    Filters:
    - user_id: Filter by user
    - platform: Filter by platform
    """
    
    try:
        platform_enum = None
        if platform:
            try:
                platform_enum = IntegrationPlatform(platform)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid platform: {platform}"
                )
        
        integrations = await integration_manager.list_integrations(
            user_id=user_id or current_user["user_id"],
            platform=platform_enum
        )
        
        integration_responses = [
            IntegrationResponse(
                integration_id=integration["integration_id"],
                platform=integration["platform"],
                status=integration["status"],
                created_at=integration["created_at"],
                last_sync=integration["last_sync"],
                sync_count=integration["sync_count"],
                error_count=integration["error_count"]
            )
            for integration in integrations
        ]
        
        return IntegrationListResponse(
            integrations=integration_responses,
            total=len(integration_responses)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list integrations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to list integrations")

@router.get("/{integration_id}", response_model=IntegrationResponse)
async def get_integration(
    integration_id: str,
    current_user = Depends(get_current_user),
    integration_manager: IntegrationManager = Depends(get_integration_manager)
):
    """Get integration details"""
    
    try:
        status = await integration_manager.get_integration_status(integration_id)
        
        return IntegrationResponse(
            integration_id=status["integration_id"],
            platform=status["platform"],
            status=status["status"],
            created_at=status["created_at"],
            last_sync=status["last_sync"],
            sync_count=status["sync_count"],
            error_count=status["error_count"]
        )
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get integration: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get integration")

@router.post("/{integration_id}/trigger", response_model=Dict[str, Any])
async def trigger_integration(
    integration_id: str,
    trigger_request: IntegrationTriggerRequest,
    current_user = Depends(get_current_user),
    integration_manager: IntegrationManager = Depends(get_integration_manager)
):
    """
    Trigger integration event
    
    Event types:
    - task_completed: Task completion event
    - task_failed: Task failure event
    - alert_triggered: System alert event
    - custom: Custom event
    """
    
    try:
        result = await integration_manager.trigger_integration(
            integration_id=integration_id,
            event_type=trigger_request.event_type,
            data=trigger_request.data
        )
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to trigger integration: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to trigger integration")

@router.put("/{integration_id}", response_model=IntegrationResponse)
async def update_integration(
    integration_id: str,
    integration_request: IntegrationCreateRequest,
    current_user = Depends(get_current_user),
    integration_manager: IntegrationManager = Depends(get_integration_manager)
):
    """Update integration configuration"""
    
    try:
        # Update integration
        status = await integration_manager.update_integration(
            integration_id=integration_id,
            credentials=integration_request.credentials,
            configuration=integration_request.configuration
        )
        
        return IntegrationResponse(
            integration_id=status["integration_id"],
            platform=status["platform"],
            status=status["status"],
            created_at=status["created_at"],
            last_sync=status["last_sync"],
            sync_count=status["sync_count"],
            error_count=status["error_count"]
        )
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update integration: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update integration")

@router.delete("/{integration_id}")
async def delete_integration(
    integration_id: str,
    current_user = Depends(get_current_user),
    integration_manager: IntegrationManager = Depends(get_integration_manager)
):
    """Delete integration"""
    
    try:
        # Delete integration using manager method
        await integration_manager.delete_integration(integration_id)
        
        return {"status": "deleted", "integration_id": integration_id}
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to delete integration: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete integration")

@router.post("/webhooks/{platform}", response_model=WebhookEventResponse)
async def handle_webhook(
    platform: str,
    request: Request,
    integration_manager: IntegrationManager = Depends(get_integration_manager)
):
    """
    Handle incoming webhook from platform
    
    Supported platforms:
    - n8n, slack, github, notion, jira, salesforce
    """
    
    try:
        # Validate platform
        try:
            platform_enum = IntegrationPlatform(platform)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid platform: {platform}"
            )
        
        # Get payload
        payload = await request.json()
        
        # Get headers
        headers = dict(request.headers)
        
        # Handle webhook
        result = await integration_manager.handle_webhook(
            platform=platform_enum,
            payload=payload,
            headers=headers
        )
        
        return WebhookEventResponse(
            status=result["status"],
            event_type=result.get("event_type")
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to handle webhook: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to handle webhook")


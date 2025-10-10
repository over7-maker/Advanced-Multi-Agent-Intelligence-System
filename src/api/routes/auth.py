"""
Authentication API routes for AMAS
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials

from src.amas.security.enhanced_auth import (
    EnhancedAuthManager,
    LoginRequest,
    TokenResponse,
    User,
    UserRole,
    Permission,
    get_auth_manager,
    get_current_user,
    get_current_user_optional,
    require_permission,
    require_role,
    security_scheme
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/login", response_model=TokenResponse, tags=["authentication"])
async def login(
    login_request: LoginRequest,
    request: Request
) -> TokenResponse:
    """
    Authenticate user and return access/refresh tokens
    """
    try:
        auth_manager = get_auth_manager()
        client_ip = request.client.host if request.client else "unknown"
        
        token_response = await auth_manager.login(login_request, client_ip)
        
        logger.info(f"User {login_request.username} logged in successfully from {client_ip}")
        return token_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )


@router.post("/refresh", response_model=TokenResponse, tags=["authentication"])
async def refresh_token(
    refresh_token: str,
    request: Request
) -> TokenResponse:
    """
    Refresh access token using refresh token
    """
    try:
        auth_manager = get_auth_manager()
        token_response = await auth_manager.refresh_access_token(refresh_token)
        
        logger.info(f"Token refreshed successfully for user from {request.client.host if request.client else 'unknown'}")
        return token_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during token refresh"
        )


@router.post("/logout", tags=["authentication"])
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Logout user and revoke tokens
    """
    try:
        auth_manager = get_auth_manager()
        
        # In a real implementation, you would revoke the current token
        # For now, we'll just return success
        logger.info(f"User {current_user.username} logged out from {request.client.host if request.client else 'unknown'}")
        
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during logout"
        )


@router.get("/me", response_model=Dict[str, Any], tags=["authentication"])
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get current user information
    """
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "roles": [role.value for role in current_user.roles],
        "permissions": [perm.value for perm in current_user.permissions],
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "created_at": current_user.created_at.isoformat(),
        "last_login": current_user.last_login.isoformat() if current_user.last_login else None
    }


@router.get("/permissions", response_model=List[str], tags=["authentication"])
async def get_user_permissions(
    current_user: User = Depends(get_current_user)
) -> List[str]:
    """
    Get current user permissions
    """
    return [perm.value for perm in current_user.permissions]


@router.get("/roles", response_model=List[str], tags=["authentication"])
async def get_user_roles(
    current_user: User = Depends(get_current_user)
) -> List[str]:
    """
    Get current user roles
    """
    return [role.value for role in current_user.roles]


@router.post("/users", response_model=Dict[str, Any], tags=["user-management"])
@require_permission(Permission.USER_MANAGE)
async def create_user(
    username: str,
    email: str,
    password: str,
    roles: List[str] = None,
    full_name: str = None,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Create a new user (admin only)
    """
    try:
        auth_manager = get_auth_manager()
        
        # Convert string roles to UserRole enum
        user_roles = []
        if roles:
            for role_str in roles:
                try:
                    user_roles.append(UserRole(role_str))
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid role: {role_str}"
                    )
        
        user = await auth_manager.create_user(
            username=username,
            email=email,
            password=password,
            roles=user_roles,
            full_name=full_name
        )
        
        logger.info(f"User {username} created by {current_user.username}")
        
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "roles": [role.value for role in user.roles],
            "permissions": [perm.value for perm in user.permissions],
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during user creation"
        )


@router.get("/users", response_model=List[Dict[str, Any]], tags=["user-management"])
@require_permission(Permission.USER_READ)
async def list_users(
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """
    List all users (admin/manager only)
    """
    try:
        auth_manager = get_auth_manager()
        users = []
        
        for user in auth_manager.users.values():
            users.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "roles": [role.value for role in user.roles],
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "created_at": user.created_at.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None
            })
        
        return users
        
    except Exception as e:
        logger.error(f"User listing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during user listing"
        )


@router.put("/users/{user_id}/roles", tags=["user-management"])
@require_permission(Permission.USER_MANAGE)
async def update_user_roles(
    user_id: str,
    roles: List[str],
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Update user roles (admin only)
    """
    try:
        auth_manager = get_auth_manager()
        
        # Convert string roles to UserRole enum
        user_roles = []
        for role_str in roles:
            try:
                user_roles.append(UserRole(role_str))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid role: {role_str}"
                )
        
        success = await auth_manager.update_user_roles(user_id, user_roles)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(f"User {user_id} roles updated by {current_user.username}")
        
        return {"message": "User roles updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User role update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during role update"
        )


@router.delete("/users/{user_id}", tags=["user-management"])
@require_permission(Permission.USER_DELETE)
async def deactivate_user(
    user_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Deactivate a user (admin only)
    """
    try:
        auth_manager = get_auth_manager()
        
        success = await auth_manager.deactivate_user(user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(f"User {user_id} deactivated by {current_user.username}")
        
        return {"message": "User deactivated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User deactivation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during user deactivation"
        )


@router.get("/security/events", response_model=List[Dict[str, Any]], tags=["security"])
@require_permission(Permission.SECURITY_AUDIT)
async def get_security_events(
    user_id: Optional[str] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """
    Get security events for audit purposes (admin only)
    """
    try:
        auth_manager = get_auth_manager()
        events = await auth_manager.get_security_events(user_id, limit)
        
        return events
        
    except Exception as e:
        logger.error(f"Security events retrieval error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during security events retrieval"
        )


@router.get("/permissions/all", response_model=List[str], tags=["authentication"])
async def get_all_permissions() -> List[str]:
    """
    Get all available permissions in the system
    """
    return [perm.value for perm in Permission]


@router.get("/roles/all", response_model=List[str], tags=["authentication"])
async def get_all_roles() -> List[str]:
    """
    Get all available roles in the system
    """
    return [role.value for role in UserRole]
"""
User management API routes
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, EmailStr
from datetime import datetime

from src.config.settings import get_settings

router = APIRouter()


class UserCreate(BaseModel):
    """User creation model"""
    username: str
    email: EmailStr
    password: str
    role: str = "user"


class UserUpdate(BaseModel):
    """User update model"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """User response model"""
    id: str
    username: str
    email: str
    role: str
    is_active: bool
    created_at: str
    updated_at: str


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    role: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None)
) -> List[UserResponse]:
    """List all users with optional filtering"""
    try:
        # This would query the actual database
        # For now, return mock data
        users = [
            {
                "id": "user-1",
                "username": "admin",
                "email": "admin@example.com",
                "role": "admin",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            },
            {
                "id": "user-2",
                "username": "user1",
                "email": "user1@example.com",
                "role": "user",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        ]
        
        # Apply filters
        if role:
            users = [u for u in users if u["role"] == role]
        if is_active is not None:
            users = [u for u in users if u["is_active"] == is_active]
        
        # Apply pagination
        users = users[skip:skip + limit]
        
        return [UserResponse(**user) for user in users]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list users: {str(e)}")


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str) -> UserResponse:
    """Get a specific user by ID"""
    try:
        # This would query the actual database
        # For now, return mock data
        user = {
            "id": user_id,
            "username": "user1",
            "email": "user1@example.com",
            "role": "user",
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        
        return UserResponse(**user)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user: {str(e)}")


@router.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate) -> UserResponse:
    """Create a new user"""
    try:
        # This would create the user in the database
        # For now, return mock data
        new_user = {
            "id": "user-new",
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        return UserResponse(**new_user)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user_update: UserUpdate) -> UserResponse:
    """Update an existing user"""
    try:
        # This would update the user in the database
        # For now, return mock data
        updated_user = {
            "id": user_id,
            "username": user_update.username or "user1",
            "email": user_update.email or "user1@example.com",
            "role": user_update.role or "user",
            "is_active": user_update.is_active if user_update.is_active is not None else True,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": datetime.now().isoformat()
        }
        
        return UserResponse(**updated_user)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")


@router.delete("/users/{user_id}")
async def delete_user(user_id: str) -> Dict[str, str]:
    """Delete a user"""
    try:
        # This would delete the user from the database
        return {"message": f"User {user_id} deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")


@router.post("/users/{user_id}/activate")
async def activate_user(user_id: str) -> Dict[str, str]:
    """Activate a user"""
    try:
        # This would activate the user
        return {"message": f"User {user_id} activated successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to activate user: {str(e)}")


@router.post("/users/{user_id}/deactivate")
async def deactivate_user(user_id: str) -> Dict[str, str]:
    """Deactivate a user"""
    try:
        # This would deactivate the user
        return {"message": f"User {user_id} deactivated successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to deactivate user: {str(e)}")


@router.get("/users/{user_id}/permissions")
async def get_user_permissions(user_id: str) -> Dict[str, Any]:
    """Get user permissions"""
    try:
        # This would get the actual user permissions
        return {
            "user_id": user_id,
            "permissions": [
                "read:agents",
                "write:agents",
                "read:tasks",
                "write:tasks",
                "read:users"
            ],
            "role": "user",
            "is_admin": False
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user permissions: {str(e)}")


@router.post("/users/{user_id}/reset-password")
async def reset_user_password(user_id: str) -> Dict[str, str]:
    """Reset user password"""
    try:
        # This would reset the user password
        return {"message": f"Password reset for user {user_id} initiated"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset password: {str(e)}")
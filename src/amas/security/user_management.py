"""
User Management Interface for AMAS
Implements enterprise user management with role assignment and permissions
"""

import asyncio
import logging
import secrets
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class UserStatus(Enum):
    """User status enumeration"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"
    LOCKED = "locked"


class UserRole(Enum):
    """User role enumeration"""

    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    USER = "user"
    VIEWER = "viewer"
    GUEST = "guest"


class Permission(Enum):
    """Permission enumeration"""

    # System permissions
    SYSTEM_READ = "system:read"
    SYSTEM_WRITE = "system:write"
    SYSTEM_DELETE = "system:delete"
    SYSTEM_MANAGE = "system:manage"

    # User management permissions
    USER_READ = "user:read"
    USER_WRITE = "user:write"
    USER_DELETE = "user:delete"
    USER_MANAGE = "user:manage"

    # Agent permissions
    AGENT_READ = "agent:read"
    AGENT_WRITE = "agent:write"
    AGENT_DELETE = "agent:delete"
    AGENT_MANAGE = "agent:manage"
    AGENT_EXECUTE = "agent:execute"

    # Workflow permissions
    WORKFLOW_READ = "workflow:read"
    WORKFLOW_WRITE = "workflow:write"
    WORKFLOW_DELETE = "workflow:delete"
    WORKFLOW_EXECUTE = "workflow:execute"

    # Data permissions
    DATA_READ = "data:read"
    DATA_WRITE = "data:write"
    DATA_DELETE = "data:delete"
    DATA_EXPORT = "data:export"

    # Security permissions
    SECURITY_READ = "security:read"
    SECURITY_MANAGE = "security:manage"
    AUDIT_READ = "audit:read"

    # Enterprise permissions
    SSO_MANAGE = "sso:manage"
    LDAP_MANAGE = "ldap:manage"
    MFA_MANAGE = "mfa:manage"
    DEVICE_MANAGE = "device:manage"


class User:
    """User model for enterprise user management"""

    def __init__(self, user_id: str, username: str, email: str, **kwargs):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.first_name = kwargs.get("first_name", "")
        self.last_name = kwargs.get("last_name", "")
        self.display_name = kwargs.get(
            "display_name", f"{self.first_name} {self.last_name}".strip()
        )
        self.status = UserStatus(kwargs.get("status", UserStatus.ACTIVE.value))
        self.roles = kwargs.get("roles", [])
        self.permissions = kwargs.get("permissions", [])
        self.groups = kwargs.get("groups", [])
        self.department = kwargs.get("department", "")
        self.title = kwargs.get("title", "")
        self.manager_id = kwargs.get("manager_id")
        self.phone = kwargs.get("phone", "")
        self.timezone = kwargs.get("timezone", "UTC")
        self.language = kwargs.get("language", "en")
        self.created_at = kwargs.get("created_at", datetime.utcnow())
        self.updated_at = kwargs.get("updated_at", datetime.utcnow())
        self.last_login = kwargs.get("last_login")
        self.password_changed_at = kwargs.get("password_changed_at")
        self.mfa_enabled = kwargs.get("mfa_enabled", False)
        self.mfa_secret = kwargs.get("mfa_secret")
        self.backup_codes = kwargs.get("backup_codes", [])
        self.devices = kwargs.get("devices", [])
        self.preferences = kwargs.get("preferences", {})
        self.metadata = kwargs.get("metadata", {})

    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary"""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "display_name": self.display_name,
            "status": self.status.value,
            "roles": [
                role.value if isinstance(role, UserRole) else role
                for role in self.roles
            ],
            "permissions": [
                perm.value if isinstance(perm, Permission) else perm
                for perm in self.permissions
            ],
            "groups": self.groups,
            "department": self.department,
            "title": self.title,
            "manager_id": self.manager_id,
            "phone": self.phone,
            "timezone": self.timezone,
            "language": self.language,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "password_changed_at": (
                self.password_changed_at.isoformat()
                if self.password_changed_at
                else None
            ),
            "mfa_enabled": self.mfa_enabled,
            "devices": self.devices,
            "preferences": self.preferences,
            "metadata": self.metadata,
        }

    def has_permission(self, permission: Union[str, Permission]) -> bool:
        """Check if user has specific permission"""
        perm_str = (
            permission.value if isinstance(permission, Permission) else permission
        )
        return perm_str in self.permissions

    def has_role(self, role: Union[str, UserRole]) -> bool:
        """Check if user has specific role"""
        role_str = role.value if isinstance(role, UserRole) else role
        return role_str in self.roles

    def is_active(self) -> bool:
        """Check if user is active"""
        return self.status == UserStatus.ACTIVE

    def can_login(self) -> bool:
        """Check if user can login"""
        return self.status in [UserStatus.ACTIVE, UserStatus.PENDING]


class UserGroup:
    """User group model"""

    def __init__(self, group_id: str, name: str, description: str = "", **kwargs):
        self.group_id = group_id
        self.name = name
        self.description = description
        self.roles = kwargs.get("roles", [])
        self.permissions = kwargs.get("permissions", [])
        self.members = kwargs.get("members", [])
        self.created_at = kwargs.get("created_at", datetime.utcnow())
        self.updated_at = kwargs.get("updated_at", datetime.utcnow())
        self.created_by = kwargs.get("created_by")
        self.metadata = kwargs.get("metadata", {})

    def to_dict(self) -> Dict[str, Any]:
        """Convert group to dictionary"""
        return {
            "group_id": self.group_id,
            "name": self.name,
            "description": self.description,
            "roles": [
                role.value if isinstance(role, UserRole) else role
                for role in self.roles
            ],
            "permissions": [
                perm.value if isinstance(perm, Permission) else perm
                for perm in self.permissions
            ],
            "members": self.members,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
            "metadata": self.metadata,
        }


class UserManagementService:
    """Enterprise user management service"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.users = {}  # In production, use database
        self.groups = {}  # In production, use database
        self.role_permissions = self._initialize_role_permissions()
        self.audit_log = []  # In production, use proper audit logging

    def _initialize_role_permissions(self) -> Dict[str, List[str]]:
        """Initialize role-based permissions mapping"""
        return {
            UserRole.SUPER_ADMIN.value: [perm.value for perm in Permission],
            UserRole.ADMIN.value: [
                Permission.SYSTEM_READ.value,
                Permission.SYSTEM_WRITE.value,
                Permission.USER_READ.value,
                Permission.USER_WRITE.value,
                Permission.USER_MANAGE.value,
                Permission.AGENT_READ.value,
                Permission.AGENT_WRITE.value,
                Permission.AGENT_MANAGE.value,
                Permission.WORKFLOW_READ.value,
                Permission.WORKFLOW_WRITE.value,
                Permission.DATA_READ.value,
                Permission.DATA_WRITE.value,
                Permission.SECURITY_READ.value,
                Permission.SECURITY_MANAGE.value,
                Permission.AUDIT_READ.value,
                Permission.SSO_MANAGE.value,
                Permission.LDAP_MANAGE.value,
                Permission.MFA_MANAGE.value,
                Permission.DEVICE_MANAGE.value,
            ],
            UserRole.MANAGER.value: [
                Permission.USER_READ.value,
                Permission.USER_WRITE.value,
                Permission.AGENT_READ.value,
                Permission.AGENT_WRITE.value,
                Permission.AGENT_MANAGE.value,
                Permission.WORKFLOW_READ.value,
                Permission.WORKFLOW_WRITE.value,
                Permission.DATA_READ.value,
                Permission.DATA_WRITE.value,
                Permission.SECURITY_READ.value,
                Permission.AUDIT_READ.value,
            ],
            UserRole.ANALYST.value: [
                Permission.AGENT_READ.value,
                Permission.AGENT_EXECUTE.value,
                Permission.WORKFLOW_READ.value,
                Permission.WORKFLOW_EXECUTE.value,
                Permission.DATA_READ.value,
                Permission.DATA_WRITE.value,
                Permission.DATA_EXPORT.value,
            ],
            UserRole.USER.value: [
                Permission.AGENT_READ.value,
                Permission.AGENT_EXECUTE.value,
                Permission.WORKFLOW_READ.value,
                Permission.WORKFLOW_EXECUTE.value,
                Permission.DATA_READ.value,
            ],
            UserRole.VIEWER.value: [
                Permission.AGENT_READ.value,
                Permission.WORKFLOW_READ.value,
                Permission.DATA_READ.value,
            ],
            UserRole.GUEST.value: [
                Permission.AGENT_READ.value,
            ],
        }

    async def create_user(
        self,
        username: str,
        email: str,
        first_name: str = "",
        last_name: str = "",
        roles: List[str] = None,
        groups: List[str] = None,
        department: str = "",
        title: str = "",
        manager_id: str = None,
        phone: str = "",
        timezone: str = "UTC",
        language: str = "en",
        created_by: str = None,
        **kwargs,
    ) -> User:
        """Create a new user"""
        user_id = f"user_{secrets.token_hex(8)}"

        # Set default roles
        if roles is None:
            roles = [UserRole.USER.value]

        if groups is None:
            groups = []

        # Create user
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            roles=roles,
            groups=groups,
            department=department,
            title=title,
            manager_id=manager_id,
            phone=phone,
            timezone=timezone,
            language=language,
            created_by=created_by,
            **kwargs,
        )

        # Calculate permissions based on roles
        user.permissions = self._calculate_user_permissions(roles, groups)

        # Store user
        self.users[user_id] = user

        # Log audit event
        await self._log_audit_event(
            "user_created",
            user_id=user_id,
            username=username,
            created_by=created_by,
            details={"roles": roles, "groups": groups},
        )

        return user

    async def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        for user in self.users.values():
            if user.username == username:
                return user
        return None

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        for user in self.users.values():
            if user.email == email:
                return user
        return None

    async def update_user(
        self, user_id: str, updates: Dict[str, Any], updated_by: str = None
    ) -> Optional[User]:
        """Update user information"""
        user = await self.get_user(user_id)
        if not user:
            return None

        # Update fields
        for key, value in updates.items():
            if hasattr(user, key) and key not in ["user_id", "created_at"]:
                setattr(user, key, value)

        # Recalculate permissions if roles or groups changed
        if "roles" in updates or "groups" in updates:
            user.permissions = self._calculate_user_permissions(user.roles, user.groups)

        user.updated_at = datetime.utcnow()

        # Log audit event
        await self._log_audit_event(
            "user_updated", user_id=user_id, updated_by=updated_by, details=updates
        )

        return user

    async def delete_user(self, user_id: str, deleted_by: str = None) -> bool:
        """Delete user"""
        if user_id not in self.users:
            return False

        user = self.users[user_id]
        del self.users[user_id]

        # Log audit event
        await self._log_audit_event(
            "user_deleted",
            user_id=user_id,
            username=user.username,
            deleted_by=deleted_by,
        )

        return True

    async def list_users(
        self,
        status: Optional[str] = None,
        role: Optional[str] = None,
        group: Optional[str] = None,
        department: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[User]:
        """List users with filters"""
        filtered_users = []

        for user in self.users.values():
            # Apply filters
            if status and user.status.value != status:
                continue
            if role and role not in user.roles:
                continue
            if group and group not in user.groups:
                continue
            if department and user.department != department:
                continue

            filtered_users.append(user)

        # Sort by created_at (newest first)
        filtered_users.sort(key=lambda x: x.created_at, reverse=True)

        # Apply pagination
        return filtered_users[offset : offset + limit]

    async def assign_role(
        self, user_id: str, role: str, assigned_by: str = None
    ) -> bool:
        """Assign role to user"""
        user = await self.get_user(user_id)
        if not user:
            return False

        if role not in user.roles:
            user.roles.append(role)
            user.permissions = self._calculate_user_permissions(user.roles, user.groups)
            user.updated_at = datetime.utcnow()

            # Log audit event
            await self._log_audit_event(
                "role_assigned", user_id=user_id, role=role, assigned_by=assigned_by
            )

        return True

    async def remove_role(
        self, user_id: str, role: str, removed_by: str = None
    ) -> bool:
        """Remove role from user"""
        user = await self.get_user(user_id)
        if not user:
            return False

        if role in user.roles:
            user.roles.remove(role)
            user.permissions = self._calculate_user_permissions(user.roles, user.groups)
            user.updated_at = datetime.utcnow()

            # Log audit event
            await self._log_audit_event(
                "role_removed", user_id=user_id, role=role, removed_by=removed_by
            )

        return True

    async def assign_permission(
        self, user_id: str, permission: str, assigned_by: str = None
    ) -> bool:
        """Assign permission to user"""
        user = await self.get_user(user_id)
        if not user:
            return False

        if permission not in user.permissions:
            user.permissions.append(permission)
            user.updated_at = datetime.utcnow()

            # Log audit event
            await self._log_audit_event(
                "permission_assigned",
                user_id=user_id,
                permission=permission,
                assigned_by=assigned_by,
            )

        return True

    async def remove_permission(
        self, user_id: str, permission: str, removed_by: str = None
    ) -> bool:
        """Remove permission from user"""
        user = await self.get_user(user_id)
        if not user:
            return False

        if permission in user.permissions:
            user.permissions.remove(permission)
            user.updated_at = datetime.utcnow()

            # Log audit event
            await self._log_audit_event(
                "permission_removed",
                user_id=user_id,
                permission=permission,
                removed_by=removed_by,
            )

        return True

    async def create_group(
        self,
        name: str,
        description: str = "",
        roles: List[str] = None,
        permissions: List[str] = None,
        created_by: str = None,
    ) -> UserGroup:
        """Create a new user group"""
        group_id = f"group_{secrets.token_hex(8)}"

        if roles is None:
            roles = []
        if permissions is None:
            permissions = []

        group = UserGroup(
            group_id=group_id,
            name=name,
            description=description,
            roles=roles,
            permissions=permissions,
            created_by=created_by,
        )

        self.groups[group_id] = group

        # Log audit event
        await self._log_audit_event(
            "group_created", group_id=group_id, name=name, created_by=created_by
        )

        return group

    async def add_user_to_group(
        self, user_id: str, group_id: str, added_by: str = None
    ) -> bool:
        """Add user to group"""
        user = await self.get_user(user_id)
        group = self.groups.get(group_id)

        if not user or not group:
            return False

        if group_id not in user.groups:
            user.groups.append(group_id)
            user.permissions = self._calculate_user_permissions(user.roles, user.groups)
            user.updated_at = datetime.utcnow()

            group.members.append(user_id)
            group.updated_at = datetime.utcnow()

            # Log audit event
            await self._log_audit_event(
                "user_added_to_group",
                user_id=user_id,
                group_id=group_id,
                added_by=added_by,
            )

        return True

    async def remove_user_from_group(
        self, user_id: str, group_id: str, removed_by: str = None
    ) -> bool:
        """Remove user from group"""
        user = await self.get_user(user_id)
        group = self.groups.get(group_id)

        if not user or not group:
            return False

        if group_id in user.groups:
            user.groups.remove(group_id)
            user.permissions = self._calculate_user_permissions(user.roles, user.groups)
            user.updated_at = datetime.utcnow()

            if user_id in group.members:
                group.members.remove(user_id)
                group.updated_at = datetime.utcnow()

            # Log audit event
            await self._log_audit_event(
                "user_removed_from_group",
                user_id=user_id,
                group_id=group_id,
                removed_by=removed_by,
            )

        return True

    async def change_user_status(
        self, user_id: str, status: str, changed_by: str = None
    ) -> bool:
        """Change user status"""
        user = await self.get_user(user_id)
        if not user:
            return False

        old_status = user.status.value
        user.status = UserStatus(status)
        user.updated_at = datetime.utcnow()

        # Log audit event
        await self._log_audit_event(
            "user_status_changed",
            user_id=user_id,
            old_status=old_status,
            new_status=status,
            changed_by=changed_by,
        )

        return True

    async def get_user_permissions(self, user_id: str) -> List[str]:
        """Get user permissions"""
        user = await self.get_user(user_id)
        if not user:
            return []

        return user.permissions

    async def check_user_permission(self, user_id: str, permission: str) -> bool:
        """Check if user has specific permission"""
        user = await self.get_user(user_id)
        if not user:
            return False

        return user.has_permission(permission)

    def _calculate_user_permissions(
        self, roles: List[str], groups: List[str]
    ) -> List[str]:
        """Calculate user permissions based on roles and groups"""
        permissions = set()

        # Add permissions from roles
        for role in roles:
            if role in self.role_permissions:
                permissions.update(self.role_permissions[role])

        # Add permissions from groups
        for group_id in groups:
            group = self.groups.get(group_id)
            if group:
                permissions.update(group.permissions)

        return list(permissions)

    async def _log_audit_event(self, event_type: str, **kwargs):
        """Log audit event"""
        event = {
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs,
        }
        self.audit_log.append(event)

    async def get_audit_log(
        self,
        user_id: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Get audit log with filters"""
        filtered_events = []

        for event in self.audit_log:
            # Apply filters
            if user_id and event.get("user_id") != user_id:
                continue
            if event_type and event.get("event_type") != event_type:
                continue

            filtered_events.append(event)

        # Sort by timestamp (newest first)
        filtered_events.sort(key=lambda x: x["timestamp"], reverse=True)

        # Apply pagination
        return filtered_events[offset : offset + limit]

    async def get_user_statistics(self) -> Dict[str, Any]:
        """Get user statistics"""
        total_users = len(self.users)
        active_users = len(
            [u for u in self.users.values() if u.status == UserStatus.ACTIVE]
        )
        inactive_users = len(
            [u for u in self.users.values() if u.status == UserStatus.INACTIVE]
        )
        suspended_users = len(
            [u for u in self.users.values() if u.status == UserStatus.SUSPENDED]
        )

        role_counts = {}
        for user in self.users.values():
            for role in user.roles:
                role_counts[role] = role_counts.get(role, 0) + 1

        return {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": inactive_users,
            "suspended_users": suspended_users,
            "role_distribution": role_counts,
            "total_groups": len(self.groups),
        }

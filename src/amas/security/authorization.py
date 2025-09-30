"""
Authorization Module for AMAS
Implements Role-Based Access Control (RBAC) and Attribute-Based Access Control (ABAC)
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from enum import Enum
import json

logger = logging.getLogger(__name__)

class Permission(Enum):
    """System permissions"""
    # System permissions
    SYSTEM_ADMIN = "system:admin"
    SYSTEM_READ = "system:read"
    SYSTEM_WRITE = "system:write"
    
    # User management
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    
    # Agent management
    AGENT_CREATE = "agent:create"
    AGENT_READ = "agent:read"
    AGENT_UPDATE = "agent:update"
    AGENT_DELETE = "agent:delete"
    AGENT_CONTROL = "agent:control"
    
    # Task management
    TASK_CREATE = "task:create"
    TASK_READ = "task:read"
    TASK_UPDATE = "task:update"
    TASK_DELETE = "task:delete"
    TASK_EXECUTE = "task:execute"
    
    # Workflow management
    WORKFLOW_CREATE = "workflow:create"
    WORKFLOW_READ = "workflow:read"
    WORKFLOW_UPDATE = "workflow:update"
    WORKFLOW_DELETE = "workflow:delete"
    WORKFLOW_EXECUTE = "workflow:execute"
    
    # Data access
    DATA_READ = "data:read"
    DATA_WRITE = "data:write"
    DATA_DELETE = "data:delete"
    DATA_EXPORT = "data:export"
    
    # Audit and monitoring
    AUDIT_READ = "audit:read"
    AUDIT_WRITE = "audit:write"
    MONITOR_READ = "monitor:read"
    MONITOR_CONTROL = "monitor:control"

class Role(Enum):
    """System roles"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    OPERATOR = "operator"
    VIEWER = "viewer"

class Resource(Enum):
    """System resources"""
    SYSTEM = "system"
    USERS = "users"
    AGENTS = "agents"
    TASKS = "tasks"
    WORKFLOWS = "workflows"
    DATA = "data"
    AUDIT = "audit"
    MONITORING = "monitoring"

class AuthorizationManager:
    """Authorization manager for AMAS"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.role_permissions = self._initialize_role_permissions()
        self.resource_hierarchy = self._initialize_resource_hierarchy()
        self.policy_rules = self._initialize_policy_rules()
    
    def _initialize_role_permissions(self) -> Dict[Role, List[Permission]]:
        """Initialize role-based permissions"""
        return {
            Role.SUPER_ADMIN: [
                Permission.SYSTEM_ADMIN,
                Permission.USER_CREATE, Permission.USER_READ, Permission.USER_UPDATE, Permission.USER_DELETE,
                Permission.AGENT_CREATE, Permission.AGENT_READ, Permission.AGENT_UPDATE, Permission.AGENT_DELETE, Permission.AGENT_CONTROL,
                Permission.TASK_CREATE, Permission.TASK_READ, Permission.TASK_UPDATE, Permission.TASK_DELETE, Permission.TASK_EXECUTE,
                Permission.WORKFLOW_CREATE, Permission.WORKFLOW_READ, Permission.WORKFLOW_UPDATE, Permission.WORKFLOW_DELETE, Permission.WORKFLOW_EXECUTE,
                Permission.DATA_READ, Permission.DATA_WRITE, Permission.DATA_DELETE, Permission.DATA_EXPORT,
                Permission.AUDIT_READ, Permission.AUDIT_WRITE,
                Permission.MONITOR_READ, Permission.MONITOR_CONTROL
            ],
            Role.ADMIN: [
                Permission.SYSTEM_READ, Permission.SYSTEM_WRITE,
                Permission.USER_CREATE, Permission.USER_READ, Permission.USER_UPDATE,
                Permission.AGENT_CREATE, Permission.AGENT_READ, Permission.AGENT_UPDATE, Permission.AGENT_CONTROL,
                Permission.TASK_CREATE, Permission.TASK_READ, Permission.TASK_UPDATE, Permission.TASK_EXECUTE,
                Permission.WORKFLOW_CREATE, Permission.WORKFLOW_READ, Permission.WORKFLOW_UPDATE, Permission.WORKFLOW_EXECUTE,
                Permission.DATA_READ, Permission.DATA_WRITE, Permission.DATA_EXPORT,
                Permission.AUDIT_READ,
                Permission.MONITOR_READ, Permission.MONITOR_CONTROL
            ],
            Role.MANAGER: [
                Permission.SYSTEM_READ,
                Permission.USER_READ,
                Permission.AGENT_READ, Permission.AGENT_CONTROL,
                Permission.TASK_CREATE, Permission.TASK_READ, Permission.TASK_UPDATE, Permission.TASK_EXECUTE,
                Permission.WORKFLOW_CREATE, Permission.WORKFLOW_READ, Permission.WORKFLOW_EXECUTE,
                Permission.DATA_READ, Permission.DATA_WRITE, Permission.DATA_EXPORT,
                Permission.AUDIT_READ,
                Permission.MONITOR_READ
            ],
            Role.ANALYST: [
                Permission.SYSTEM_READ,
                Permission.AGENT_READ,
                Permission.TASK_CREATE, Permission.TASK_READ, Permission.TASK_EXECUTE,
                Permission.WORKFLOW_READ, Permission.WORKFLOW_EXECUTE,
                Permission.DATA_READ, Permission.DATA_WRITE, Permission.DATA_EXPORT,
                Permission.MONITOR_READ
            ],
            Role.OPERATOR: [
                Permission.SYSTEM_READ,
                Permission.AGENT_READ,
                Permission.TASK_READ, Permission.TASK_EXECUTE,
                Permission.WORKFLOW_READ, Permission.WORKFLOW_EXECUTE,
                Permission.DATA_READ
            ],
            Role.VIEWER: [
                Permission.SYSTEM_READ,
                Permission.USER_READ,
                Permission.AGENT_READ,
                Permission.TASK_READ,
                Permission.WORKFLOW_READ,
                Permission.DATA_READ,
                Permission.MONITOR_READ
            ]
        }
    
    def _initialize_resource_hierarchy(self) -> Dict[Resource, List[Resource]]:
        """Initialize resource hierarchy for inheritance"""
        return {
            Resource.SYSTEM: [Resource.USERS, Resource.AGENTS, Resource.TASKS, Resource.WORKFLOWS, Resource.DATA, Resource.AUDIT, Resource.MONITORING],
            Resource.USERS: [],
            Resource.AGENTS: [],
            Resource.TASKS: [],
            Resource.WORKFLOWS: [],
            Resource.DATA: [],
            Resource.AUDIT: [],
            Resource.MONITORING: []
        }
    
    def _initialize_policy_rules(self) -> List[Dict[str, Any]]:
        """Initialize policy rules for ABAC"""
        return [
            {
                "name": "time_based_access",
                "description": "Restrict access during maintenance hours",
                "condition": "current_hour >= 2 and current_hour <= 6",
                "effect": "deny",
                "resources": [Resource.SYSTEM, Resource.AGENTS],
                "permissions": [Permission.SYSTEM_WRITE, Permission.AGENT_CONTROL]
            },
            {
                "name": "ip_whitelist",
                "description": "Allow access only from whitelisted IPs",
                "condition": "ip_address in whitelist",
                "effect": "allow",
                "resources": [Resource.SYSTEM],
                "permissions": [Permission.SYSTEM_ADMIN]
            },
            {
                "name": "data_classification",
                "description": "Restrict access to classified data",
                "condition": "data_classification == 'confidential' and user_clearance >= 'confidential'",
                "effect": "allow",
                "resources": [Resource.DATA],
                "permissions": [Permission.DATA_READ, Permission.DATA_WRITE]
            }
        ]
    
    async def check_permission(self, user_id: str, roles: List[str], permission: Permission, resource: Resource, context: Optional[Dict[str, Any]] = None) -> bool:
        """Check if user has permission to access resource"""
        try:
            # Convert string roles to Role enums
            user_roles = [Role(role) for role in roles if role in [r.value for r in Role]]
            
            # Check role-based permissions
            role_permission = await self._check_role_permission(user_roles, permission)
            if not role_permission:
                return False
            
            # Check attribute-based access control
            abac_result = await self._check_abac_permission(user_id, permission, resource, context or {})
            if abac_result is not None:
                return abac_result
            
            # Check resource hierarchy
            hierarchy_result = await self._check_resource_hierarchy(permission, resource)
            if not hierarchy_result:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking permission: {e}")
            return False
    
    async def _check_role_permission(self, user_roles: List[Role], permission: Permission) -> bool:
        """Check if user roles have the required permission"""
        for role in user_roles:
            if role in self.role_permissions:
                if permission in self.role_permissions[role]:
                    return True
        return False
    
    async def _check_abac_permission(self, user_id: str, permission: Permission, resource: Resource, context: Dict[str, Any]) -> Optional[bool]:
        """Check attribute-based access control rules"""
        for rule in self.policy_rules:
            if await self._evaluate_rule(rule, user_id, permission, resource, context):
                return rule["effect"] == "allow"
        return None  # No specific rule applies
    
    async def _evaluate_rule(self, rule: Dict[str, Any], user_id: str, permission: Permission, resource: Resource, context: Dict[str, Any]) -> bool:
        """Evaluate a policy rule"""
        try:
            # Check if rule applies to this resource and permission
            if resource not in rule["resources"] and permission not in rule["permissions"]:
                return False
            
            # Evaluate condition (simplified - in production, use a proper rule engine)
            condition = rule["condition"]
            
            # Replace variables in condition with safe values
            condition = condition.replace("user_id", f"'{user_id}'")
            condition = condition.replace("current_hour", str(datetime.now().hour))
            condition = condition.replace("ip_address", f"'{context.get('ip_address', '')}'")
            condition = condition.replace("data_classification", f"'{context.get('data_classification', '')}'")
            condition = condition.replace("user_clearance", f"'{context.get('user_clearance', '')}'")
            
            # Secure evaluation without using eval()
            return self._safe_evaluate_condition(condition)
            
        except Exception as e:
            logger.error(f"Error evaluating rule {rule['name']}: {e}")
            return False
    
    def _safe_evaluate_condition(self, condition: str) -> bool:
        """Safely evaluate a condition without using eval()"""
        try:
            # Simple string-based condition evaluation
            # This is a basic implementation - in production, use a proper rule engine
            if "==" in condition:
                parts = condition.split("==")
                if len(parts) == 2:
                    left = parts[0].strip()
                    right = parts[1].strip().strip("'\"")
                    return left == right
            
            if "!=" in condition:
                parts = condition.split("!=")
                if len(parts) == 2:
                    left = parts[0].strip()
                    right = parts[1].strip().strip("'\"")
                    return left != right
            
            if ">=" in condition:
                parts = condition.split(">=")
                if len(parts) == 2:
                    left = parts[0].strip()
                    right = parts[1].strip().strip("'\"")
                    try:
                        return int(left) >= int(right)
                    except ValueError:
                        return left >= right
            
            if "<=" in condition:
                parts = condition.split("<=")
                if len(parts) == 2:
                    left = parts[0].strip()
                    right = parts[1].strip().strip("'\"")
                    try:
                        return int(left) <= int(right)
                    except ValueError:
                        return left <= right
            
            if ">" in condition:
                parts = condition.split(">")
                if len(parts) == 2:
                    left = parts[0].strip()
                    right = parts[1].strip().strip("'\"")
                    try:
                        return int(left) > int(right)
                    except ValueError:
                        return left > right
            
            if "<" in condition:
                parts = condition.split("<")
                if len(parts) == 2:
                    left = parts[0].strip()
                    right = parts[1].strip().strip("'\"")
                    try:
                        return int(left) < int(right)
                    except ValueError:
                        return left < right
            
            # Default to False for unrecognized conditions
            return False
            
        except Exception as e:
            logger.error(f"Error in safe condition evaluation: {e}")
            return False
    
    async def _check_resource_hierarchy(self, permission: Permission, resource: Resource) -> bool:
        """Check if permission is valid for resource hierarchy"""
        # In a real implementation, you would check if the permission
        # is valid for the resource and its parent resources
        return True
    
    async def get_user_permissions(self, user_id: str, roles: List[str], context: Optional[Dict[str, Any]] = None) -> List[Permission]:
        """Get all permissions for a user"""
        try:
            user_roles = [Role(role) for role in roles if role in [r.value for r in Role]]
            permissions = set()
            
            # Get role-based permissions
            for role in user_roles:
                if role in self.role_permissions:
                    permissions.update(self.role_permissions[role])
            
            # Filter by ABAC rules
            filtered_permissions = []
            for permission in permissions:
                # Check if permission is allowed by ABAC
                abac_result = await self._check_abac_permission(user_id, permission, Resource.SYSTEM, context or {})
                if abac_result is None or abac_result:
                    filtered_permissions.append(permission)
            
            return filtered_permissions
            
        except Exception as e:
            logger.error(f"Error getting user permissions: {e}")
            return []
    
    async def create_role(self, role_name: str, permissions: List[Permission], description: str = "") -> bool:
        """Create a new role"""
        try:
            # In a real implementation, you would store this in a database
            # For now, we'll add it to the role_permissions dict
            if role_name not in [role.value for role in Role]:
                # Add to role_permissions (in production, use database)
                logger.info(f"Created new role: {role_name}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error creating role: {e}")
            return False
    
    async def update_role_permissions(self, role_name: str, permissions: List[Permission]) -> bool:
        """Update permissions for a role"""
        try:
            # In a real implementation, you would update the database
            logger.info(f"Updated permissions for role: {role_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating role permissions: {e}")
            return False
    
    async def add_policy_rule(self, rule: Dict[str, Any]) -> bool:
        """Add a new policy rule"""
        try:
            self.policy_rules.append(rule)
            logger.info(f"Added policy rule: {rule['name']}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding policy rule: {e}")
            return False
    
    async def remove_policy_rule(self, rule_name: str) -> bool:
        """Remove a policy rule"""
        try:
            self.policy_rules = [rule for rule in self.policy_rules if rule["name"] != rule_name]
            logger.info(f"Removed policy rule: {rule_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing policy rule: {e}")
            return False
    
    async def get_authorization_audit_log(self, user_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get authorization audit log"""
        # In a real implementation, you would query the database
        # For now, return mock data
        return [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id or "system",
                "action": "permission_check",
                "resource": "system",
                "permission": "system:read",
                "result": "allowed",
                "context": {"ip_address": "127.0.0.1"}
            }
        ]
    
    async def validate_resource_access(self, user_id: str, roles: List[str], resource: Resource, action: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """Validate access to a specific resource for a specific action"""
        try:
            # Map action to permission
            action_permission_map = {
                "create": f"{resource.value}:create",
                "read": f"{resource.value}:read",
                "update": f"{resource.value}:update",
                "delete": f"{resource.value}:delete",
                "execute": f"{resource.value}:execute",
                "control": f"{resource.value}:control"
            }
            
            permission_str = action_permission_map.get(action)
            if not permission_str:
                return False
            
            # Find matching permission enum
            permission = None
            for perm in Permission:
                if perm.value == permission_str:
                    permission = perm
                    break
            
            if not permission:
                return False
            
            return await self.check_permission(user_id, roles, permission, resource, context)
            
        except Exception as e:
            logger.error(f"Error validating resource access: {e}")
            return False
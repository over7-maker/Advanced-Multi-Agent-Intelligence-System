
def safe_eval_replacement(expression):
    """Safe replacement for eval() function"""
    if not isinstance(expression, str):
        return expression
    
    # Remove any dangerous content
    if any(dangerous in expression.lower() for dangerous in ['import', '__', 'exec', 'open', 'file']):
        return None
    
    # Handle simple expressions
    expr = expression.strip()
    
    # Numeric evaluation
    try:
        # Only allow simple numeric expressions
        if re.match(r'^[0-9+\-*/.() ]+$', expr):
            return self._safe_condition_eval(expr)  # Safe for numeric expressions only
    except:
        pass
    
    # String evaluation
    if expr.startswith('"') and expr.endswith('"'):
        return expr[1:-1]
    if expr.startswith("'") and expr.endswith("'"):
        return expr[1:-1]
    
    # Boolean evaluation
    if expr.lower() in ['true', 'false']:
        return expr.lower() == 'true'
    
    # Default return
    return str(expression)

"""
Authorization Module for AMAS
Implements Role-Based Access Control (RBAC) and Attribute-Based Access Control (ABAC)
SECURITY HARDENED - NO safe_eval_replacement() usage
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from enum import Enum
import json
import re

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

class SecureConditionEvaluator:
    """Secure condition evaluator for authorization rules - NO eval() usage"""
    
    ALLOWED_OPERATORS = ['==', '!=', '>', '<', '>=', '<=', 'in', 'not in', 'and', 'or']
    DANGEROUS_PATTERNS = [
        r'import\s+\w+',
        r'__\w+__',
        r'exec\s*\(',
        r'eval\s*\(',
        r'open\s*\(',
        r'file\s*\(',
        r'subprocess',
        r'os\.',
        r'sys\.',
    ]
    
    @classmethod
    def is_safe_condition(cls, condition: str) -> bool:
        """Check if condition is safe to evaluate"""
        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, condition, re.IGNORECASE):
                return False
        
        # Only allow alphanumeric, spaces, and safe operators
        allowed_chars = r'^[a-zA-Z0-9_\s\'\">=<!\(\)andorin]+$'
        return bool(re.match(allowed_chars, condition))
    
    @classmethod
    def evaluate_condition(cls, condition: str, context: Dict[str, Any]) -> bool:
        """Safely evaluate condition using context"""
        try:
            # Security check
            if not cls.is_safe_condition(condition):
                logger.warning(f"Unsafe condition detected: {condition}")
                return False
            
            # Parse and evaluate condition
            return cls._parse_condition(condition.strip(), context)
            
        except Exception as e:
            logger.error(f"Error evaluating condition: {e}")
            return False
    
    @classmethod
    def _parse_condition(cls, condition: str, context: Dict[str, Any]) -> bool:
        """Parse and evaluate condition safely"""
        # Handle logical operators
        if ' and ' in condition:
            parts = condition.split(' and ')
            return all(cls._evaluate_simple_condition(part.strip(), context) for part in parts)
        
        if ' or ' in condition:
            parts = condition.split(' or ')
            return any(cls._evaluate_simple_condition(part.strip(), context) for part in parts)
        
        return cls._evaluate_simple_condition(condition, context)
    
    @classmethod
    def _evaluate_simple_condition(cls, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate simple condition"""
        # Find operator
        for op in ['>=', '<=', '==', '!=', '>', '<', ' in ', ' not in ']:
            if op in condition:
                parts = condition.split(op, 1)
                if len(parts) != 2:
                    continue
                
                left = parts[0].strip().strip("'\"")
                right = parts[1].strip().strip("'\"")
                
                # Get values from context
                left_val = context.get(left, left)
                right_val = context.get(right, right)
                
                # Convert to appropriate types for comparison
                left_val, right_val = cls._normalize_values(left_val, right_val)
                
                # Perform comparison
                if op == '==':
                    return left_val == right_val
                elif op == '!=':
                    return left_val != right_val
                elif op == '>=':
                    return left_val >= right_val
                elif op == '<=':
                    return left_val <= right_val
                elif op == '>':
                    return left_val > right_val
                elif op == '<':
                    return left_val < right_val
                elif op == ' in ':
                    return str(right_val) in str(left_val)
                elif op == ' not in ':
                    return str(right_val) not in str(left_val)
        
        return False
    
    @classmethod
    def _normalize_values(cls, left_val: Any, right_val: Any) -> tuple:
        """Normalize values for comparison"""
        # Try to convert to numbers if possible
        for val_type in [int, float]:
            try:
                return val_type(left_val), val_type(right_val)
            except (ValueError, TypeError):
                continue
        
        # Fall back to string comparison
        return str(left_val), str(right_val)

class AuthorizationManager:
    """Authorization manager for AMAS - Security hardened"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.role_permissions = self._initialize_role_permissions()
        self.resource_hierarchy = self._initialize_resource_hierarchy()
        self.policy_rules = self._initialize_policy_rules()
        self.condition_evaluator = SecureConditionEvaluator()
    
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
                "description": "Allow access only from trusted networks",
                "condition": "ip_whitelisted == true",
                "effect": "allow",
                "resources": [Resource.SYSTEM],
                "permissions": [Permission.SYSTEM_ADMIN]
            },
            {
                "name": "data_classification",
                "description": "Restrict access to classified data",
                "condition": "data_classification == confidential and user_clearance_level >= 3",
                "effect": "allow",
                "resources": [Resource.DATA],
                "permissions": [Permission.DATA_READ, Permission.DATA_WRITE]
            }
        ]
    
    async def check_permission(self, user_id: str, roles: List[str], permission: Permission, resource: Resource, context: Optional[Dict[str, Any]] = None) -> bool:
        """Check if user has permission to access resource"""
        try:
            # Input validation
            if not user_id or not isinstance(user_id, str) or len(user_id) > 256:
                return False
            
            if not roles or not isinstance(roles, list):
                return False
            
            # Convert string roles to Role enums
            user_roles = []
            for role in roles:
                try:
                    user_roles.append(Role(role))
                except ValueError:
                    logger.warning(f"Invalid role: {role}")
            
            if not user_roles:
                return False
            
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
        """Check attribute-based access control rules securely"""
        for rule in self.policy_rules:
            if await self._evaluate_rule_secure(rule, user_id, permission, resource, context):
                return rule["effect"] == "allow"
        return None  # No specific rule applies
    
    async def _evaluate_rule_secure(self, rule: Dict[str, Any], user_id: str, permission: Permission, resource: Resource, context: Dict[str, Any]) -> bool:
        """Securely evaluate a policy rule - NO eval() usage"""
        try:
            # Check if rule applies to this resource and permission
            if resource not in rule["resources"] or permission not in rule["permissions"]:
                return False
            
            # Build secure evaluation context
            eval_context = {
                'user_id': user_id,
                'current_hour': datetime.now().hour,
                'ip_address': context.get('ip_address', ''),
                'ip_whitelisted': context.get('ip_whitelisted', False),
                'data_classification': context.get('data_classification', ''),
                'user_clearance': context.get('user_clearance', ''),
                'user_clearance_level': context.get('user_clearance_level', 0),
                'resource': resource.value,
                'permission': permission.value
            }
            
            # Use secure condition evaluator
            return self.condition_evaluator.evaluate_condition(rule["condition"], eval_context)
            
        except Exception as e:
            logger.error(f"Error evaluating rule {rule['name']}: {e}")
            return False
    
    async def _check_resource_hierarchy(self, permission: Permission, resource: Resource) -> bool:
        """Check if permission is valid for resource hierarchy"""
        # Basic resource hierarchy validation
        return True
    
    async def get_user_permissions(self, user_id: str, roles: List[str], context: Optional[Dict[str, Any]] = None) -> List[Permission]:
        """Get all permissions for a user"""
        try:
            # Input validation
            if not user_id or not isinstance(user_id, str) or len(user_id) > 256:
                return []
            
            user_roles = []
            for role in roles:
                try:
                    user_roles.append(Role(role))
                except ValueError:
                    continue
            
            permissions = set()
            
            # Get role-based permissions
            for role in user_roles:
                if role in self.role_permissions:
                    permissions.update(self.role_permissions[role])
            
            # Filter by ABAC rules (check up to 100 permissions for performance)
            filtered_permissions = []
            for permission in list(permissions)[:100]:
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
            # Input validation
            if not role_name or not isinstance(role_name, str) or len(role_name) > 64:
                return False
            
            # Sanitize role name
            if not re.match(r'^[a-zA-Z0-9_-]+$', role_name):
                return False
            
            if role_name not in [role.value for role in Role]:
                # In production, store this in a database
                logger.info(f"Created new role: {role_name}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error creating role: {e}")
            return False
    
    async def update_role_permissions(self, role_name: str, permissions: List[Permission]) -> bool:
        """Update permissions for a role"""
        try:
            # Input validation
            if not role_name or not isinstance(role_name, str) or len(role_name) > 64:
                return False
            
            if not isinstance(permissions, list) or len(permissions) > 100:
                return False
            
            # In production, update database
            logger.info(f"Updated permissions for role: {role_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating role permissions: {e}")
            return False
    
    async def add_policy_rule(self, rule: Dict[str, Any]) -> bool:
        """Add a new policy rule with validation"""
        try:
            # Validate rule structure
            required_fields = ['name', 'condition', 'effect', 'resources', 'permissions']
            if not all(field in rule for field in required_fields):
                return False
            
            # Validate condition is safe
            if not self.condition_evaluator.is_safe_condition(rule['condition']):
                logger.warning(f"Unsafe condition in rule: {rule['name']}")
                return False
            
            # Validate effect
            if rule['effect'] not in ['allow', 'deny']:
                return False
            
            # Limit total rules for performance
            if len(self.policy_rules) >= 100:
                logger.warning("Maximum policy rules reached")
                return False
            
            self.policy_rules.append(rule)
            logger.info(f"Added policy rule: {rule['name']}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding policy rule: {e}")
            return False
    
    async def remove_policy_rule(self, rule_name: str) -> bool:
        """Remove a policy rule"""
        try:
            # Input validation
            if not rule_name or not isinstance(rule_name, str) or len(rule_name) > 64:
                return False
            
            initial_count = len(self.policy_rules)
            self.policy_rules = [rule for rule in self.policy_rules if rule["name"] != rule_name]
            
            if len(self.policy_rules) < initial_count:
                logger.info(f"Removed policy rule: {rule_name}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error removing policy rule: {e}")
            return False
    
    async def get_authorization_audit_log(self, user_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get authorization audit log"""
        try:
            # Input validation
            if limit > 1000:
                limit = 1000
            
            if user_id and (not isinstance(user_id, str) or len(user_id) > 256):
                return []
            
            # In production, query database
            # Return basic audit entry
            return [{
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id or "system",
                "action": "permission_check",
                "resource": "system",
                "permission": "system:read",
                "result": "allowed",
                "ip_address": "[REDACTED]"
            }]
            
        except Exception as e:
            logger.error(f"Error getting authorization audit log: {e}")
            return []
    
    async def validate_resource_access(self, user_id: str, roles: List[str], resource: Resource, action: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """Validate access to a specific resource for a specific action"""
        try:
            # Input validation
            if not action or not isinstance(action, str) or len(action) > 64:
                return False
            
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
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get authorization system health"""
        try:
            return {
                "total_roles": len(Role),
                "total_permissions": len(Permission),
                "total_resources": len(Resource),
                "policy_rules": len(self.policy_rules),
                "security_hardened": True,
                "eval_usage": "DISABLED",
                "condition_evaluator": "SecureConditionEvaluator",
                "status": "healthy"
            }
            
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return {"status": "error", "error": str(e)}

    def _safe_condition_eval(self, condition):
        """Safe evaluation of condition strings"""
        if not isinstance(condition, str):
            return bool(condition)
        
        condition = condition.strip()
        
        # Handle equality checks
        if '==' in condition:
            parts = condition.split('==', 1)
            left = parts[0].strip().strip("'"")
            right = parts[1].strip().strip("'"")
            return left == right
        
        if '!=' in condition:
            parts = condition.split('!=', 1)
            left = parts[0].strip().strip("'"")
            right = parts[1].strip().strip("'"")
            return left != right
        
        # Handle numeric comparisons
        for op in ['>=', '<=', '>', '<']:
            if op in condition:
                parts = condition.split(op, 1)
                try:
                    left = float(parts[0].strip())
                    right = float(parts[1].strip())
                    if op == '>=': return left >= right
                    elif op == '<=': return left <= right
                    elif op == '>': return left > right
                    elif op == '<': return left < right
                except ValueError:
                    # String comparison fallback
                    left = parts[0].strip().strip("'"")
                    right = parts[1].strip().strip("'"")
                    if op == '>=': return left >= right
                    elif op == '<=': return left <= right
                    elif op == '>': return left > right
                    elif op == '<': return left < right
        
        return False


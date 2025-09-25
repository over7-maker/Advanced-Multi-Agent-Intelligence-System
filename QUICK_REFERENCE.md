# AMAS Rules Quick Reference
## Essential Guidelines for Backend & Frontend Development

### 🚀 **Quick Start Checklist**

#### **Before You Start Coding:**
- [ ] Read the relevant rule files in `/rules/`
- [ ] Set up your development environment
- [ ] Configure code quality tools (Black, ESLint, Prettier)
- [ ] Review the architecture documentation

#### **Before You Commit:**
- [ ] Run code quality checks (`black`, `isort`, `mypy`, `eslint`)
- [ ] Ensure all tests pass (`pytest`, `jest`)
- [ ] Update documentation if needed
- [ ] Review security implications

#### **Before You Deploy:**
- [ ] Complete code review process
- [ ] Run security scans
- [ ] Perform performance testing
- [ ] Update deployment documentation

---

### 🐍 **Backend (Python) Quick Rules**

#### **Code Style:**
```python
# ✅ CORRECT - Type hints, async/await, proper error handling
async def process_user_data(
    user_id: str,
    data: Dict[str, Any],
    options: Optional[Dict[str, bool]] = None
) -> Dict[str, Union[str, int, datetime]]:
    """Process user data with comprehensive error handling."""
    try:
        # Implementation
        result = await some_async_operation(data)
        logger.info("User data processed successfully", extra={"user_id": user_id})
        return result
    except ValidationError as e:
        logger.error("Validation error in user data processing", extra={"user_id": user_id, "error": str(e)})
        raise
    except Exception as e:
        logger.error("Unexpected error in user data processing", extra={"user_id": user_id, "error": str(e)}, exc_info=True)
        raise AMASException(f"Failed to process user data: {e}")
```

#### **Required Imports:**
```python
# Standard library imports
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Union, Any

# Third-party imports
import httpx
import redis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Local imports
from .core.config import settings
from .models.user import User
from .services.llm_service import LLMService
```

#### **Error Handling Pattern:**
```python
try:
    # Operation
    result = await risky_operation()
    return result
except SpecificException as e:
    logger.error(f"Specific error: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise AMASException(f"Operation failed: {e}")
```

---

### ⚛️ **Frontend (React/TypeScript) Quick Rules**

#### **Component Structure:**
```typescript
// ✅ CORRECT - TypeScript, hooks, proper error handling
import React, { useState, useCallback, memo } from 'react';
import { Card, CardContent, Typography, Button } from '@mui/material';
import { User } from '@/types/user';
import { useUserService } from '@/hooks/useUserService';
import { logger } from '@/utils/logger';

interface UserCardProps {
  user: User;
  onEdit?: (user: User) => void;
  onDelete?: (userId: string) => void;
  className?: string;
}

const UserCard: React.FC<UserCardProps> = memo(({
  user,
  onEdit,
  onDelete,
  className
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const { updateUser, deleteUser } = useUserService();

  const handleEdit = useCallback(async () => {
    try {
      setIsLoading(true);
      await onEdit?.(user);
      logger.info('User edit initiated', { userId: user.id });
    } catch (error) {
      logger.error('Failed to edit user', { userId: user.id, error });
    } finally {
      setIsLoading(false);
    }
  }, [user, onEdit]);

  return (
    <Card className={className} elevation={2}>
      <CardContent>
        <Typography variant="h6">{user.name}</Typography>
        <Typography variant="body2" color="text.secondary">
          {user.email}
        </Typography>
        {onEdit && (
          <Button
            onClick={handleEdit}
            disabled={isLoading}
            variant="outlined"
          >
            Edit
          </Button>
        )}
      </CardContent>
    </Card>
  );
});

UserCard.displayName = 'UserCard';
export default UserCard;
```

#### **Custom Hook Pattern:**
```typescript
// ✅ CORRECT - Custom hook with proper error handling
export const useUserService = () => {
  const queryClient = useQueryClient();
  const { showNotification } = useNotification();
  const [isLoading, setIsLoading] = useState(false);

  const createUser = useCallback(async (data: CreateUserData) => {
    setIsLoading(true);
    try {
      const result = await userService.createUser(data);
      queryClient.invalidateQueries({ queryKey: ['users'] });
      showNotification('User created successfully', 'success');
      return result;
    } catch (error) {
      showNotification('Failed to create user', 'error');
      logger.error('User creation failed', { error });
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [queryClient, showNotification]);

  return {
    createUser,
    isLoading,
  };
};
```

---

### 🔒 **Security Quick Rules**

#### **Authentication:**
```python
# ✅ CORRECT - JWT with proper validation
def create_access_token(user_id: str, roles: List[str]) -> str:
    """Create short-lived access token."""
    now = datetime.utcnow()
    payload = {
        'sub': user_id,
        'roles': roles,
        'iat': now,
        'exp': now + timedelta(minutes=15),  # Short-lived!
        'iss': 'amas-system',
        'aud': 'amas-clients',
        'jti': str(uuid.uuid4())
    }
    return jwt.encode(payload, settings.secret_key, algorithm='HS256')
```

#### **Password Security:**
```python
# ✅ CORRECT - Strong password validation
def validate_password(password: str) -> bool:
    """Validate password strength."""
    if len(password) < 12:
        raise ValidationError("Password must be at least 12 characters")
    if not re.search(r'[A-Z]', password):
        raise ValidationError("Password must contain uppercase letter")
    if not re.search(r'[a-z]', password):
        raise ValidationError("Password must contain lowercase letter")
    if not re.search(r'\d', password):
        raise ValidationError("Password must contain number")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError("Password must contain special character")
    return True
```

---

### 🧪 **Testing Quick Rules**

#### **Unit Test Structure:**
```python
# ✅ CORRECT - Comprehensive test with proper setup
@pytest.mark.asyncio
async def test_create_user_success(
    user_service: UserService,
    sample_user_data: dict
):
    """Test successful user creation with valid data."""
    # Arrange
    user_create = UserCreate(**sample_user_data)
    expected_email = sample_user_data["email"]
    
    # Act
    result = await user_service.create_user(user_create)
    
    # Assert
    assert result is not None
    assert isinstance(result, User)
    assert result.email == expected_email
    assert result.id is not None
    assert result.created_at is not None
```

#### **Test Naming Convention:**
```python
# Pattern: test_[method_name]_[scenario]_[expected_result]
test_create_user_success                    # Happy path
test_create_user_validation_error          # Validation failure
test_create_user_duplicate_email           # Business logic error
test_get_user_by_id_not_found              # Not found scenario
```

---

### 🚫 **FORBIDDEN PATTERNS**

#### **❌ NEVER DO THESE:**

**Backend:**
```python
# ❌ WRONG - No type hints, sync I/O, bare except
def process_data(data, options=None):
    try:
        response = requests.get("http://api.example.com")  # Blocking!
        return response.json()
    except:
        pass  # Silent failure!

# ✅ CORRECT - Type hints, async I/O, proper error handling
async def process_data(
    data: Dict[str, Any], 
    options: Optional[Dict[str, bool]] = None
) -> Dict[str, Any]:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://api.example.com")
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Request failed: {e}")
        raise AMASException(f"Data processing failed: {e}")
```

**Frontend:**
```typescript
// ❌ WRONG - No TypeScript, direct DOM manipulation, no error handling
const MyComponent = () => {
  useEffect(() => {
    document.getElementById('myElement')?.classList.add('active');
  }, []);
  
  return <div>Content</div>;
};

// ✅ CORRECT - TypeScript, React patterns, error handling
const MyComponent: React.FC = () => {
  const [isActive, setIsActive] = useState(false);
  
  const handleClick = useCallback(() => {
    try {
      setIsActive(true);
    } catch (error) {
      logger.error('Failed to activate component', { error });
    }
  }, []);
  
  return (
    <div className={isActive ? 'active' : ''} onClick={handleClick}>
      Content
    </div>
  );
};
```

---

### 📋 **Essential Commands**

#### **Code Quality:**
```bash
# Backend
black .                    # Format Python code
isort .                    # Sort imports
mypy .                     # Type checking
pytest                     # Run tests
pytest --cov=src          # Run tests with coverage

# Frontend
npm run lint              # ESLint
npm run format            # Prettier
npm run type-check        # TypeScript check
npm test                  # Run tests
npm run test:coverage     # Run tests with coverage
```

#### **Security:**
```bash
# Security scanning
bandit -r src/            # Python security scan
npm audit                 # Node.js security audit
docker scan image:tag     # Docker security scan
```

---

### 🎯 **Performance Targets**

#### **Response Times:**
- **API endpoints**: < 200ms for simple operations
- **Database queries**: < 100ms for standard operations
- **Page loads**: < 2s for initial load
- **File uploads**: < 5s for files up to 100MB

#### **Resource Usage:**
- **Memory usage**: < 80% of available RAM
- **CPU usage**: < 70% under normal load
- **Test coverage**: Minimum 80%

---

### 📞 **Getting Help**

#### **Rule Violations:**
- **Minor violations**: Automated warnings in CI/CD
- **Major violations**: Blocked deployment
- **Security violations**: Immediate escalation required

#### **Rule Updates:**
- Rules are reviewed monthly
- Team feedback is incorporated
- Industry best practices are updated
- All changes are version controlled

---

## 🚀 **Remember: These rules ensure AMAS remains the most advanced, secure, and maintainable AI system ever built!**

**Follow them religiously, and you'll contribute to something truly extraordinary!** ✨

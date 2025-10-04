# Issue #4: Refactor Provider Initialization

## Priority: Medium (Code Refactoring - Week 2-3)
## Labels: `refactoring`, `provider-initialization`, `architecture`, `maintainability`

## Description

Refactor the provider initialization system to improve security, maintainability, and code organization. The current implementation has scattered provider logic across multiple files with inconsistent patterns.

## Current Architecture Issues

### 1. Scattered Provider Logic
- **Location**: Multiple files with provider initialization
- **Issue**: Provider logic spread across `universal_ai_manager.py`, `ultimate_fallback_system.py`, `llm_service.py`
- **Risk**: Code duplication, inconsistent patterns, maintenance difficulties

### 2. Inconsistent Provider Management
- **Location**: Various service files
- **Issue**: Different initialization patterns for different providers
- **Risk**: Security vulnerabilities, configuration inconsistencies

### 3. Hard-coded Provider Configuration
- **Location**: Multiple service files
- **Issue**: Provider configurations hard-coded in service files
- **Risk**: Difficult to maintain, security issues, configuration drift

### 4. Lack of Provider Abstraction
- **Location**: All provider-related files
- **Issue**: No common interface for providers
- **Risk**: Code duplication, inconsistent error handling

## Implementation Plan

### Phase 1: Provider Architecture Design (Days 1-2)
1. **Create Provider Abstraction Layer**
   ```python
   # src/amas/providers/
   ├── __init__.py
   ├── base/
   │   ├── __init__.py
   │   ├── provider_base.py
   │   └── provider_interface.py
   ├── llm/
   │   ├── __init__.py
   │   ├── openai_provider.py
   │   ├── anthropic_provider.py
   │   └── local_provider.py
   └── manager/
       ├── __init__.py
       └── provider_manager.py
   ```

2. **Define Provider Interface**
   - Create abstract base class for all providers
   - Define common methods and properties
   - Implement provider lifecycle management

### Phase 2: Provider Implementation (Days 3-5)
1. **Implement Core Providers**
   - Refactor existing providers to use new architecture
   - Implement secure provider initialization
   - Add provider health checking and monitoring

2. **Provider Manager Implementation**
   - Create centralized provider management
   - Implement provider discovery and registration
   - Add provider failover and load balancing

### Phase 3: Integration and Testing (Days 6-7)
1. **Service Integration**
   - Update all services to use new provider architecture
   - Implement backward compatibility
   - Add comprehensive testing

2. **Documentation and Migration**
   - Create migration guide
   - Update documentation
   - Add configuration examples

## Technical Requirements

### Provider Interface
```python
# src/amas/providers/base/provider_interface.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

@dataclass
class ProviderConfig:
    name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    enabled: bool = True

class ProviderBase(ABC):
    """Base class for all AI providers"""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.initialized = False
        self.healthy = False
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the provider"""
        pass
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate response from the provider"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check provider health"""
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the provider"""
        pass
```

### Provider Manager
```python
# src/amas/providers/manager/provider_manager.py
from typing import Dict, List, Optional
from .base.provider_interface import ProviderBase, ProviderConfig

class ProviderManager:
    """Centralized provider management"""
    
    def __init__(self):
        self.providers: Dict[str, ProviderBase] = {}
        self.active_providers: List[str] = []
        self.fallback_chain: List[str] = []
    
    async def register_provider(self, provider: ProviderBase) -> bool:
        """Register a new provider"""
        # Implementation details...
    
    async def initialize_all_providers(self) -> Dict[str, bool]:
        """Initialize all registered providers"""
        # Implementation details...
    
    async def get_available_provider(self) -> Optional[ProviderBase]:
        """Get the next available provider in the chain"""
        # Implementation details...
```

## Security Improvements

### 1. Secure Configuration Management
- Encrypt API keys in configuration
- Implement secure key rotation
- Add configuration validation

### 2. Provider Isolation
- Isolate provider instances
- Implement provider sandboxing
- Add provider access controls

### 3. Audit and Monitoring
- Log all provider interactions
- Monitor provider performance
- Alert on provider failures

## Implementation Details

### 1. Provider Base Implementation
```python
# src/amas/providers/base/provider_base.py
import asyncio
import logging
from typing import Dict, Any, Optional
from .provider_interface import ProviderBase, ProviderConfig

class BaseProvider(ProviderBase):
    """Base implementation for all providers"""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.logger = logging.getLogger(f"provider.{config.name}")
        self.retry_count = 0
    
    async def initialize(self) -> bool:
        """Initialize the provider with security checks"""
        try:
            # Validate configuration
            if not self._validate_config():
                return False
            
            # Initialize provider-specific logic
            await self._initialize_provider()
            
            # Perform health check
            self.healthy = await self.health_check()
            self.initialized = True
            
            self.logger.info(f"Provider {self.config.name} initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize provider {self.config.name}: {e}")
            return False
    
    def _validate_config(self) -> bool:
        """Validate provider configuration"""
        # Implementation details...
    
    async def _initialize_provider(self) -> None:
        """Provider-specific initialization"""
        # Override in subclasses
        pass
```

### 2. Specific Provider Implementation
```python
# src/amas/providers/llm/openai_provider.py
from ..base.provider_base import BaseProvider
from ..base.provider_interface import ProviderConfig

class OpenAIProvider(BaseProvider):
    """OpenAI provider implementation"""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.client = None
    
    async def _initialize_provider(self) -> None:
        """Initialize OpenAI client"""
        import openai
        self.client = openai.AsyncOpenAI(api_key=self.config.api_key)
    
    async def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate response using OpenAI"""
        try:
            response = await self.client.chat.completions.create(
                model=kwargs.get('model', 'gpt-3.5-turbo'),
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get('max_tokens', 1000),
                temperature=kwargs.get('temperature', 0.7)
            )
            
            return {
                'content': response.choices[0].message.content,
                'tokens_used': response.usage.total_tokens,
                'provider': self.config.name
            }
            
        except Exception as e:
            self.logger.error(f"OpenAI generation failed: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check OpenAI service health"""
        try:
            # Simple health check
            await self.client.models.list()
            return True
        except Exception:
            return False
```

## Testing Requirements

### Unit Tests
- Test provider initialization
- Test provider health checking
- Test provider failover
- Test configuration validation

### Integration Tests
- Test provider manager functionality
- Test provider chain execution
- Test error handling and recovery
- Test performance under load

### Security Tests
- Test API key handling
- Test provider isolation
- Test configuration security
- Test audit logging

## Acceptance Criteria

- [ ] All providers use unified interface
- [ ] Provider initialization is secure
- [ ] Provider failover works correctly
- [ ] Configuration is centralized
- [ ] Code duplication is eliminated
- [ ] Performance is maintained or improved
- [ ] All tests pass

## Files to Modify

### New Files
- `src/amas/providers/` (new directory)
- `src/amas/providers/base/provider_interface.py`
- `src/amas/providers/base/provider_base.py`
- `src/amas/providers/llm/openai_provider.py`
- `src/amas/providers/llm/anthropic_provider.py`
- `src/amas/providers/llm/local_provider.py`
- `src/amas/providers/manager/provider_manager.py`

### Modified Files
- `src/amas/services/universal_ai_manager.py`
- `src/amas/services/ultimate_fallback_system.py`
- `src/amas/services/llm_service.py`
- `src/amas/config/settings.py`

### Test Files
- `tests/unit/test_providers/` (new directory)
- `tests/integration/test_provider_manager.py` (new)
- `tests/security/test_provider_security.py` (new)

## Configuration Updates

### Provider Configuration
```yaml
# Add to amas_config.yaml
providers:
  manager:
    enabled: true
    failover_enabled: true
    health_check_interval: 30
    max_retries: 3
  
  llm:
    openai:
      enabled: true
      api_key: "${OPENAI_API_KEY}"
      base_url: "https://api.openai.com/v1"
      timeout: 30
      max_retries: 3
    
    anthropic:
      enabled: true
      api_key: "${ANTHROPIC_API_KEY}"
      base_url: "https://api.anthropic.com"
      timeout: 30
      max_retries: 3
    
    local:
      enabled: true
      base_url: "http://localhost:11434"
      timeout: 60
      max_retries: 1
```

## Dependencies

### New Dependencies
```python
# Add to requirements.txt
# No new dependencies required - using existing libraries
```

## Related Issues

- Issue #1: Add input validation
- Issue #2: Implement path sanitization
- Issue #3: Mask API keys in logs

## Estimated Effort

- **Development**: 7-10 days
- **Testing**: 3-4 days
- **Documentation**: 2-3 days
- **Total**: 12-17 days

## Risk Assessment

- **Security Risk**: Medium (improved security)
- **Implementation Risk**: Medium
- **Performance Impact**: Minimal
- **Breaking Changes**: Low (backward compatible)

## Migration Strategy

### Phase 1: Parallel Implementation
- Implement new provider architecture alongside existing code
- Add feature flags for gradual migration
- Maintain backward compatibility

### Phase 2: Gradual Migration
- Migrate services one by one
- Update configuration gradually
- Monitor for issues

### Phase 3: Cleanup
- Remove old provider code
- Update documentation
- Final testing and validation

---

**Assignee**: TBD
**Milestone**: Code Refactoring (Week 2-3)
**Created**: [Current Date]
**Last Updated**: [Current Date]
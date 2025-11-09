# Agent Capabilities Configuration Guide

**File:** `config/agent_capabilities.yaml`  
**Version:** 1.0  
**Last Updated:** 2025-11-04

---

## Overview

The `agent_capabilities.yaml` file defines per-agent policies, tool configurations, security policies, and environment-specific overrides for the AMAS system.

---

## File Structure

```yaml
schema_version: "1.0"

_defaults:
  # Default policies applied to all agents

agents:
  # Agent-specific configurations
  
tool_configurations:
  # Tool-specific security and operational settings
  
security_policies:
  # Global security policies
  
environments:
  # Environment-specific overrides
```

---

## Schema Version

```yaml
schema_version: "1.0"
```

The schema version ensures backward compatibility. When making breaking changes, increment the version.

---

## Default Policies

Default policies are applied to all agents unless overridden:

```yaml
_defaults:
  constraints:
    max_iterations: 5
    timeout_seconds: 300
    cost_budget_tokens: 10000  # ~$0.02 per execution at GPT-3.5-turbo rates
  rate_limits:
    requests_per_minute: 15
    tokens_per_hour: 8000
  quality_gates:
    require_human_approval: true
    output_validation_required: true
```

---

## Agent Configuration

### Required Fields

Each agent must have:

- `role` - Agent's functional role (research, analysis, synthesis, etc.)
- `description` - Human-readable description
- `allowed_tools` - List of permitted tool capabilities
- `constraints` - Execution constraints
- `rate_limits` - Rate limiting configuration
- `quality_gates` - Quality control settings

### Example: Research Agent

```yaml
research_agent_v1:
  role: "research"
  description: "Web research and information gathering specialist"
  allowed_tools:
    - "web_search"
    - "api_call"
    - "file_read"
    - "vector_search"
    - "document_generation"
  constraints:
    max_iterations: 8
    timeout_seconds: 600
    cost_budget_tokens: 20000
  rate_limits:
    requests_per_minute: 30
    tokens_per_hour: 15000
  quality_gates:
    require_human_approval: false
    output_validation_required: true
    fact_checking_enabled: true  # Requires cross-referencing facts with trusted sources
```

### Example: Synthesis Agent

```yaml
synthesis_agent_v1:
  role: "synthesis"
  description: "Content synthesis and document generation specialist"
  allowed_tools:
    - "file_read"  # Restricted to allowed_paths in tool_configurations
    - "file_write"  # Restricted to allowed_directories in tool_configurations
    - "document_generation"  # Generates structured documents with validation
    - "template_rendering"  # Renders templates with sandboxing enabled
    - "vector_search"  # Searches vector database for content references
  constraints:
    max_iterations: 3  # Limited iterations to prevent runaway synthesis
    timeout_seconds: 300  # 5 minute timeout for document generation
    cost_budget_tokens: 10000  # Token budget for synthesis operations
  rate_limits:
    requests_per_minute: 15  # Prevents overwhelming document generation service
    tokens_per_hour: 8000  # Prevents excessive token consumption
  quality_gates:
    require_human_approval: false  # Auto-approved for non-critical content synthesis
    output_validation_required: true  # Validates output against schema
    plagiarism_check_enabled: true  # Checks for plagiarism before output
    pii_detection_enabled: true  # Detects and redacts PII in outputs
    output_sanitization_required: true  # Sanitizes output to prevent injection
    content_moderation_required: true  # Moderates content for safety
```

---

## Tool Configurations

### File Read Configuration

```yaml
file_read:
  # Restricted to sandboxed directories only for security
  allowed_paths:
    - "data/input/"
    - "data/shared/"
    - "reports/"
    - "documents/"
  allowed_extensions:
    - ".txt"
    - ".json"
    - ".csv"
    - ".md"
    - ".yaml"
    - ".yml"
  max_file_size_mb: 100
  blocked_paths:
    - "/etc/*"
    - "/usr/*"
    - "*.env"
    - "*secret*"
    - "*password*"
    - "/root/*"
    - "/home/*/.ssh/*"
```

### File Write Configuration

```yaml
file_write:
  allowed_extensions:
    - ".txt"
    - ".json"
    - ".csv"
    - ".md"
    - ".yaml"
  max_file_size_mb: 50
  allowed_directories:
    - "outputs/"
    - "reports/"
    - "documents/"
  blocked_directories:
    - "/"
    - "/etc/"
    - "/usr/"
    - "/var/"
```

### API Call Configuration

```yaml
api_call:
  # API call whitelisting for security - restrict to allowed domains
  allowed_domains: []  # Empty means all domains allowed (configure per environment)
  allowed_endpoints: []  # Whitelist specific endpoints if needed
  allowed_methods: ["GET", "POST"]
  blocked_methods: ["DELETE", "PUT", "PATCH"]
  max_response_size_mb: 10
  timeout_seconds: 60
  rate_limit_per_endpoint: 100
  # Audit logging required for all API calls
  audit_logging_required: true
  allowed_headers:
    - "Content-Type"
    - "Authorization"
    - "User-Agent"
    - "Accept"
  blocked_headers:
    - "X-Forwarded-For"
    - "X-Real-IP"
```

### Database Query Configuration

```yaml
database_query:
  allowed_operations: ["SELECT"]
  blocked_operations: ["DELETE", "DROP", "ALTER", "CREATE", "INSERT", "UPDATE"]
  max_rows_returned: 10000
  timeout_seconds: 60
  allowed_tables:
    - "public.research_data"
    - "public.analysis_results"
    - "public.document_metadata"
  blocked_tables:
    - "users"
    - "auth_tokens"
    - "system_config"
  # Mask sensitive data in outputs
  mask_sensitive_data: true
```

---

## Security Policies

### PII Detection

```yaml
security_policies:
  pii_detection:
    enabled: true
    redact_in_logs: true
    block_pii_in_outputs: true
```

### Content Safety

```yaml
  content_safety:
    enabled: true
    scan_inputs: true
    scan_outputs: true
    block_unsafe_content: true
```

### Audit Logging

```yaml
  audit_logging:
    enabled: true
    log_all_tool_calls: true
    log_parameters: true
    log_outputs: false  # Outputs may contain sensitive data
    retention_days: 90
```

### Approval Workflows

```yaml
  approval_workflows:
    default_approvers:
      - "admin@amas.com"
      - "security@amas.com"
    approval_timeout_minutes: 30
    auto_deny_on_timeout: true
    escalation_enabled: true
```

---

## Environment-Specific Overrides

### Development

```yaml
environments:
  development:
    security_policies:
      approval_workflows:
        auto_approve_low_risk: true
      audit_logging:
        retention_days: 30
```

### Staging

```yaml
  staging:
    security_policies:
      approval_workflows:
        auto_approve_low_risk: false
      audit_logging:
        retention_days: 60
```

### Production

```yaml
  production:
    security_policies:
      pii_detection:
        block_pii_in_outputs: true
      approval_workflows:
        auto_approve_low_risk: false
        require_dual_approval_high_risk: true
      audit_logging:
        retention_days: 365
        backup_enabled: true
```

---

## Validation

### YAML Syntax Validation

```bash
# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('config/agent_capabilities.yaml'))"
```

### Schema Validation

The system validates the configuration structure at runtime:

- All required agent fields present
- Tool names match registered tools
- Rate limits are positive integers
- Timeouts are within acceptable ranges
- Quality gates are boolean values

---

## Best Practices

### 1. Principle of Least Privilege

✅ **Do:**
- Grant agents only the tools they need
- Use specific tool capabilities
- Restrict file paths and directories

❌ **Don't:**
- Grant all tools to all agents
- Use wildcard paths
- Disable security features

### 2. Rate Limiting

✅ **Do:**
- Set appropriate rate limits based on tool capacity
- Consider downstream service limits
- Monitor and adjust based on usage

❌ **Don't:**
- Set unlimited rate limits
- Ignore service capacity
- Set limits too low (causing legitimate failures)

### 3. Quality Gates

✅ **Do:**
- Enable validation for production agents
- Require approval for high-risk operations
- Enable PII detection for agents handling user data

❌ **Don't:**
- Disable validation in production
- Auto-approve high-risk tools
- Skip content moderation

### 4. Security Configuration

✅ **Do:**
- Configure path restrictions for file operations
- Whitelist API domains in production
- Enable audit logging
- Mask sensitive data

❌ **Don't:**
- Allow unrestricted file access
- Allow all API domains in production
- Disable audit logging
- Log sensitive data

---

## Troubleshooting

### Issue: Agent Cannot Use Tool

**Check:**
1. Tool is in agent's `allowed_tools` list
2. Tool exists in `tool_configurations`
3. YAML file is valid and loaded correctly

### Issue: Rate Limit Too Restrictive

**Solution:**
1. Check current usage with `get_usage_stats()`
2. Adjust `requests_per_minute` or `tokens_per_hour`
3. Consider tool-specific limits

### Issue: Approval Always Required

**Check:**
1. Tool's `requires_approval` setting in tool configuration
2. Agent's `require_human_approval` in quality_gates
3. Environment-specific overrides

---

## Migration Guide

### Updating Agent Configuration

When updating an agent configuration:

1. **Backup current configuration**
2. **Update YAML file**
3. **Validate syntax**: `python3 -c "import yaml; yaml.safe_load(open('config/agent_capabilities.yaml'))"`
4. **Test with agent**: Verify agent can still function
5. **Deploy to staging first**
6. **Monitor usage and errors**
7. **Deploy to production**

### Adding New Agent

1. Add agent definition to `agents:` section
2. Configure all required fields
3. Set appropriate constraints and limits
4. Test in development
5. Update documentation

### Adding New Tool

1. Add tool definition to `tool_configurations:`
2. Set risk level and approval requirements
3. Configure security restrictions
4. Update agent `allowed_tools` lists as needed
5. Test tool access and execution

---

*Last Updated: 2025-11-04*

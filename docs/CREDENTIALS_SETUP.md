# AMAS Credentials Setup Guide

This guide explains how to configure real credentials for all AMAS components.

## Quick Start

1. Copy the environment variables template below to a `.env` file in the project root
2. Fill in your actual API keys and credentials
3. Restart the application

## Environment Variables Template

Create a `.env` file in the project root with the following variables:

```bash
# ============================================================================
# APPLICATION SETTINGS
# ============================================================================
ENVIRONMENT=development
DEBUG=false
APP_NAME=AMAS
HOST=0.0.0.0
PORT=8000

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================
DB_URL=postgresql://postgres:amas_password@localhost:5432/amas
DB_HOST=localhost
DB_PORT=5432
DB_NAME=amas
DB_USER=postgres
DB_PASSWORD=amas_password

# ============================================================================
# REDIS CONFIGURATION
# ============================================================================
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# ============================================================================
# NEO4J CONFIGURATION
# ============================================================================
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=amas_password

# ============================================================================
# SECURITY SETTINGS
# ============================================================================
SECURITY_SECRET_KEY=change_this_to_a_secure_random_string_in_production
SECURITY_JWT_SECRET_KEY=change_this_to_a_secure_random_string_in_production
SECURITY_JWT_ALGORITHM=HS256
SECURITY_JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# ============================================================================
# AI PROVIDER API KEYS (26+ Providers)
# ============================================================================

# Tier 0 - Standard Premium Providers (Highest Priority)
AI_OPENAI_API_KEY=your_openai_api_key_here
AI_ANTHROPIC_API_KEY=your_anthropic_api_key_here
AI_GOOGLE_AI_API_KEY=your_google_ai_api_key_here
AI_GROQ_API_KEY=your_groq_api_key_here
AI_COHERE_API_KEY=your_cohere_api_key_here

# Tier 1 - Premium Speed & Quality
AI_CEREBRAS_API_KEY=your_cerebras_api_key_here
AI_NVIDIA_API_KEY=your_nvidia_api_key_here
AI_GROQ2_API_KEY=your_groq2_api_key_here
AI_GROQAI_API_KEY=your_groqai_api_key_here

# Tier 2 - High Quality
AI_DEEPSEEK_API_KEY=your_deepseek_api_key_here
AI_CODESTRAL_API_KEY=your_codestral_api_key_here
AI_GLM_API_KEY=your_glm_api_key_here
AI_GEMINI2_API_KEY=your_gemini2_api_key_here
AI_GROK_API_KEY=your_grok_api_key_here

# Tier 4 - OpenRouter Free Tier
AI_KIMI_API_KEY=your_kimi_api_key_here
AI_QWEN_API_KEY=your_qwen_api_key_here
AI_GPTOSS_API_KEY=your_gptoss_api_key_here
AI_CHUTES_API_KEY=your_chutes_api_key_here

# Additional Providers
AI_TOGETHER_API_KEY=your_together_api_key_here
AI_PERPLEXITY_API_KEY=your_perplexity_api_key_here
AI_FIREWORKS_API_KEY=your_fireworks_api_key_here
AI_REPLICATE_API_KEY=your_replicate_api_key_here
AI_AI21_API_KEY=your_ai21_api_key_here
AI_ALEPH_ALPHA_API_KEY=your_aleph_alpha_api_key_here
AI_WRITER_API_KEY=your_writer_api_key_here
AI_MOONSHOT_API_KEY=your_moonshot_api_key_here
AI_MISTRAL_API_KEY=your_mistral_api_key_here

# ============================================================================
# INTEGRATION PLATFORM CREDENTIALS
# ============================================================================

# N8N Workflow Automation
INTEGRATION_N8N_BASE_URL=http://localhost:5678
INTEGRATION_N8N_API_KEY=your_n8n_api_key_here
INTEGRATION_N8N_USERNAME=your_n8n_username_here
INTEGRATION_N8N_PASSWORD=your_n8n_password_here

# Slack Communication
INTEGRATION_SLACK_BOT_TOKEN=xoxb-your-slack-bot-token-here
INTEGRATION_SLACK_SIGNING_SECRET=your_slack_signing_secret_here

# GitHub DevOps
INTEGRATION_GITHUB_ACCESS_TOKEN=ghp_your_github_personal_access_token_here
INTEGRATION_GITHUB_WEBHOOK_SECRET=your_github_webhook_secret_here

# Notion Project Management
INTEGRATION_NOTION_API_KEY=secret_your_notion_integration_token_here

# Jira Project Management
INTEGRATION_JIRA_SERVER=https://your-domain.atlassian.net
INTEGRATION_JIRA_EMAIL=your_email@example.com
INTEGRATION_JIRA_API_TOKEN=your_jira_api_token_here

# Salesforce CRM
INTEGRATION_SALESFORCE_USERNAME=your_salesforce_username_here
INTEGRATION_SALESFORCE_PASSWORD=your_salesforce_password_here
INTEGRATION_SALESFORCE_SECURITY_TOKEN=your_salesforce_security_token_here
# OR use OAuth tokens:
INTEGRATION_SALESFORCE_ACCESS_TOKEN=your_salesforce_oauth_access_token_here
INTEGRATION_SALESFORCE_INSTANCE_URL=https://your-instance.salesforce.com
```

## Credential Priority

The system uses the following priority order for loading credentials:

1. **Environment Variables** (Highest Priority)
   - Direct environment variables (e.g., `OPENAI_API_KEY`)
   - System environment variables
   - Shell environment variables

2. **Settings Configuration** (From `.env` file)
   - Loaded via `pydantic-settings`
   - Automatically parsed from `.env` file
   - Supports nested settings (e.g., `AI_OPENAI_API_KEY` → `settings.ai.openai_api_key`)

3. **Default Values** (Lowest Priority)
   - Fallback values defined in code
   - Only used if no credentials are found

## How It Works

### AI Provider Credentials

The `EnhancedAIRouter` automatically loads API keys using the `get_api_key()` function:

```python
# Priority 1: Environment variable
OPENAI_API_KEY=sk-...

# Priority 2: Settings (from .env)
AI_OPENAI_API_KEY=sk-...

# Both work! Environment variable takes precedence.
```

### Integration Platform Credentials

Integration connectors use the `CredentialManager` service:

```python
from src.amas.services.credential_manager import get_credential_manager

cred_manager = get_credential_manager()

# Get N8N credentials
n8n_creds = cred_manager.get_integration_credentials("n8n")
# Returns: {"base_url": "...", "api_key": "...", ...}

# Get AI provider key
openai_key = cred_manager.get_ai_api_key("openai")
```

### Credential Validation

All connectors validate credentials before use:

```python
# In test mode, accepts test credentials
credentials = {"api_key": "test_key", "test_mode": True}
is_valid = await connector.validate_credentials(credentials)  # Returns True

# In production, validates against real API
credentials = {"api_key": "real_api_key_here"}
is_valid = await connector.validate_credentials(credentials)  # Validates with API
```

## Security Best Practices

1. **Never commit `.env` file to Git**
   - Already in `.gitignore`
   - Use `.env.example` as template

2. **Use Environment Variables in Production**
   - Set via deployment platform (Docker, Kubernetes, etc.)
   - Use secrets management (AWS Secrets Manager, HashiCorp Vault, etc.)

3. **Encrypt Sensitive Credentials** (Optional)
   - Set `CREDENTIAL_ENCRYPTION_KEY` environment variable
   - CredentialManager will automatically encrypt/decrypt

4. **Rotate Credentials Regularly**
   - Update API keys periodically
   - Revoke old keys after rotation

## Testing with Real Credentials

To test with real credentials:

1. Add your API keys to `.env` file
2. Set `ENVIRONMENT=testing` (still validates but allows test mode)
3. Run tests - they will use real credentials if available

## Troubleshooting

### Credentials Not Loading

1. Check `.env` file exists in project root
2. Verify variable names match exactly (case-sensitive)
3. Restart application after changing `.env`
4. Check logs for credential loading errors

### Validation Failing

1. Verify API key format is correct
2. Check API key has required permissions
3. Ensure network connectivity to provider
4. Review connector logs for specific error messages

### Multiple Credential Sources

If you have credentials in both environment variables and `.env`:
- Environment variables take precedence
- This allows overriding `.env` values per deployment

## Support

For issues with credential setup:
1. Check application logs for credential loading messages
2. Verify `.env` file syntax (no spaces around `=`)
3. Ensure all required credentials are provided
4. Review connector-specific documentation


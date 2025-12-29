"""
Integration Agent - Specialized agent for platform integrations and connectors
Implements PART_3 requirements
"""

import json
import logging
import time
from typing import Any, Dict, List, Optional

from src.amas.agents.base_agent import BaseAgent
from src.amas.agents.tools import get_tool_registry
from src.amas.agents.utils.json_parser import JSONParser

logger = logging.getLogger(__name__)


class IntegrationAgent(BaseAgent):
    """
    Integration Agent
    
    Specializes in:
    - Platform integrations
    - API connectors
    - Webhook handling
    - Data synchronization
    - Integration patterns
    """
    
    def __init__(self):
        super().__init__(
            agent_id="integration_agent",
            name="Integration Agent",
            agent_type="integration",
            system_prompt="""You are an expert integration engineer with 15+ years of experience 
            in platform integrations, API connectors, and system integration patterns.
            
            Your expertise includes:
            • REST API integrations
            • Webhook implementations
            • OAuth2 authentication flows
            • Data synchronization patterns
            • ETL (Extract, Transform, Load) processes
            • Message queue integrations
            • Third-party service connectors
            • Integration testing
            • Error handling and retry logic
            • Rate limiting and throttling
            
            When designing integrations, you:
            1. Follow integration best practices
            2. Implement proper error handling
            3. Include retry logic with exponential backoff
            4. Handle rate limiting gracefully
            5. Ensure data consistency
            
            Always produce production-ready integration code.""",
            model_preference=None,  # Use local models first
            strategy="quality_first"
        )
        
        # Get tool registry
        tool_registry = get_tool_registry()
        self.integration_tools = []
    
    async def _prepare_prompt(
        self,
        target: str,
        parameters: Dict[str, Any]
    ) -> str:
        """Prepare integration design prompt"""
        
        platform = parameters.get("platform", target)
        integration_type = parameters.get("integration_type", "api")
        requirements = parameters.get("requirements", {})
        existing_code = parameters.get("existing_code", "")
        
        prompt = f"""Design integration for: {platform}

Integration Type: {integration_type}

Requirements:
{json.dumps(requirements, indent=2) if requirements else "No specific requirements"}

Existing Code (if reviewing):
{existing_code[:3000] if existing_code else "New integration"}

Please provide comprehensive integration design including:
1. Authentication/Authorization setup
2. API client implementation
3. Webhook handling (if applicable)
4. Error handling and retry logic
5. Rate limiting implementation
6. Data transformation logic
7. Testing strategy

Format your response as JSON with the following structure:
{{
    "authentication": {{
        "type": "oauth2|api_key|basic",
        "implementation": "..."
    }},
    "api_client": "...",
    "webhook_handler": "...",
    "error_handling": {{
        "retry_strategy": "...",
        "error_codes": {{...}}
    }},
    "rate_limiting": "...",
    "data_transformation": "...",
    "test_code": "..."
}}"""
        
        return prompt
    
    async def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response into structured format"""
        
        try:
            # Try to extract JSON from response
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                response = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                response = response[json_start:json_end].strip()
            
            result = json.loads(response)
            
            return {
                "success": True,
                "integration_design": result,
                "has_authentication": bool(result.get("authentication")),
                "has_api_client": bool(result.get("api_client")),
                "has_webhook_handler": bool(result.get("webhook_handler")),
                "has_error_handling": bool(result.get("error_handling"))
            }
        except json.JSONDecodeError:
            # Fallback: return raw response
            logger.warning("Failed to parse JSON response, returning raw text")
            return {
                "success": True,
                "integration_design": {
                    "raw_response": response,
                    "api_client": response
                },
                "has_authentication": False,
                "has_api_client": True,
                "has_webhook_handler": False,
                "has_error_handling": False
            }
    
    async def _generate_integration_patterns(self, platform: str, integration_type: str) -> List[Dict[str, Any]]:
        """
        Generate integration patterns for the platform
        """
        patterns = []
        
        try:
            logger.info(f"IntegrationAgent: Generating integration patterns for {platform}")
            
            # Common integration patterns
            base_patterns = [
                {
                    "name": "API Client Pattern",
                    "description": "RESTful API client with retry logic and error handling",
                    "components": [
                        "Base API client class",
                        "Request/Response models",
                        "Error handling",
                        "Retry mechanism",
                        "Rate limiting"
                    ],
                    "code_template": """
class {Platform}APIClient:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({{"Authorization": f"Bearer {{api_key}}"}})
    
    def _request(self, method: str, endpoint: str, **kwargs):
        url = f"{{self.base_url}}{{endpoint}}"
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.session.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
"""
                },
                {
                    "name": "Webhook Handler Pattern",
                    "description": "Webhook endpoint with signature verification",
                    "components": [
                        "Webhook endpoint",
                        "Signature verification",
                        "Event processing",
                        "Idempotency handling"
                    ],
                    "code_template": """
@app.post("/webhooks/{platform}")
async def handle_webhook(request: Request):
    signature = request.headers.get("X-{Platform}-Signature")
    payload = await request.body()
    
    # Verify signature
    if not verify_signature(payload, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    event = json.loads(payload)
    event_id = event.get("id")
    
    # Check idempotency
    if await is_event_processed(event_id):
        return {{"status": "already_processed"}}
    
    # Process event
    await process_webhook_event(event)
    await mark_event_processed(event_id)
    
    return {{"status": "success"}}
"""
                },
                {
                    "name": "OAuth2 Flow Pattern",
                    "description": "OAuth2 authorization code flow implementation",
                    "components": [
                        "Authorization URL generation",
                        "Token exchange",
                        "Token refresh",
                        "Token storage"
                    ],
                    "code_template": """
class {Platform}OAuth2Client:
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.auth_url = "https://{platform}.com/oauth/authorize"
        self.token_url = "https://{platform}.com/oauth/token"
    
    def get_authorization_url(self, state: str) -> str:
        params = {{
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "read write",
            "state": state
        }}
        return f"{{self.auth_url}}?{{urlencode(params)}}"
    
    async def exchange_code_for_token(self, code: str) -> dict:
        data = {{
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri
        }}
        response = requests.post(self.token_url, data=data)
        return response.json()
    
    async def refresh_token(self, refresh_token: str) -> dict:
        data = {{
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }}
        response = requests.post(self.token_url, data=data)
        return response.json()
"""
                },
                {
                    "name": "Data Synchronization Pattern",
                    "description": "Bidirectional data sync with conflict resolution",
                    "components": [
                        "Sync scheduler",
                        "Change detection",
                        "Conflict resolution",
                        "Sync status tracking"
                    ],
                    "code_template": """
class {Platform}SyncManager:
    def __init__(self, local_db, remote_api):
        self.local_db = local_db
        self.remote_api = remote_api
    
    async def sync_to_remote(self, local_id: str):
        local_record = await self.local_db.get(local_id)
        remote_record = await self.remote_api.get(local_id)
        
        if remote_record and remote_record["updated_at"] > local_record["updated_at"]:
            # Conflict: remote is newer
            return await self.resolve_conflict(local_record, remote_record)
        
        await self.remote_api.update(local_id, local_record)
    
    async def sync_from_remote(self, remote_id: str):
        remote_record = await self.remote_api.get(remote_id)
        local_record = await self.local_db.get(remote_id)
        
        if not local_record or remote_record["updated_at"] > local_record["updated_at"]:
            await self.local_db.upsert(remote_record)
"""
                }
            ]
            
            # Platform-specific patterns
            platform_patterns = {
                "github": [
                    {
                        "name": "GitHub Webhook Handler",
                        "description": "Handle GitHub push, pull request, and issue events",
                        "events": ["push", "pull_request", "issues", "release"]
                    }
                ],
                "slack": [
                    {
                        "name": "Slack Bot Integration",
                        "description": "Slack bot with slash commands and interactive components",
                        "features": ["slash_commands", "interactive_components", "events_api"]
                    }
                ],
                "salesforce": [
                    {
                        "name": "Salesforce API Integration",
                        "description": "SOQL queries and REST API operations",
                        "features": ["soql_queries", "bulk_api", "streaming_api"]
                    }
                ]
            }
            
            patterns.extend(base_patterns)
            
            if platform.lower() in platform_patterns:
                patterns.extend(platform_patterns[platform.lower()])
            
            logger.info(f"IntegrationAgent: Generated {len(patterns)} integration patterns")
        
        except Exception as e:
            logger.error(f"IntegrationAgent: Pattern generation failed: {e}", exc_info=True)
        
        return patterns
    
    async def _generate_webhook_implementation(self, platform: str, events: List[str]) -> Dict[str, Any]:
        """
        Generate webhook implementation code
        """
        webhook_impl = {
            "endpoint": "",
            "handler_code": "",
            "verification": "",
            "event_processors": {},
            "error": None
        }
        
        try:
            logger.info(f"IntegrationAgent: Generating webhook implementation for {platform}")
            
            webhook_impl["endpoint"] = f"/webhooks/{platform.lower()}"
            
            # Generate handler code
            webhook_impl["handler_code"] = f"""
from fastapi import APIRouter, Request, HTTPException, Header
from typing import Optional
import hmac
import hashlib
import json

router = APIRouter()

def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    \"\"\"Verify webhook signature\"\"\"
    expected_signature = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected_signature)

@router.post("{webhook_impl['endpoint']}")
async def handle_{platform.lower()}_webhook(
    request: Request,
    x_{platform.lower()}_signature: Optional[str] = Header(None)
):
    \"\"\"Handle {platform} webhook events\"\"\"
    payload = await request.body()
    
    # Verify signature
    secret = get_webhook_secret("{platform}")
    if not verify_webhook_signature(payload, x_{platform.lower()}_signature, secret):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    event = json.loads(payload)
    event_type = event.get("type") or event.get("action")
    event_id = event.get("id") or event.get("event_id")
    
    # Check idempotency
    if await is_event_processed(event_id):
        return {{"status": "already_processed"}}
    
    # Process event based on type
    processor = get_event_processor(event_type)
    if processor:
        await processor(event)
    
    await mark_event_processed(event_id)
    return {{"status": "success", "event_id": event_id}}
"""
            
            # Generate event processors
            for event in events:
                webhook_impl["event_processors"][event] = f"""
async def process_{event}_event(event: dict):
    \"\"\"Process {event} event from {platform}\"\"\"
    # Extract event data
    event_data = event.get("data", event)
    
    # Process based on event type
    # TODO: Implement event-specific logic
    
    logger.info(f"Processed {event} event: {{event.get('id')}}")
"""
            
            # Generate verification endpoint
            webhook_impl["verification"] = f"""
@router.get("{webhook_impl['endpoint']}")
async def verify_{platform.lower()}_webhook(
    challenge: str = None,
    mode: str = None,
    token: str = None
):
    \"\"\"Verify {platform} webhook subscription\"\"\"
    # Some platforms require webhook verification
    if challenge:
        return {{"challenge": challenge}}
    return {{"status": "verified"}}
"""
            
            logger.info(f"IntegrationAgent: Generated webhook implementation for {len(events)} events")
        
        except Exception as e:
            webhook_impl["error"] = f"Webhook implementation generation failed: {str(e)}"
            logger.error(f"IntegrationAgent: Webhook implementation generation failed: {e}", exc_info=True)
        
        return webhook_impl
    
    async def _generate_oauth2_flow(self, platform: str, scopes: List[str]) -> Dict[str, Any]:
        """
        Generate OAuth2 flow implementation
        """
        oauth2_flow = {
            "client_code": "",
            "authorization_url": "",
            "token_exchange": "",
            "token_refresh": "",
            "error": None
        }
        
        try:
            logger.info(f"IntegrationAgent: Generating OAuth2 flow for {platform}")
            
            # Generate OAuth2 client
            oauth2_flow["client_code"] = f"""
class {platform.title()}OAuth2Client:
    \"\"\"OAuth2 client for {platform}\"\"\"
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.auth_url = "https://{platform.lower()}.com/oauth/authorize"
        self.token_url = "https://{platform.lower()}.com/oauth/token"
        self.scopes = {scopes}
    
    def get_authorization_url(self, state: str) -> str:
        \"\"\"Generate authorization URL\"\"\"
        from urllib.parse import urlencode
        
        params = {{
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.scopes),
            "state": state
        }}
        return f"{{self.auth_url}}?{{urlencode(params)}}"
    
    async def exchange_code_for_token(self, code: str) -> dict:
        \"\"\"Exchange authorization code for access token\"\"\"
        import requests
        
        data = {{
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri
        }}
        
        response = requests.post(self.token_url, data=data)
        response.raise_for_status()
        return response.json()
    
    async def refresh_token(self, refresh_token: str) -> dict:
        \"\"\"Refresh access token\"\"\"
        import requests
        
        data = {{
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }}
        
        response = requests.post(self.token_url, data=data)
        response.raise_for_status()
        return response.json()
    
    def get_authenticated_session(self, access_token: str):
        \"\"\"Create authenticated requests session\"\"\"
        import requests
        session = requests.Session()
        session.headers.update({{
            "Authorization": f"Bearer {{access_token}}"
        }})
        return session
"""
            
            # Generate authorization endpoint
            oauth2_flow["authorization_url"] = f"""
@router.get("/auth/{platform.lower()}/authorize")
async def authorize_{platform.lower()}():
    \"\"\"Initiate {platform} OAuth2 authorization\"\"\"
    import secrets
    
    state = secrets.token_urlsafe(32)
    oauth_client = {platform.title()}OAuth2Client(
        client_id=get_client_id("{platform}"),
        client_secret=get_client_secret("{platform}"),
        redirect_uri=get_redirect_uri("{platform}")
    )
    
    auth_url = oauth_client.get_authorization_url(state)
    await store_oauth_state(state)
    
    return {{"authorization_url": auth_url, "state": state}}
"""
            
            # Generate callback endpoint
            oauth2_flow["token_exchange"] = f"""
@router.get("/auth/{platform.lower()}/callback")
async def {platform.lower()}_oauth_callback(code: str, state: str):
    \"\"\"Handle {platform} OAuth2 callback\"\"\"
    # Verify state
    if not await verify_oauth_state(state):
        raise HTTPException(status_code=400, detail="Invalid state")
    
    # Exchange code for token
    oauth_client = {platform.title()}OAuth2Client(
        client_id=get_client_id("{platform}"),
        client_secret=get_client_secret("{platform}"),
        redirect_uri=get_redirect_uri("{platform}")
    )
    
    token_data = await oauth_client.exchange_code_for_token(code)
    
    # Store tokens
    await store_tokens("{platform}", token_data)
    
    return {{"status": "success", "access_token": token_data.get("access_token")[:20] + "..."}}
"""
            
            logger.info(f"IntegrationAgent: Generated OAuth2 flow for {platform}")
        
        except Exception as e:
            oauth2_flow["error"] = f"OAuth2 flow generation failed: {str(e)}"
            logger.error(f"IntegrationAgent: OAuth2 flow generation failed: {e}", exc_info=True)
        
        return oauth2_flow
    
    async def execute(
        self,
        task_id: str,
        target: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute enhanced integration design with patterns, webhooks, and OAuth2
        Overrides BaseAgent.execute to add comprehensive integration capabilities
        """
        execution_start = time.time()
        
        try:
            logger.info(f"IntegrationAgent: Starting enhanced integration design for {target}")
            
            platform = parameters.get("platform", target)
            integration_type = parameters.get("integration_type", "api")
            events = parameters.get("events", [])
            scopes = parameters.get("scopes", ["read", "write"])
            generate_patterns = parameters.get("generate_patterns", True)
            generate_webhook = parameters.get("generate_webhook", False)
            generate_oauth2 = parameters.get("generate_oauth2", False)
            
            # STEP 1: Generate integration patterns
            patterns = []
            if generate_patterns:
                patterns = await self._generate_integration_patterns(platform, integration_type)
            
            # STEP 2: Generate webhook implementation
            webhook_impl = {}
            if generate_webhook and events:
                webhook_impl = await self._generate_webhook_implementation(platform, events)
            
            # STEP 3: Generate OAuth2 flow
            oauth2_flow = {}
            if generate_oauth2:
                oauth2_flow = await self._generate_oauth2_flow(platform, scopes)
            
            # STEP 4: Prepare enhanced prompt
            prompt = await self._prepare_prompt(
                target, parameters, patterns, webhook_impl, oauth2_flow
            )
            
            # STEP 5: Call AI via router
            logger.info(f"IntegrationAgent: Calling AI with integration patterns and implementations")
            
            ai_response = await self.ai_router.generate_with_fallback(
                prompt=prompt,
                model_preference=self.model_preference,
                max_tokens=4000,
                temperature=0.3,
                system_prompt=self.system_prompt,
                strategy=self.strategy
            )
            
            logger.info(f"IntegrationAgent: Got response from {ai_response.provider} "
                       f"({ai_response.tokens_used} tokens, ${ai_response.cost_usd:.4f})")
            
            # STEP 6: Parse response
            parsed_result = await self._parse_response(ai_response.content)
            
            # STEP 7: Merge generated implementations
            if parsed_result.get("success") and parsed_result.get("integration_design"):
                integration_design = parsed_result["integration_design"]
                
                # Merge patterns
                if patterns:
                    integration_design["integration_patterns"] = patterns
                
                # Merge webhook implementation
                if webhook_impl:
                    integration_design["webhook_implementation"] = webhook_impl
                
                # Merge OAuth2 flow
                if oauth2_flow:
                    integration_design["oauth2_flow"] = oauth2_flow
            
            execution_duration = time.time() - execution_start
            
            # Update stats
            self.executions += 1
            self.successes += 1
            self.total_duration += execution_duration
            
            return {
                "success": parsed_result.get("success", True),
                "result": parsed_result.get("integration_design", {}),
                "output": parsed_result.get("integration_design", {}),
                "quality_score": 0.85,
                "duration": execution_duration,
                "tokens_used": ai_response.tokens_used,
                "cost_usd": ai_response.cost_usd,
                "provider": ai_response.provider,
                "summary": f"Designed integration for {platform}: {len(patterns)} patterns, webhook: {bool(webhook_impl)}, OAuth2: {bool(oauth2_flow)}"
            }
        
        except Exception as e:
            execution_duration = time.time() - execution_start
            logger.error(f"IntegrationAgent: Execution failed: {e}", exc_info=True)
            
            self.executions += 1
            self.total_duration += execution_duration
            
            return {
                "success": False,
                "error": str(e),
                "duration": execution_duration,
                "quality_score": 0.0
            }
    
    async def _prepare_prompt(
        self,
        target: str,
        parameters: Dict[str, Any],
        patterns: List[Dict[str, Any]] = None,
        webhook_impl: Dict[str, Any] = None,
        oauth2_flow: Dict[str, Any] = None
    ) -> str:
        """Prepare enhanced integration prompt with all generated implementations"""
        
        platform = parameters.get("platform", target)
        integration_type = parameters.get("integration_type", "api")
        requirements = parameters.get("requirements", {})
        existing_code = parameters.get("existing_code", "")
        
        # Build context from generated implementations
        implementation_context = ""
        
        if patterns:
            implementation_context += f"\n=== GENERATED INTEGRATION PATTERNS ===\n"
            implementation_context += f"Patterns: {len(patterns)}\n"
            for pattern in patterns[:5]:
                implementation_context += f"  - {pattern.get('name')}: {pattern.get('description')}\n"
        
        if webhook_impl:
            implementation_context += f"\n=== GENERATED WEBHOOK IMPLEMENTATION ===\n"
            implementation_context += f"Endpoint: {webhook_impl.get('endpoint')}\n"
            implementation_context += f"Events: {len(webhook_impl.get('event_processors', {}))}\n"
        
        if oauth2_flow:
            implementation_context += f"\n=== GENERATED OAUTH2 FLOW ===\n"
            implementation_context += f"OAuth2 client: Generated\n"
            implementation_context += f"Authorization URL: Generated\n"
            implementation_context += f"Token exchange: Generated\n"
        
        prompt = f"""Design integration for: {platform}

Integration Type: {integration_type}

{implementation_context}

Requirements:
{json.dumps(requirements, indent=2) if requirements else "No specific requirements"}

Existing Code (if reviewing):
{existing_code[:3000] if existing_code else "New integration"}

Based on the GENERATED INTEGRATION PATTERNS, WEBHOOK IMPLEMENTATION, and OAUTH2 FLOW above, please provide:
1. Complete integration architecture (use generated patterns)
2. API client implementation (enhance generated patterns)
3. Webhook handling strategy (use generated webhook implementation)
4. OAuth2 authentication flow (use generated OAuth2 flow)
5. Error handling and retry logic
6. Rate limiting implementation
7. Data transformation logic
8. Testing strategy

IMPORTANT:
- Reference the generated integration patterns
- Use the generated webhook implementation
- Use the generated OAuth2 flow
- Ensure production-ready code

Format your response as JSON with the following structure:
{{
    "integration_patterns": {json.dumps(patterns) if patterns else []},
    "authentication": {{
        "type": "oauth2|api_key|basic",
        "implementation": "...",
        "oauth2_flow": {json.dumps(oauth2_flow) if oauth2_flow else {}}
    }},
    "api_client": "...",
    "webhook_handler": {json.dumps(webhook_impl) if webhook_impl else {}},
    "error_handling": {{
        "retry_strategy": "...",
        "error_codes": {{...}}
    }},
    "rate_limiting": "...",
    "data_transformation": "...",
    "test_code": "..."
}}"""
        
        return prompt


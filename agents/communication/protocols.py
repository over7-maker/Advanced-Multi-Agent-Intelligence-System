"""
AMAS Agent Communication Protocols

Standardized communication protocols for inter-agent coordination:
- Message format specifications
- Conversation patterns and workflows
- Protocol validation and compliance
- Communication security standards
- Error handling and recovery protocols

Ensures reliable and secure agent-to-agent communication.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Protocol, runtime_checkable
from enum import Enum
from dataclasses import dataclass, field
import json
import uuid

logger = logging.getLogger(__name__)


class ProtocolVersion(Enum):
    """Communication protocol versions"""
    V1_0 = "1.0"
    V1_1 = "1.1"
    V2_0 = "2.0"


class ConversationState(Enum):
    """States in agent conversations"""
    INITIATED = "initiated"
    IN_PROGRESS = "in_progress"
    WAITING_RESPONSE = "waiting_response"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class SecurityLevel(Enum):
    """Security levels for communication"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"
    TOP_SECRET = "top_secret"


@runtime_checkable
class CommunicationProtocol(Protocol):
    """Protocol interface for agent communication"""
    
    async def send_message(self, message: Dict[str, Any]) -> bool:
        """Send a message following the protocol"""
        ...
    
    async def receive_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Receive and process a message"""
        ...
    
    async def validate_message(self, message: Dict[str, Any]) -> bool:
        """Validate message format and content"""
        ...


@dataclass
class ConversationContext:
    """Context for ongoing agent conversations"""
    conversation_id: str
    participants: List[str]
    initiator: str
    topic: str
    state: ConversationState
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    messages: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    security_level: SecurityLevel = SecurityLevel.INTERNAL
    expires_at: Optional[datetime] = None


@dataclass
class MessageSchema:
    """Schema definition for agent messages"""
    required_fields: List[str]
    optional_fields: List[str]
    field_types: Dict[str, type]
    validation_rules: Dict[str, Any]
    security_requirements: Dict[str, Any]


class StandardCommunicationProtocols:
    """
    Standard communication protocols for AMAS agent interactions.
    
    Implements common communication patterns:
    - Request-Response
    - Task Delegation
    - Information Sharing
    - Collaborative Problem Solving
    - Status Reporting
    """
    
    def __init__(self):
        self.protocol_version = ProtocolVersion.V2_0
        self.conversations: Dict[str, ConversationContext] = {}
        self.message_schemas = self._initialize_message_schemas()
        self.security_validator = SecurityValidator()
        
        logger.info(f"Communication Protocols initialized (version {self.protocol_version.value})")
    
    def _initialize_message_schemas(self) -> Dict[str, MessageSchema]:
        """Initialize message schemas for validation"""
        schemas = {}
        
        # Task delegation schema
        schemas['task_delegation'] = MessageSchema(
            required_fields=['action', 'task_id', 'task_type', 'description'],
            optional_fields=['parameters', 'deadline', 'priority', 'context'],
            field_types={
                'action': str,
                'task_id': str,
                'task_type': str,
                'description': str,
                'parameters': dict,
                'deadline': str,
                'priority': int
            },
            validation_rules={
                'task_id': {'min_length': 8, 'pattern': r'^[a-zA-Z0-9_-]+$'},
                'description': {'min_length': 10, 'max_length': 1000},
                'priority': {'min': 1, 'max': 5}
            },
            security_requirements={
                'authentication': True,
                'authorization': True,
                'audit_logging': True
            }
        )
        
        # Information request schema
        schemas['information_request'] = MessageSchema(
            required_fields=['action', 'query', 'information_type'],
            optional_fields=['context', 'format_requirements', 'urgency'],
            field_types={
                'action': str,
                'query': str,
                'information_type': str,
                'context': dict,
                'urgency': str
            },
            validation_rules={
                'query': {'min_length': 5, 'max_length': 500},
                'information_type': {'allowed_values': ['intelligence', 'analysis', 'status', 'capability']}
            },
            security_requirements={
                'authentication': True,
                'data_classification': True
            }
        )
        
        # Status update schema
        schemas['status_update'] = MessageSchema(
            required_fields=['action', 'status', 'timestamp'],
            optional_fields=['details', 'metrics', 'next_action'],
            field_types={
                'action': str,
                'status': str,
                'timestamp': str,
                'details': dict,
                'metrics': dict
            },
            validation_rules={
                'status': {'allowed_values': ['active', 'busy', 'idle', 'error', 'maintenance']},
                'timestamp': {'format': 'iso8601'}
            },
            security_requirements={
                'authentication': True
            }
        )
        
        return schemas
    
    async def validate_message(
        self,
        message: Dict[str, Any],
        message_type: str
    ) -> Tuple[bool, List[str]]:
        """
        Validate message against protocol schema.
        
        Args:
            message: Message to validate
            message_type: Type of message for schema selection
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        try:
            if message_type not in self.message_schemas:
                return False, [f"Unknown message type: {message_type}"]
            
            schema = self.message_schemas[message_type]
            errors = []
            
            # Check required fields
            for field in schema.required_fields:
                if field not in message:
                    errors.append(f"Missing required field: {field}")
                elif not isinstance(message[field], schema.field_types.get(field, str)):
                    errors.append(f"Invalid type for field {field}")
            
            # Validate field values
            for field, rules in schema.validation_rules.items():
                if field in message:
                    value = message[field]
                    
                    # String validations
                    if isinstance(value, str):
                        if 'min_length' in rules and len(value) < rules['min_length']:
                            errors.append(f"Field {field} too short (min: {rules['min_length']})")
                        if 'max_length' in rules and len(value) > rules['max_length']:
                            errors.append(f"Field {field} too long (max: {rules['max_length']})")
                        if 'pattern' in rules and not re.match(rules['pattern'], value):
                            errors.append(f"Field {field} doesn't match required pattern")
                        if 'allowed_values' in rules and value not in rules['allowed_values']:
                            errors.append(f"Field {field} has invalid value: {value}")
                    
                    # Numeric validations
                    if isinstance(value, (int, float)):
                        if 'min' in rules and value < rules['min']:
                            errors.append(f"Field {field} below minimum: {rules['min']}")
                        if 'max' in rules and value > rules['max']:
                            errors.append(f"Field {field} above maximum: {rules['max']}")
            
            # Security validation
            security_errors = await self.security_validator.validate_message_security(
                message, schema.security_requirements
            )
            errors.extend(security_errors)
            
            return len(errors) == 0, errors
            
        except Exception as e:
            logger.error(f"Error validating message: {e}")
            return False, [f"Validation error: {str(e)}"]
    
    async def start_conversation(
        self,
        initiator: str,
        participants: List[str],
        topic: str,
        security_level: SecurityLevel = SecurityLevel.INTERNAL
    ) -> str:
        """
        Start a new conversation between agents.
        
        Args:
            initiator: Agent starting the conversation
            participants: List of participating agents
            topic: Conversation topic
            security_level: Security level for the conversation
            
        Returns:
            Conversation ID
        """
        try:
            conversation_id = str(uuid.uuid4())
            
            context = ConversationContext(
                conversation_id=conversation_id,
                participants=participants,
                initiator=initiator,
                topic=topic,
                state=ConversationState.INITIATED,
                security_level=security_level,
                expires_at=datetime.utcnow() + timedelta(hours=24)  # Default 24 hour expiry
            )
            
            self.conversations[conversation_id] = context
            
            logger.info(f"Conversation {conversation_id} started by {initiator} on topic: {topic}")
            
            return conversation_id
            
        except Exception as e:
            logger.error(f"Error starting conversation: {e}")
            raise
    
    async def add_message_to_conversation(
        self,
        conversation_id: str,
        message_id: str
    ) -> bool:
        """Add a message to an ongoing conversation"""
        try:
            if conversation_id not in self.conversations:
                logger.warning(f"Conversation {conversation_id} not found")
                return False
            
            context = self.conversations[conversation_id]
            context.messages.append(message_id)
            context.last_activity = datetime.utcnow()
            
            # Update conversation state
            if context.state == ConversationState.INITIATED:
                context.state = ConversationState.IN_PROGRESS
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding message to conversation: {e}")
            return False
    
    async def end_conversation(
        self,
        conversation_id: str,
        ending_agent: str,
        reason: str = "completed"
    ) -> bool:
        """End an ongoing conversation"""
        try:
            if conversation_id not in self.conversations:
                logger.warning(f"Conversation {conversation_id} not found")
                return False
            
            context = self.conversations[conversation_id]
            
            if ending_agent not in context.participants:
                logger.warning(f"Agent {ending_agent} not participant in conversation {conversation_id}")
                return False
            
            context.state = ConversationState.COMPLETED
            context.metadata['ended_by'] = ending_agent
            context.metadata['end_reason'] = reason
            context.metadata['ended_at'] = datetime.utcnow().isoformat()
            
            logger.info(f"Conversation {conversation_id} ended by {ending_agent}: {reason}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error ending conversation: {e}")
            return False
    
    def get_conversation_status(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a conversation"""
        if conversation_id not in self.conversations:
            return None
        
        context = self.conversations[conversation_id]
        return {
            'conversation_id': conversation_id,
            'state': context.state.value,
            'participants': context.participants,
            'initiator': context.initiator,
            'topic': context.topic,
            'message_count': len(context.messages),
            'created_at': context.created_at.isoformat(),
            'last_activity': context.last_activity.isoformat(),
            'security_level': context.security_level.value,
            'expires_at': context.expires_at.isoformat() if context.expires_at else None
        }


class SecurityValidator:
    """Security validation for agent communications"""
    
    async def validate_message_security(
        self,
        message: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> List[str]:
        """Validate message security requirements"""
        errors = []
        
        try:
            # Check authentication requirement
            if requirements.get('authentication', False):
                if 'sender_auth' not in message or not message['sender_auth']:
                    errors.append("Authentication required but not provided")
            
            # Check authorization requirement
            if requirements.get('authorization', False):
                if 'permissions' not in message:
                    errors.append("Authorization permissions not specified")
            
            # Check data classification
            if requirements.get('data_classification', False):
                if 'security_level' not in message:
                    errors.append("Data security level not specified")
            
            # Check audit logging requirement
            if requirements.get('audit_logging', False):
                if 'audit_info' not in message:
                    errors.append("Audit information required but not provided")
            
            return errors
            
        except Exception as e:
            logger.error(f"Error in security validation: {e}")
            return [f"Security validation error: {str(e)}"]


class ConversationManager:
    """
    Manager for multi-agent conversations and collaborative workflows.
    
    Handles complex multi-party communication patterns and ensures
    proper conversation flow and context management.
    """
    
    def __init__(self, message_bus):
        self.message_bus = message_bus
        self.protocols = StandardCommunicationProtocols()
        self.active_conversations: Dict[str, ConversationContext] = {}
        self.conversation_templates = self._initialize_conversation_templates()
        
        logger.info("Conversation Manager initialized")
    
    def _initialize_conversation_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize templates for common conversation patterns"""
        return {
            'intelligence_briefing': {
                'participants_required': ['osint_agent', 'analysis_agent', 'reporting_agent'],
                'flow': [
                    {'step': 'data_collection', 'agent': 'osint_agent'},
                    {'step': 'analysis', 'agent': 'analysis_agent'},
                    {'step': 'report_generation', 'agent': 'reporting_agent'}
                ],
                'timeout_minutes': 60
            },
            'collaborative_investigation': {
                'participants_required': ['investigation_agent', 'forensics_agent', 'osint_agent'],
                'flow': [
                    {'step': 'evidence_gathering', 'agent': 'multiple'},
                    {'step': 'correlation', 'agent': 'investigation_agent'},
                    {'step': 'validation', 'agent': 'forensics_agent'}
                ],
                'timeout_minutes': 120
            },
            'threat_assessment': {
                'participants_required': ['osint_agent', 'analysis_agent'],
                'flow': [
                    {'step': 'threat_data_collection', 'agent': 'osint_agent'},
                    {'step': 'threat_analysis', 'agent': 'analysis_agent'},
                    {'step': 'risk_scoring', 'agent': 'analysis_agent'}
                ],
                'timeout_minutes': 30
            }
        }
    
    async def initiate_collaborative_workflow(
        self,
        workflow_type: str,
        initiator: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Initiate a collaborative workflow between multiple agents.
        
        Args:
            workflow_type: Type of collaborative workflow
            initiator: Agent initiating the workflow
            context: Workflow context and parameters
            
        Returns:
            Conversation ID for the workflow
        """
        try:
            if workflow_type not in self.conversation_templates:
                raise ValueError(f"Unknown workflow type: {workflow_type}")
            
            template = self.conversation_templates[workflow_type]
            
            # Start conversation
            conversation_id = await self.protocols.start_conversation(
                initiator=initiator,
                participants=template['participants_required'],
                topic=f"Collaborative {workflow_type}",
                security_level=SecurityLevel.INTERNAL
            )
            
            # Initialize workflow context
            workflow_context = {
                'workflow_type': workflow_type,
                'template': template,
                'current_step': 0,
                'step_results': {},
                'context': context
            }
            
            conversation = self.protocols.conversations[conversation_id]
            conversation.metadata['workflow'] = workflow_context
            
            # Send initial workflow message to participants
            await self._send_workflow_initiation_message(conversation_id, workflow_context)
            
            logger.info(f"Collaborative workflow {workflow_type} initiated (conversation: {conversation_id})")
            
            return conversation_id
            
        except Exception as e:
            logger.error(f"Error initiating collaborative workflow: {e}")
            raise
    
    async def _send_workflow_initiation_message(
        self,
        conversation_id: str,
        workflow_context: Dict[str, Any]
    ):
        """Send workflow initiation message to all participants"""
        try:
            conversation = self.protocols.conversations[conversation_id]
            
            initiation_payload = {
                'action': 'workflow_initiation',
                'conversation_id': conversation_id,
                'workflow_type': workflow_context['workflow_type'],
                'your_role': 'participant',
                'workflow_steps': workflow_context['template']['flow'],
                'context': workflow_context['context'],
                'instructions': 'Prepare for collaborative workflow execution'
            }
            
            # Send to all participants except initiator
            for participant in conversation.participants:
                if participant != conversation.initiator:
                    await self.message_bus.send_message(
                        from_agent=conversation.initiator,
                        to_agent=participant,
                        message_type=MessageType.COLLABORATION_REQUEST,
                        payload=initiation_payload,
                        priority=MessagePriority.HIGH,
                        conversation_id=conversation_id
                    )
            
        except Exception as e:
            logger.error(f"Error sending workflow initiation: {e}")
    
    async def process_workflow_step(
        self,
        conversation_id: str,
        step_result: Dict[str, Any],
        completing_agent: str
    ) -> Dict[str, Any]:
        """
        Process completion of a workflow step and advance to next step.
        
        Args:
            conversation_id: Conversation ID
            step_result: Result from completed step
            completing_agent: Agent that completed the step
            
        Returns:
            Next step information or workflow completion status
        """
        try:
            if conversation_id not in self.protocols.conversations:
                raise ValueError(f"Conversation {conversation_id} not found")
            
            conversation = self.protocols.conversations[conversation_id]
            workflow_context = conversation.metadata.get('workflow', {})
            
            if not workflow_context:
                raise ValueError("No workflow context found in conversation")
            
            # Store step result
            current_step = workflow_context['current_step']
            workflow_context['step_results'][current_step] = {
                'result': step_result,
                'completed_by': completing_agent,
                'completed_at': datetime.utcnow().isoformat()
            }
            
            # Advance to next step
            template = workflow_context['template']
            workflow_context['current_step'] += 1
            
            # Check if workflow is complete
            if workflow_context['current_step'] >= len(template['flow']):
                # Workflow complete
                await self._complete_workflow(conversation_id, workflow_context)
                return {
                    'status': 'workflow_completed',
                    'final_results': workflow_context['step_results']
                }
            else:
                # Continue to next step
                next_step = template['flow'][workflow_context['current_step']]
                await self._initiate_next_workflow_step(conversation_id, next_step, workflow_context)
                return {
                    'status': 'step_completed',
                    'next_step': next_step,
                    'current_step': workflow_context['current_step']
                }
            
        except Exception as e:
            logger.error(f"Error processing workflow step: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _complete_workflow(
        self,
        conversation_id: str,
        workflow_context: Dict[str, Any]
    ):
        """Complete a collaborative workflow"""
        try:
            # Send completion message to all participants
            conversation = self.protocols.conversations[conversation_id]
            
            completion_payload = {
                'action': 'workflow_completed',
                'conversation_id': conversation_id,
                'workflow_type': workflow_context['workflow_type'],
                'final_results': workflow_context['step_results'],
                'completed_at': datetime.utcnow().isoformat()
            }
            
            for participant in conversation.participants:
                await self.message_bus.send_message(
                    from_agent='system',
                    to_agent=participant,
                    message_type=MessageType.STATUS_UPDATE,
                    payload=completion_payload,
                    priority=MessagePriority.HIGH,
                    conversation_id=conversation_id
                )
            
            # End conversation
            await self.protocols.end_conversation(
                conversation_id=conversation_id,
                ending_agent='system',
                reason='workflow_completed'
            )
            
            logger.info(f"Workflow {workflow_context['workflow_type']} completed (conversation: {conversation_id})")
            
        except Exception as e:
            logger.error(f"Error completing workflow: {e}")
    
    async def _initiate_next_workflow_step(
        self,
        conversation_id: str,
        next_step: Dict[str, Any],
        workflow_context: Dict[str, Any]
    ):
        """Initiate the next step in a workflow"""
        try:
            conversation = self.protocols.conversations[conversation_id]
            
            # Determine which agent should execute the next step
            step_agent = next_step['agent']
            
            if step_agent == 'multiple':
                # Multiple agents involved - broadcast to all
                for participant in conversation.participants:
                    await self._send_step_instruction(
                        conversation_id, participant, next_step, workflow_context
                    )
            else:
                # Single agent
                await self._send_step_instruction(
                    conversation_id, step_agent, next_step, workflow_context
                )
            
        except Exception as e:
            logger.error(f"Error initiating next workflow step: {e}")
    
    async def _send_step_instruction(
        self,
        conversation_id: str,
        target_agent: str,
        step: Dict[str, Any],
        workflow_context: Dict[str, Any]
    ):
        """Send step instruction to specific agent"""
        try:
            step_payload = {
                'action': 'execute_workflow_step',
                'conversation_id': conversation_id,
                'step_name': step['step'],
                'step_index': workflow_context['current_step'],
                'instructions': f"Execute {step['step']} as part of {workflow_context['workflow_type']} workflow",
                'context': workflow_context['context'],
                'previous_results': workflow_context.get('step_results', {}),
                'response_required': True
            }
            
            await self.message_bus.send_message(
                from_agent='system',
                to_agent=target_agent,
                message_type=MessageType.TASK_DELEGATION,
                payload=step_payload,
                priority=MessagePriority.HIGH,
                response_expected=True,
                conversation_id=conversation_id
            )
            
        except Exception as e:
            logger.error(f"Error sending step instruction: {e}")
    
    async def get_conversation_summary(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive summary of a conversation"""
        try:
            if conversation_id not in self.protocols.conversations:
                return None
            
            context = self.protocols.conversations[conversation_id]
            
            return {
                'conversation_id': conversation_id,
                'state': context.state.value,
                'participants': context.participants,
                'initiator': context.initiator,
                'topic': context.topic,
                'security_level': context.security_level.value,
                'created_at': context.created_at.isoformat(),
                'last_activity': context.last_activity.isoformat(),
                'message_count': len(context.messages),
                'workflow_info': context.metadata.get('workflow', {}),
                'duration_minutes': (
                    (context.last_activity - context.created_at).total_seconds() / 60
                ),
                'is_active': context.state in [ConversationState.IN_PROGRESS, ConversationState.WAITING_RESPONSE]
            }
            
        except Exception as e:
            logger.error(f"Error getting conversation summary: {e}")
            return None


# Import the MessageType from message_bus for consistency
from agents.communication.message_bus import MessageType, MessagePriority
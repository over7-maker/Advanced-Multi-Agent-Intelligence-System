"""
AMAS Agent Communication Tests

Comprehensive test suite for the advanced agent communication system:
- Message bus functionality
- Communication protocols
- State management
- Conversation management
- Security validation
- Performance testing

Validates reliable inter-agent communication with enterprise-grade features.
"""

import pytest
import asyncio
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

# Import communication components
from agents.communication.message_bus import (
    AdvancedMessageBus, AgentMessage, MessageType, MessagePriority, MessageStatus,
    CommunicationChannel, AgentCommunicationProtocol
)
from agents.communication.protocols import (
    StandardCommunicationProtocols, ConversationContext, ConversationState,
    SecurityLevel, MessageSchema, SecurityValidator
)
from core.state_manager import (
    AdvancedStateManager, StateEntry, StateScope, AccessLevel, StateOperation,
    StateLock, StateSnapshot
)


class TestAdvancedMessageBus:
    """Test suite for the Advanced Message Bus"""
    
    @pytest.fixture
    async def message_bus(self):
        """Create message bus for testing"""
        config = {
            'max_queue_size': 100,
            'message_ttl_seconds': 3600,
            'delivery_timeout_seconds': 30,
            'heartbeat_interval_seconds': 60
        }
        bus = AdvancedMessageBus(config)
        await bus.start()
        yield bus
        await bus.stop()
    
    @pytest.mark.asyncio
    async def test_message_bus_initialization(self, message_bus):
        """Test message bus initialization"""
        assert message_bus is not None
        assert hasattr(message_bus, 'messages')
        assert hasattr(message_bus, 'message_queues')
        assert hasattr(message_bus, 'registered_agents')
        assert hasattr(message_bus, 'communication_channels')
        assert message_bus._running is True
    
    @pytest.mark.asyncio
    async def test_agent_registration(self, message_bus):
        """Test agent registration with message bus"""
        agent_info = {
            'name': 'Test Agent',
            'capabilities': ['test_capability'],
            'type': 'test'
        }
        
        # Test successful registration
        result = await message_bus.register_agent('test_agent_001', agent_info)
        assert result is True
        assert 'test_agent_001' in message_bus.registered_agents
        assert 'test_agent_001' in message_bus.message_queues
        
        # Test duplicate registration
        result = await message_bus.register_agent('test_agent_001', agent_info)
        assert result is False  # Should fail for duplicate
    
    @pytest.mark.asyncio
    async def test_message_sending(self, message_bus):
        """Test message sending between agents"""
        # Register agents
        await message_bus.register_agent('agent_a', {'name': 'Agent A'})
        await message_bus.register_agent('agent_b', {'name': 'Agent B'})
        
        # Send message
        payload = {'test_data': 'Hello from Agent A'}
        message_id = await message_bus.send_message(
            from_agent='agent_a',
            to_agent='agent_b',
            message_type=MessageType.INFORMATION_REQUEST,
            payload=payload,
            priority=MessagePriority.HIGH
        )
        
        assert message_id is not None
        assert message_id in message_bus.messages
        
        # Check message details
        message = message_bus.messages[message_id]
        assert message.from_agent == 'agent_a'
        assert message.to_agent == 'agent_b'
        assert message.message_type == MessageType.INFORMATION_REQUEST
        assert message.priority == MessagePriority.HIGH
        assert message.payload == payload
    
    @pytest.mark.asyncio
    async def test_message_retrieval(self, message_bus):
        """Test message retrieval by agents"""
        # Register agents
        await message_bus.register_agent('agent_a', {'name': 'Agent A'})
        await message_bus.register_agent('agent_b', {'name': 'Agent B'})
        
        # Send multiple messages
        for i in range(3):
            await message_bus.send_message(
                from_agent='agent_a',
                to_agent='agent_b',
                message_type=MessageType.STATUS_UPDATE,
                payload={'update': f'Update {i}'},
                priority=MessagePriority.MEDIUM
            )
        
        # Retrieve messages
        messages = await message_bus.get_messages('agent_b', limit=5)
        
        assert len(messages) == 3
        assert all(msg.to_agent == 'agent_b' for msg in messages)
        assert all(msg.status == MessageStatus.DELIVERED for msg in messages)
    
    @pytest.mark.asyncio
    async def test_message_acknowledgment(self, message_bus):
        """Test message acknowledgment"""
        # Register agents
        await message_bus.register_agent('agent_a', {'name': 'Agent A'})
        await message_bus.register_agent('agent_b', {'name': 'Agent B'})
        
        # Send message
        message_id = await message_bus.send_message(
            from_agent='agent_a',
            to_agent='agent_b',
            message_type=MessageType.TASK_DELEGATION,
            payload={'task': 'test_task'},
            priority=MessagePriority.HIGH
        )
        
        # Retrieve message
        messages = await message_bus.get_messages('agent_b', limit=1)
        assert len(messages) == 1
        assert messages[0].status == MessageStatus.DELIVERED
        
        # Acknowledge message
        result = await message_bus.acknowledge_message('agent_b', message_id)
        assert result is True
        
        # Check status updated
        message = message_bus.messages[message_id]
        assert message.status == MessageStatus.ACKNOWLEDGED
    
    @pytest.mark.asyncio
    async def test_task_delegation(self, message_bus):
        """Test task delegation between agents"""
        # Register agents
        await message_bus.register_agent('manager_agent', {'name': 'Manager'})
        await message_bus.register_agent('worker_agent', {'name': 'Worker'})
        
        # Delegate task
        task_data = {
            'task_id': 'test_task_001',
            'task_type': 'osint',
            'description': 'Collect intelligence on target',
            'parameters': {'target': 'example.com'}
        }
        
        message_id = await message_bus.delegate_task(
            from_agent='manager_agent',
            to_agent='worker_agent',
            task_data=task_data,
            priority=MessagePriority.HIGH
        )
        
        assert message_id is not None
        
        # Check delegation message
        message = message_bus.messages[message_id]
        assert message.message_type == MessageType.TASK_DELEGATION
        assert message.response_expected is True
        assert 'delegation_id' in message.payload
        assert message.payload['task_data'] == task_data
    
    @pytest.mark.asyncio
    async def test_information_request(self, message_bus):
        """Test information request between agents"""
        # Register agents
        await message_bus.register_agent('requester', {'name': 'Requester'})
        await message_bus.register_agent('provider', {'name': 'Provider'})
        
        # Request information
        info_request = {
            'query': 'What is the current threat level?',
            'information_type': 'threat_assessment',
            'urgency': 'high'
        }
        
        message_id = await message_bus.request_information(
            from_agent='requester',
            to_agent='provider',
            information_request=info_request,
            priority=MessagePriority.HIGH
        )
        
        assert message_id is not None
        
        # Check request message
        message = message_bus.messages[message_id]
        assert message.message_type == MessageType.INFORMATION_REQUEST
        assert message.response_expected is True
        assert message.payload['request_details'] == info_request
    
    @pytest.mark.asyncio
    async def test_broadcast_messaging(self, message_bus):
        """Test broadcast messaging to multiple agents"""
        # Register multiple agents
        agents = ['agent_1', 'agent_2', 'agent_3']
        for agent_id in agents:
            await message_bus.register_agent(agent_id, {'name': f'Agent {agent_id}'})
        
        # Broadcast message
        broadcast_payload = {
            'announcement': 'System maintenance scheduled',
            'scheduled_time': '2024-01-15T02:00:00Z'
        }
        
        message_ids = await message_bus.broadcast_message(
            from_agent='system',
            message_type=MessageType.BROADCAST,
            payload=broadcast_payload,
            priority=MessagePriority.MEDIUM
        )
        
        # Should send to all agents except sender
        assert len(message_ids) == len(agents)
        
        # Check each agent received the broadcast
        for agent_id in agents:
            messages = await message_bus.get_messages(agent_id, limit=1)
            assert len(messages) == 1
            assert messages[0].message_type == MessageType.BROADCAST
            assert 'broadcast_id' in messages[0].payload
    
    @pytest.mark.asyncio
    async def test_communication_channel_creation(self, message_bus):
        """Test creation of dedicated communication channels"""
        # Register agents
        await message_bus.register_agent('agent_a', {'name': 'Agent A'})
        await message_bus.register_agent('agent_b', {'name': 'Agent B'})
        
        # Create communication channel
        channel_id = await message_bus.create_communication_channel(
            agent_a='agent_a',
            agent_b='agent_b',
            channel_type='bidirectional'
        )
        
        assert channel_id is not None
        assert channel_id in message_bus.communication_channels
        
        # Check channel details
        channel = message_bus.communication_channels[channel_id]
        assert channel.agent_a == 'agent_a'
        assert channel.agent_b == 'agent_b'
        assert channel.channel_type == 'bidirectional'
        assert channel.is_active is True
    
    @pytest.mark.asyncio
    async def test_message_expiration(self, message_bus):
        """Test message expiration and cleanup"""
        # Register agents
        await message_bus.register_agent('agent_a', {'name': 'Agent A'})
        await message_bus.register_agent('agent_b', {'name': 'Agent B'})
        
        # Send message with short TTL
        message_id = await message_bus.send_message(
            from_agent='agent_a',
            to_agent='agent_b',
            message_type=MessageType.STATUS_UPDATE,
            payload={'status': 'test'},
            ttl_seconds=1  # 1 second TTL
        )
        
        # Wait for expiration
        await asyncio.sleep(2)
        
        # Trigger cleanup
        await message_bus._cleanup_expired_messages()
        
        # Message should be expired
        if message_id in message_bus.messages:
            message = message_bus.messages[message_id]
            assert message.status == MessageStatus.EXPIRED


class TestCommunicationProtocols:
    """Test suite for Communication Protocols"""
    
    @pytest.fixture
    def protocols(self):
        """Create communication protocols for testing"""
        return StandardCommunicationProtocols()
    
    @pytest.mark.asyncio
    async def test_message_validation(self, protocols):
        """Test message validation against schemas"""
        # Valid task delegation message
        valid_message = {
            'action': 'delegate_task',
            'task_id': 'test_task_001',
            'task_type': 'osint',
            'description': 'Test task delegation message',
            'parameters': {'target': 'example.com'},
            'priority': 3
        }
        
        is_valid, errors = await protocols.validate_message(valid_message, 'task_delegation')
        assert is_valid is True
        assert len(errors) == 0
        
        # Invalid message (missing required field)
        invalid_message = {
            'action': 'delegate_task',
            'task_type': 'osint',
            'description': 'Missing task_id'
        }
        
        is_valid, errors = await protocols.validate_message(invalid_message, 'task_delegation')
        assert is_valid is False
        assert len(errors) > 0
        assert any('task_id' in error for error in errors)
    
    @pytest.mark.asyncio
    async def test_conversation_management(self, protocols):
        """Test conversation creation and management"""
        # Start conversation
        conversation_id = await protocols.start_conversation(
            initiator='agent_a',
            participants=['agent_a', 'agent_b', 'agent_c'],
            topic='Test collaboration',
            security_level=SecurityLevel.INTERNAL
        )
        
        assert conversation_id is not None
        assert conversation_id in protocols.conversations
        
        # Check conversation details
        context = protocols.conversations[conversation_id]
        assert context.initiator == 'agent_a'
        assert len(context.participants) == 3
        assert context.state == ConversationState.INITIATED
        assert context.security_level == SecurityLevel.INTERNAL
        
        # Add message to conversation
        result = await protocols.add_message_to_conversation(conversation_id, 'test_message_001')
        assert result is True
        assert 'test_message_001' in context.messages
        assert context.state == ConversationState.IN_PROGRESS
        
        # End conversation
        result = await protocols.end_conversation(conversation_id, 'agent_a', 'completed')
        assert result is True
        assert context.state == ConversationState.COMPLETED
    
    @pytest.mark.asyncio
    async def test_protocol_message_creation(self):
        """Test standardized message creation"""
        # Task delegation message
        task_msg = AgentCommunicationProtocol.create_task_delegation_message(
            task_id='test_task_001',
            task_type='osint',
            description='Test task delegation',
            parameters={'target': 'example.com'}
        )
        
        assert task_msg['action'] == 'delegate_task'
        assert task_msg['task_id'] == 'test_task_001'
        assert task_msg['task_type'] == 'osint'
        assert task_msg['response_format'] == 'structured_result'
        
        # Information request message
        info_msg = AgentCommunicationProtocol.create_information_request_message(
            query='What is the current system status?',
            information_type='status',
            context={'urgency': 'medium'}
        )
        
        assert info_msg['action'] == 'provide_information'
        assert info_msg['query'] == 'What is the current system status?'
        assert info_msg['information_type'] == 'status'
        assert info_msg['response_format'] == 'structured_data'


class TestAdvancedStateManager:
    """Test suite for the Advanced State Manager"""
    
    @pytest.fixture
    async def state_manager(self):
        """Create state manager for testing"""
        config = {
            'max_history_per_key': 50,
            'default_ttl_hours': 24,
            'lock_timeout_minutes': 5,
            'cleanup_interval_minutes': 15
        }
        manager = AdvancedStateManager(config)
        await manager.start()
        yield manager
        await manager.stop()
    
    @pytest.mark.asyncio
    async def test_state_manager_initialization(self, state_manager):
        """Test state manager initialization"""
        assert state_manager is not None
        assert hasattr(state_manager, 'state_entries')
        assert hasattr(state_manager, 'state_history')
        assert hasattr(state_manager, 'state_locks')
        assert state_manager._running is True
    
    @pytest.mark.asyncio
    async def test_basic_state_operations(self, state_manager):
        """Test basic state set/get/delete operations"""
        # Set state
        result = await state_manager.set_state(
            key='test_key',
            value={'data': 'test_value'},
            scope=StateScope.WORKFLOW,
            owner_agent='test_agent'
        )
        assert result is True
        
        # Get state
        value = await state_manager.get_state('test_key', 'test_agent')
        assert value == {'data': 'test_value'}
        
        # Delete state
        result = await state_manager.delete_state('test_key', 'test_agent')
        assert result is True
        
        # Verify deletion
        value = await state_manager.get_state('test_key', 'test_agent', default='not_found')
        assert value == 'not_found'
    
    @pytest.mark.asyncio
    async def test_state_access_control(self, state_manager):
        """Test state access control and permissions"""
        # Set private state
        await state_manager.set_state(
            key='private_key',
            value='private_data',
            scope=StateScope.AGENT,
            owner_agent='owner_agent',
            access_level=AccessLevel.PRIVATE
        )
        
        # Owner should have access
        value = await state_manager.get_state('private_key', 'owner_agent')
        assert value == 'private_data'
        
        # Other agent should not have access
        value = await state_manager.get_state('private_key', 'other_agent', default='denied')
        assert value == 'denied'
        
        # Set protected state with authorized agents
        await state_manager.set_state(
            key='protected_key',
            value='protected_data',
            scope=StateScope.WORKFLOW,
            owner_agent='owner_agent',
            access_level=AccessLevel.PROTECTED,
            authorized_agents={'authorized_agent'}
        )
        
        # Authorized agent should have access
        value = await state_manager.get_state('protected_key', 'authorized_agent')
        assert value == 'protected_data'
        
        # Unauthorized agent should not have access
        value = await state_manager.get_state('protected_key', 'unauthorized_agent', default='denied')
        assert value == 'denied'
    
    @pytest.mark.asyncio
    async def test_state_locking(self, state_manager):
        """Test state locking for concurrent access"""
        # Set initial state
        await state_manager.set_state(
            key='locked_key',
            value='initial_value',
            scope=StateScope.WORKFLOW,
            owner_agent='agent_a'
        )
        
        # Acquire lock
        lock_acquired = await state_manager._acquire_state_lock('locked_key', 'agent_a')
        assert lock_acquired is True
        assert 'locked_key' in state_manager.state_locks
        
        # Try to acquire lock with different agent (should fail)
        lock_acquired = await state_manager._acquire_state_lock('locked_key', 'agent_b')
        assert lock_acquired is False
        
        # Release lock
        lock_released = await state_manager._release_state_lock('locked_key', 'agent_a')
        assert lock_released is True
        assert 'locked_key' not in state_manager.state_locks
    
    @pytest.mark.asyncio
    async def test_state_merging(self, state_manager):
        """Test state merging functionality"""
        # Set initial state
        initial_state = {
            'data': {'field1': 'value1', 'field2': 'value2'},
            'metadata': {'created': '2024-01-01'}
        }
        
        await state_manager.set_state(
            key='merge_key',
            value=initial_state,
            scope=StateScope.WORKFLOW,
            owner_agent='agent_a'
        )
        
        # Merge partial update
        partial_update = {
            'data': {'field2': 'updated_value2', 'field3': 'new_value3'},
            'metadata': {'updated': '2024-01-15'}
        }
        
        result = await state_manager.merge_state(
            key='merge_key',
            partial_value=partial_update,
            requesting_agent='agent_a',
            merge_strategy='deep_merge'
        )
        
        assert result is True
        
        # Check merged result
        merged_value = await state_manager.get_state('merge_key', 'agent_a')
        
        assert merged_value['data']['field1'] == 'value1'  # Original value preserved
        assert merged_value['data']['field2'] == 'updated_value2'  # Updated value
        assert merged_value['data']['field3'] == 'new_value3'  # New value added
        assert merged_value['metadata']['created'] == '2024-01-01'  # Original metadata preserved
        assert merged_value['metadata']['updated'] == '2024-01-15'  # New metadata added
    
    @pytest.mark.asyncio
    async def test_state_versioning(self, state_manager):
        """Test state versioning and history"""
        # Set initial state
        await state_manager.set_state(
            key='versioned_key',
            value='version_1',
            scope=StateScope.TASK,
            owner_agent='agent_a'
        )
        
        # Update state multiple times
        for i in range(2, 5):
            await state_manager.set_state(
                key='versioned_key',
                value=f'version_{i}',
                scope=StateScope.TASK,
                owner_agent='agent_a'
            )
        
        # Check current version
        entry = state_manager.state_entries['versioned_key']
        assert entry.version == 4
        assert entry.value == 'version_4'
        
        # Check history
        history = state_manager.state_history['versioned_key']
        assert len(history) == 3  # Previous versions
        assert history[0].value == 'version_1'
        assert history[1].value == 'version_2'
        assert history[2].value == 'version_3'
    
    @pytest.mark.asyncio
    async def test_state_snapshots(self, state_manager):
        """Test state snapshot creation and management"""
        # Set multiple states
        for i in range(3):
            await state_manager.set_state(
                key=f'snapshot_key_{i}',
                value=f'snapshot_value_{i}',
                scope=StateScope.WORKFLOW,
                owner_agent='agent_a'
            )
        
        # Create snapshot
        snapshot_id = await state_manager.create_state_snapshot(
            scope=StateScope.WORKFLOW,
            scope_id='test_workflow',
            creating_agent='agent_a',
            description='Test snapshot'
        )
        
        assert snapshot_id is not None
        assert snapshot_id in state_manager.state_snapshots
        
        # Check snapshot content
        snapshot = state_manager.state_snapshots[snapshot_id]
        assert snapshot.scope == StateScope.WORKFLOW
        assert snapshot.created_by == 'agent_a'
        assert len(snapshot.state_data) == 3  # Should include all workflow-scoped states
    
    @pytest.mark.asyncio
    async def test_state_subscriptions(self, state_manager):
        """Test state change subscriptions"""
        notifications_received = []
        
        async def test_callback(notification):
            notifications_received.append(notification)
        
        # Subscribe to state changes
        subscription_id = await state_manager.subscribe_to_state_changes(
            agent_id='subscriber_agent',
            state_key_pattern='test_*',
            callback=test_callback,
            scope=StateScope.WORKFLOW
        )
        
        assert subscription_id is not None
        
        # Set state that should trigger notification
        await state_manager.set_state(
            key='test_notification_key',
            value='notification_test',
            scope=StateScope.WORKFLOW,
            owner_agent='agent_a'
        )
        
        # Give time for notification processing
        await asyncio.sleep(0.1)
        
        # Check notification received
        assert len(notifications_received) > 0
        notification = notifications_received[0]
        assert notification['state_key'] == 'test_notification_key'
        assert notification['operation'] == 'update'


class TestCommunicationPerformance:
    """Performance tests for communication system"""
    
    @pytest.mark.asyncio
    async def test_message_throughput(self):
        """Test message bus throughput"""
        config = {'max_queue_size': 1000}
        message_bus = AdvancedMessageBus(config)
        await message_bus.start()
        
        try:
            # Register agents
            await message_bus.register_agent('sender', {'name': 'Sender'})
            await message_bus.register_agent('receiver', {'name': 'Receiver'})
            
            # Send many messages rapidly
            start_time = time.time()
            message_count = 100
            
            tasks = []
            for i in range(message_count):
                task = message_bus.send_message(
                    from_agent='sender',
                    to_agent='receiver',
                    message_type=MessageType.STATUS_UPDATE,
                    payload={'update': f'Message {i}'},
                    priority=MessagePriority.MEDIUM
                )
                tasks.append(task)
            
            # Wait for all messages to be sent
            message_ids = await asyncio.gather(*tasks)
            send_time = time.time() - start_time
            
            # Calculate throughput
            throughput = message_count / send_time
            
            assert len(message_ids) == message_count
            assert throughput > 50  # Should handle at least 50 messages/second
            
            print(f"Message throughput: {throughput:.2f} messages/second")
            
        finally:
            await message_bus.stop()
    
    @pytest.mark.asyncio
    async def test_state_operation_performance(self):
        """Test state manager operation performance"""
        config = {'max_history_per_key': 100}
        state_manager = AdvancedStateManager(config)
        await state_manager.start()
        
        try:
            # Perform many state operations
            operation_count = 100
            start_time = time.time()
            
            # Set operations
            for i in range(operation_count):
                await state_manager.set_state(
                    key=f'perf_key_{i}',
                    value=f'perf_value_{i}',
                    scope=StateScope.TASK,
                    owner_agent='perf_agent'
                )
            
            set_time = time.time() - start_time
            
            # Get operations
            start_time = time.time()
            
            for i in range(operation_count):
                value = await state_manager.get_state(f'perf_key_{i}', 'perf_agent')
                assert value == f'perf_value_{i}'
            
            get_time = time.time() - start_time
            
            # Calculate performance
            set_throughput = operation_count / set_time
            get_throughput = operation_count / get_time
            
            assert set_throughput > 20  # Should handle at least 20 set operations/second
            assert get_throughput > 50  # Should handle at least 50 get operations/second
            
            print(f"State performance - Set: {set_throughput:.2f} ops/sec, Get: {get_throughput:.2f} ops/sec")
            
        finally:
            await state_manager.stop()


class TestCommunicationSecurity:
    """Security tests for communication system"""
    
    @pytest.mark.asyncio
    async def test_message_security_validation(self):
        """Test message security validation"""
        validator = SecurityValidator()
        
        # Message with all security requirements
        secure_message = {
            'sender_auth': 'valid_token',
            'permissions': ['read', 'write'],
            'security_level': 'internal',
            'audit_info': {'user_id': 'agent_001', 'timestamp': datetime.utcnow().isoformat()}
        }
        
        requirements = {
            'authentication': True,
            'authorization': True,
            'data_classification': True,
            'audit_logging': True
        }
        
        errors = await validator.validate_message_security(secure_message, requirements)
        assert len(errors) == 0
        
        # Message missing security requirements
        insecure_message = {
            'data': 'some data'
        }
        
        errors = await validator.validate_message_security(insecure_message, requirements)
        assert len(errors) > 0
        assert any('authentication' in error.lower() for error in errors)
    
    @pytest.mark.asyncio
    async def test_state_access_control_enforcement(self):
        """Test state access control enforcement"""
        config = {}
        state_manager = AdvancedStateManager(config)
        await state_manager.start()
        
        try:
            # Set secret state
            await state_manager.set_state(
                key='secret_key',
                value='secret_data',
                scope=StateScope.AGENT,
                owner_agent='owner_agent',
                access_level=AccessLevel.PRIVATE
            )
            
            # Owner should have access
            entry = state_manager.state_entries['secret_key']
            has_access = await state_manager._check_read_access(entry, 'owner_agent')
            assert has_access is True
            
            # Other agent should not have access
            has_access = await state_manager._check_read_access(entry, 'other_agent')
            assert has_access is False
            
            # Test write access
            has_write = await state_manager._check_write_access(entry, 'owner_agent')
            assert has_write is True
            
            has_write = await state_manager._check_write_access(entry, 'other_agent')
            assert has_write is False
            
        finally:
            await state_manager.stop()


# Integration tests
class TestCommunicationIntegration:
    """Integration tests for complete communication system"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_agent_collaboration(self):
        """Test complete agent collaboration workflow"""
        # Setup message bus and state manager
        message_bus = AdvancedMessageBus({})
        state_manager = AdvancedStateManager({})
        
        await message_bus.start()
        await state_manager.start()
        
        try:
            # Register agents
            agents = ['osint_agent', 'analysis_agent', 'reporting_agent']
            for agent_id in agents:
                await message_bus.register_agent(agent_id, {'name': f'{agent_id.title()}'})
            
            # Set shared workflow state
            await state_manager.set_state(
                key='workflow_context',
                value={'target': 'example.com', 'priority': 'high'},
                scope=StateScope.WORKFLOW,
                owner_agent='osint_agent',
                access_level=AccessLevel.PROTECTED,
                authorized_agents=set(agents)
            )
            
            # Delegate task from osint to analysis agent
            task_data = {
                'task_id': 'integration_test_001',
                'task_type': 'analysis',
                'description': 'Analyze collected intelligence',
                'shared_state_key': 'workflow_context'
            }
            
            delegation_msg_id = await message_bus.delegate_task(
                from_agent='osint_agent',
                to_agent='analysis_agent',
                task_data=task_data,
                priority=MessagePriority.HIGH
            )
            
            assert delegation_msg_id is not None
            
            # Analysis agent retrieves shared state
            shared_context = await state_manager.get_state('workflow_context', 'analysis_agent')
            assert shared_context == {'target': 'example.com', 'priority': 'high'}
            
            # Analysis agent updates shared state with results
            analysis_results = {'findings': 'threat_detected', 'confidence': 0.8}
            merge_result = await state_manager.merge_state(
                key='workflow_context',
                partial_value={'analysis_results': analysis_results},
                requesting_agent='analysis_agent'
            )
            
            assert merge_result is True
            
            # Verify merged state
            updated_context = await state_manager.get_state('workflow_context', 'reporting_agent')
            assert 'analysis_results' in updated_context
            assert updated_context['analysis_results'] == analysis_results
            
        finally:
            await message_bus.stop()
            await state_manager.stop()


if __name__ == "__main__":
    # Run tests with coverage
    pytest.main([
        __file__,
        "-v",
        "--cov=agents.communication",
        "--cov=core.state_manager",
        "--cov-report=html:htmlcov/communication_tests",
        "--cov-report=term-missing",
        "--cov-fail-under=80"
    ])
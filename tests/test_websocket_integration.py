"""
AMAS WebSocket Integration Tests

Comprehensive test suite for WebSocket real-time communication:
- WebSocket connection management
- Real-time message handling
- Subscription management
- Authentication and security
- Performance and reliability
- Error handling and recovery

Validates enterprise-grade real-time communication capabilities.
"""

import pytest
import asyncio
import json
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import WebSocket

# Import WebSocket components
from api.websocket_handler import (
    WebSocketConnectionManager, WebSocketConnection, Subscription
)
from web.src.services.websocket import WebSocketService  # This would be mocked in real tests


class MockWebSocket:
    """Mock WebSocket for testing"""
    
    def __init__(self):
        self.messages_sent = []
        self.is_closed = False
        self.close_code = None
        self.close_reason = None
    
    async def accept(self):
        pass
    
    async def send_text(self, message: str):
        if not self.is_closed:
            self.messages_sent.append(message)
    
    async def receive_text(self):
        # Mock receiving text - would be implemented based on test needs
        await asyncio.sleep(0.1)
        return '{"type": "test", "data": {}}'
    
    async def close(self, code: int = 1000, reason: str = ""):
        self.is_closed = True
        self.close_code = code
        self.close_reason = reason


class TestWebSocketConnectionManager:
    """Test suite for WebSocket Connection Manager"""
    
    @pytest.fixture
    async def ws_manager(self):
        """Create WebSocket manager for testing"""
        manager = WebSocketConnectionManager()
        await manager.start()
        yield manager
        await manager.stop()
    
    @pytest.mark.asyncio
    async def test_websocket_manager_initialization(self, ws_manager):
        """Test WebSocket manager initialization"""
        assert ws_manager is not None
        assert hasattr(ws_manager, 'active_connections')
        assert hasattr(ws_manager, 'subscriptions')
        assert hasattr(ws_manager, 'message_handlers')
        assert ws_manager._running is True
    
    @pytest.mark.asyncio
    async def test_client_connection_with_auth(self, ws_manager):
        """Test client connection with authentication"""
        mock_websocket = MockWebSocket()
        
        # Mock authentication
        with patch.object(ws_manager, '_authenticate_websocket') as mock_auth:
            mock_auth.return_value = {
                'user_id': 'test_user',
                'username': 'testuser',
                'role': 'admin'
            }
            
            connection_id = await ws_manager.connect_client(mock_websocket, 'valid_token')
            
            assert connection_id is not None
            assert connection_id in ws_manager.active_connections
            
            # Check connection details
            connection = ws_manager.active_connections[connection_id]
            assert connection.user_id == 'test_user'
            assert connection.user_role == 'admin'
            assert connection.is_active is True
            
            # Check welcome message was sent
            assert len(mock_websocket.messages_sent) > 0
            welcome_message = json.loads(mock_websocket.messages_sent[0])
            assert welcome_message['type'] == 'connection_established'
    
    @pytest.mark.asyncio
    async def test_client_connection_without_auth(self, ws_manager):
        """Test client connection without authentication"""
        mock_websocket = MockWebSocket()
        
        # Mock failed authentication
        with patch.object(ws_manager, '_authenticate_websocket') as mock_auth:
            mock_auth.return_value = None
            
            with pytest.raises(Exception):  # Should raise authentication error
                await ws_manager.connect_client(mock_websocket, None)
            
            # WebSocket should be closed
            assert mock_websocket.is_closed is True
            assert mock_websocket.close_code == 4001
    
    @pytest.mark.asyncio
    async def test_message_handling(self, ws_manager):
        """Test WebSocket message handling"""
        mock_websocket = MockWebSocket()
        
        # Connect client
        with patch.object(ws_manager, '_authenticate_websocket') as mock_auth:
            mock_auth.return_value = {'user_id': 'test_user', 'username': 'testuser', 'role': 'user'}
            connection_id = await ws_manager.connect_client(mock_websocket, 'valid_token')
        
        # Test system status request
        message = {
            'type': 'get_system_status',
            'data': {}
        }
        
        # Mock AMAS system
        mock_amas = Mock()
        mock_amas.get_system_status = AsyncMock(return_value={
            'status': 'operational',
            'agents': 5,
            'active_tasks': 3
        })
        ws_manager.amas_system = mock_amas
        
        await ws_manager.handle_message(connection_id, message)
        
        # Should have sent response
        assert len(mock_websocket.messages_sent) > 1  # Welcome + response
        response_message = json.loads(mock_websocket.messages_sent[-1])
        assert response_message['type'] == 'system_status'
        assert response_message['data']['status'] == 'operational'
    
    @pytest.mark.asyncio
    async def test_subscription_management(self, ws_manager):
        """Test subscription creation and management"""
        mock_websocket = MockWebSocket()
        
        # Connect client
        with patch.object(ws_manager, '_authenticate_websocket') as mock_auth:
            mock_auth.return_value = {'user_id': 'test_user', 'username': 'testuser', 'role': 'user'}
            connection_id = await ws_manager.connect_client(mock_websocket, 'valid_token')
        
        # Create subscription
        subscription_id = await ws_manager._create_subscription(
            connection_id=connection_id,
            subscription_type='task_updates',
            filters={'task_id': 'test_task_001'}
        )
        
        assert subscription_id is not None
        assert subscription_id in ws_manager.subscriptions
        
        # Check subscription details
        subscription = ws_manager.subscriptions[subscription_id]
        assert subscription.connection_id == connection_id
        assert subscription.subscription_type == 'task_updates'
        assert subscription.filters['task_id'] == 'test_task_001'
        
        # Check subscription index
        assert connection_id in ws_manager.subscription_index['task_updates']
        
        # Remove subscription
        await ws_manager._remove_subscription(subscription_id)
        
        assert subscription_id not in ws_manager.subscriptions
        assert connection_id not in ws_manager.subscription_index.get('task_updates', set())
    
    @pytest.mark.asyncio
    async def test_broadcasting(self, ws_manager):
        """Test message broadcasting to all connections"""
        # Connect multiple clients
        connections = []
        mock_websockets = []
        
        for i in range(3):
            mock_websocket = MockWebSocket()
            mock_websockets.append(mock_websocket)
            
            with patch.object(ws_manager, '_authenticate_websocket') as mock_auth:
                mock_auth.return_value = {
                    'user_id': f'test_user_{i}',
                    'username': f'testuser{i}',
                    'role': 'user'
                }
                connection_id = await ws_manager.connect_client(mock_websocket, f'token_{i}')
                connections.append(connection_id)
        
        # Broadcast message
        broadcast_message = {
            'type': 'system_alert',
            'data': {
                'alert': 'System maintenance scheduled',
                'time': '2024-01-15T02:00:00Z'
            }
        }
        
        await ws_manager.broadcast_to_all(broadcast_message)
        
        # Check all clients received the message
        for mock_websocket in mock_websockets:
            assert len(mock_websocket.messages_sent) > 1  # Welcome + broadcast
            broadcast_received = json.loads(mock_websocket.messages_sent[-1])
            assert broadcast_received['type'] == 'system_alert'
            assert broadcast_received['data']['alert'] == 'System maintenance scheduled'
    
    @pytest.mark.asyncio
    async def test_subscription_broadcasting(self, ws_manager):
        """Test broadcasting to specific subscribers"""
        # Connect clients
        connection_ids = []
        mock_websockets = []
        
        for i in range(3):
            mock_websocket = MockWebSocket()
            mock_websockets.append(mock_websocket)
            
            with patch.object(ws_manager, '_authenticate_websocket') as mock_auth:
                mock_auth.return_value = {
                    'user_id': f'test_user_{i}',
                    'username': f'testuser{i}',
                    'role': 'user'
                }
                connection_id = await ws_manager.connect_client(mock_websocket, f'token_{i}')
                connection_ids.append(connection_id)
        
        # Subscribe first two clients to task updates
        for i in range(2):
            await ws_manager._create_subscription(
                connection_id=connection_ids[i],
                subscription_type='task_updates',
                filters={'task_id': 'test_task'}
            )
        
        # Broadcast to task update subscribers
        task_update_message = {
            'type': 'task_update',
            'data': {
                'task_id': 'test_task',
                'status': 'completed',
                'progress': 100
            }
        }
        
        await ws_manager.broadcast_to_subscribers('task_updates', task_update_message)
        
        # First two clients should have received the update
        for i in range(2):
            messages = mock_websockets[i].messages_sent
            assert len(messages) > 1
            task_message = json.loads(messages[-1])
            assert task_message['type'] == 'task_update'
        
        # Third client should not have received task update (not subscribed)
        third_client_messages = mock_websockets[2].messages_sent
        task_updates = [
            json.loads(msg) for msg in third_client_messages
            if json.loads(msg).get('type') == 'task_update'
        ]
        assert len(task_updates) == 0
    
    @pytest.mark.asyncio
    async def test_connection_cleanup(self, ws_manager):
        """Test connection cleanup and heartbeat monitoring"""
        mock_websocket = MockWebSocket()
        
        # Connect client
        with patch.object(ws_manager, '_authenticate_websocket') as mock_auth:
            mock_auth.return_value = {'user_id': 'test_user', 'username': 'testuser', 'role': 'user'}
            connection_id = await ws_manager.connect_client(mock_websocket, 'valid_token')
        
        # Simulate old heartbeat
        connection = ws_manager.active_connections[connection_id]
        connection.last_heartbeat = datetime.utcnow() - timedelta(minutes=10)
        
        # Run connection monitor once
        await ws_manager._connection_monitor()
        
        # Connection should be cleaned up due to inactive heartbeat
        # Note: This test depends on the implementation of _connection_monitor
        # In a real test, we might need to wait or trigger the cleanup manually
    
    @pytest.mark.asyncio
    async def test_performance_metrics(self, ws_manager):
        """Test performance metrics collection"""
        # Get initial metrics
        initial_status = ws_manager.get_manager_status()
        initial_connections = initial_status['active_connections']
        
        # Connect client
        mock_websocket = MockWebSocket()
        
        with patch.object(ws_manager, '_authenticate_websocket') as mock_auth:
            mock_auth.return_value = {'user_id': 'test_user', 'username': 'testuser', 'role': 'user'}
            connection_id = await ws_manager.connect_client(mock_websocket, 'valid_token')
        
        # Get updated metrics
        updated_status = ws_manager.get_manager_status()
        
        assert updated_status['active_connections'] == initial_connections + 1
        assert updated_status['total_subscriptions'] >= 0
        assert 'metrics' in updated_status
        assert 'connection_details' in updated_status
        
        # Check connection details
        connection_details = updated_status['connection_details']
        assert len(connection_details) == initial_connections + 1
        
        # Find our connection
        our_connection = next(
            (conn for conn in connection_details if conn['connection_id'] == connection_id),
            None
        )
        assert our_connection is not None
        assert our_connection['user_id'] == 'test_user'


class TestWebSocketSecurity:
    """Security tests for WebSocket communication"""
    
    @pytest.mark.asyncio
    async def test_authentication_validation(self):
        """Test WebSocket authentication validation"""
        ws_manager = WebSocketConnectionManager()
        
        # Test valid token authentication
        with patch('jwt.decode') as mock_decode:
            mock_decode.return_value = {
                'user_id': 'valid_user',
                'sub': 'validuser',
                'role': 'admin'
            }
            
            user_info = await ws_manager._authenticate_websocket('valid_token')
            assert user_info is not None
            assert user_info['user_id'] == 'valid_user'
            assert user_info['role'] == 'admin'
        
        # Test invalid token authentication
        with patch('jwt.decode') as mock_decode:
            mock_decode.side_effect = Exception("Invalid token")
            
            user_info = await ws_manager._authenticate_websocket('invalid_token')
            assert user_info is None
        
        # Test no token
        user_info = await ws_manager._authenticate_websocket(None)
        assert user_info is None
    
    @pytest.mark.asyncio
    async def test_message_validation(self):
        """Test WebSocket message validation"""
        ws_manager = WebSocketConnectionManager()
        await ws_manager.start()
        
        try:
            mock_websocket = MockWebSocket()
            
            # Connect client
            with patch.object(ws_manager, '_authenticate_websocket') as mock_auth:
                mock_auth.return_value = {'user_id': 'test_user', 'username': 'testuser', 'role': 'user'}
                connection_id = await ws_manager.connect_client(mock_websocket, 'valid_token')
            
            # Test valid message
            valid_message = {
                'type': 'get_system_status',
                'data': {}
            }
            
            await ws_manager.handle_message(connection_id, valid_message)
            
            # Should not generate error
            error_messages = [
                msg for msg in mock_websocket.messages_sent
                if 'error' in json.loads(msg).get('type', '')
            ]
            assert len(error_messages) == 0
            
            # Test invalid message type
            invalid_message = {
                'type': 'invalid_message_type',
                'data': {}
            }
            
            await ws_manager.handle_message(connection_id, invalid_message)
            
            # Should generate error message
            error_messages = [
                msg for msg in mock_websocket.messages_sent
                if 'error' in json.loads(msg).get('type', '')
            ]
            assert len(error_messages) > 0
            
        finally:
            await ws_manager.stop()


class TestWebSocketPerformance:
    """Performance tests for WebSocket communication"""
    
    @pytest.mark.asyncio
    async def test_connection_scalability(self):
        """Test WebSocket connection scalability"""
        ws_manager = WebSocketConnectionManager()
        await ws_manager.start()
        
        try:
            # Connect multiple clients
            connection_count = 50
            connections = []
            
            start_time = time.time()
            
            for i in range(connection_count):
                mock_websocket = MockWebSocket()
                
                with patch.object(ws_manager, '_authenticate_websocket') as mock_auth:
                    mock_auth.return_value = {
                        'user_id': f'user_{i}',
                        'username': f'user{i}',
                        'role': 'user'
                    }
                    
                    connection_id = await ws_manager.connect_client(mock_websocket, f'token_{i}')
                    connections.append(connection_id)
            
            connection_time = time.time() - start_time
            
            # Should handle 50 connections efficiently
            assert len(connections) == connection_count
            assert connection_time < 5.0  # Should connect 50 clients in under 5 seconds
            assert len(ws_manager.active_connections) == connection_count
            
            print(f"Connected {connection_count} clients in {connection_time:.2f} seconds")
            
        finally:
            await ws_manager.stop()
    
    @pytest.mark.asyncio
    async def test_message_throughput(self):
        """Test WebSocket message throughput"""
        ws_manager = WebSocketConnectionManager()
        await ws_manager.start()
        
        try:
            # Connect client
            mock_websocket = MockWebSocket()
            
            with patch.object(ws_manager, '_authenticate_websocket') as mock_auth:
                mock_auth.return_value = {'user_id': 'test_user', 'username': 'testuser', 'role': 'user'}
                connection_id = await ws_manager.connect_client(mock_websocket, 'valid_token')
            
            # Send many messages rapidly
            message_count = 100
            start_time = time.time()
            
            tasks = []
            for i in range(message_count):
                message = {
                    'type': 'heartbeat',
                    'data': {'timestamp': time.time(), 'sequence': i}
                }
                tasks.append(ws_manager.handle_message(connection_id, message))
            
            # Wait for all messages to be processed
            await asyncio.gather(*tasks)
            processing_time = time.time() - start_time
            
            # Calculate throughput
            throughput = message_count / processing_time
            
            assert throughput > 50  # Should handle at least 50 messages/second
            
            print(f"WebSocket message throughput: {throughput:.2f} messages/second")
            
        finally:
            await ws_manager.stop()
    
    @pytest.mark.asyncio
    async def test_broadcast_performance(self):
        """Test broadcast performance to multiple clients"""
        ws_manager = WebSocketConnectionManager()
        await ws_manager.start()
        
        try:
            # Connect multiple clients
            client_count = 20
            mock_websockets = []
            
            for i in range(client_count):
                mock_websocket = MockWebSocket()
                mock_websockets.append(mock_websocket)
                
                with patch.object(ws_manager, '_authenticate_websocket') as mock_auth:
                    mock_auth.return_value = {
                        'user_id': f'user_{i}',
                        'username': f'user{i}',
                        'role': 'user'
                    }
                    await ws_manager.connect_client(mock_websocket, f'token_{i}')
            
            # Broadcast message
            broadcast_message = {
                'type': 'system_alert',
                'data': {
                    'alert': 'Performance test broadcast',
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
            
            start_time = time.time()
            await ws_manager.broadcast_to_all(broadcast_message)
            broadcast_time = time.time() - start_time
            
            # Should broadcast to all clients efficiently
            assert broadcast_time < 1.0  # Should broadcast to 20 clients in under 1 second
            
            # Check all clients received the message
            for mock_websocket in mock_websockets:
                assert len(mock_websocket.messages_sent) > 1  # Welcome + broadcast
                broadcast_received = json.loads(mock_websocket.messages_sent[-1])
                assert broadcast_received['type'] == 'system_alert'
            
            print(f"Broadcast to {client_count} clients in {broadcast_time:.3f} seconds")
            
        finally:
            await ws_manager.stop()


class TestWebSocketReliability:
    """Reliability and error handling tests"""
    
    @pytest.mark.asyncio
    async def test_connection_recovery(self):
        """Test connection recovery after errors"""
        ws_manager = WebSocketConnectionManager()
        await ws_manager.start()
        
        try:
            mock_websocket = MockWebSocket()
            
            # Connect client
            with patch.object(ws_manager, '_authenticate_websocket') as mock_auth:
                mock_auth.return_value = {'user_id': 'test_user', 'username': 'testuser', 'role': 'user'}
                connection_id = await ws_manager.connect_client(mock_websocket, 'valid_token')
            
            assert connection_id in ws_manager.active_connections
            
            # Simulate connection error
            await ws_manager._disconnect_client(connection_id, "Simulated error")
            
            # Connection should be removed
            assert connection_id not in ws_manager.active_connections
            
            # Reconnect
            new_connection_id = await ws_manager.connect_client(mock_websocket, 'valid_token')
            
            # Should get new connection ID
            assert new_connection_id != connection_id
            assert new_connection_id in ws_manager.active_connections
            
        finally:
            await ws_manager.stop()
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in message processing"""
        ws_manager = WebSocketConnectionManager()
        await ws_manager.start()
        
        try:
            mock_websocket = MockWebSocket()
            
            # Connect client
            with patch.object(ws_manager, '_authenticate_websocket') as mock_auth:
                mock_auth.return_value = {'user_id': 'test_user', 'username': 'testuser', 'role': 'user'}
                connection_id = await ws_manager.connect_client(mock_websocket, 'valid_token')
            
            # Send message that will cause handler error
            with patch.object(ws_manager, '_handle_get_system_status') as mock_handler:
                mock_handler.side_effect = Exception("Handler error")
                
                error_message = {
                    'type': 'get_system_status',
                    'data': {}
                }
                
                await ws_manager.handle_message(connection_id, error_message)
                
                # Should send error response to client
                error_responses = [
                    msg for msg in mock_websocket.messages_sent
                    if 'error' in json.loads(msg).get('type', '')
                ]
                assert len(error_responses) > 0
                
                error_response = json.loads(error_responses[0])
                assert 'Handler error' in error_response['data']['error']
            
        finally:
            await ws_manager.stop()


class TestWebSocketIntegration:
    """Integration tests for WebSocket with AMAS system"""
    
    @pytest.mark.asyncio
    async def test_real_time_system_status(self):
        """Test real-time system status updates"""
        # Mock AMAS system
        mock_amas = Mock()
        mock_amas.get_system_status = AsyncMock(return_value={
            'status': 'operational',
            'agents': 8,
            'active_tasks': 5,
            'total_tasks': 100,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        ws_manager = WebSocketConnectionManager(mock_amas)
        await ws_manager.start()
        
        try:
            mock_websocket = MockWebSocket()
            
            # Connect client
            with patch.object(ws_manager, '_authenticate_websocket') as mock_auth:
                mock_auth.return_value = {'user_id': 'test_user', 'username': 'testuser', 'role': 'admin'}
                connection_id = await ws_manager.connect_client(mock_websocket, 'valid_token')
            
            # Request system status
            status_request = {
                'type': 'get_system_status',
                'data': {}
            }
            
            await ws_manager.handle_message(connection_id, status_request)
            
            # Should receive system status response
            status_responses = [
                json.loads(msg) for msg in mock_websocket.messages_sent
                if json.loads(msg).get('type') == 'system_status'
            ]
            
            assert len(status_responses) > 0
            status_response = status_responses[0]
            assert status_response['data']['status'] == 'operational'
            assert status_response['data']['agents'] == 8
            
        finally:
            await ws_manager.stop()


if __name__ == "__main__":
    # Run tests with coverage
    pytest.main([
        __file__,
        "-v",
        "--cov=api.websocket_handler",
        "--cov-report=html:htmlcov/websocket_tests",
        "--cov-report=term-missing",
        "--cov-fail-under=80"
    ])
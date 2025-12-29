"""
Tests for Agent Communication Protocol
"""

import asyncio
import pytest
from typing import Any, Dict

from src.amas.agents.communication import (
    AgentMessage,
    MessageType,
    MessagePriority,
    get_event_bus,
    get_shared_context,
    get_communication_protocol,
    get_collaboration_manager,
    CollaborationPattern,
)


@pytest.mark.asyncio
async def test_message_creation():
    """Test message creation and serialization"""
    message = AgentMessage(
        sender="agent1",
        receiver="agent2",
        type=MessageType.REQUEST,
        priority=MessagePriority.HIGH,
        payload={"test": "data"},
    )
    
    assert message.sender == "agent1"
    assert message.receiver == "agent2"
    assert message.type == MessageType.REQUEST
    assert message.priority == MessagePriority.HIGH
    
    # Test serialization
    json_str = message.to_json()
    assert json_str is not None
    
    # Test deserialization
    message2 = AgentMessage.from_json(json_str)
    assert message2.sender == message.sender
    assert message2.receiver == message.receiver


@pytest.mark.asyncio
async def test_event_bus():
    """Test event bus publish/subscribe"""
    event_bus = get_event_bus()
    await event_bus.initialize()
    
    # Start processing
    await event_bus.start_processing()
    
    # Track received events
    received_events = []
    
    async def handler(event):
        received_events.append(event)
    
    # Subscribe to event
    event_bus.subscribe("test_event", handler)
    
    # Publish event
    await event_bus.publish(
        event_type="test_event",
        data={"message": "Hello World"},
        sender="test_agent",
    )
    
    # Wait for processing
    await asyncio.sleep(0.5)
    
    # Check event was received
    assert len(received_events) > 0
    assert received_events[0].event_type == "test_event"
    assert received_events[0].data["message"] == "Hello World"
    
    # Stop processing
    await event_bus.stop_processing()


@pytest.mark.asyncio
async def test_shared_context():
    """Test shared context"""
    context = get_shared_context("test_namespace")
    await context.initialize()
    
    # Set value
    success = await context.set("test_key", "test_value")
    assert success
    
    # Get value
    value = await context.get("test_key")
    assert value == "test_value"
    
    # Update value
    await context.update("test_key", "new_value", updated_by="test_agent")
    value = await context.get("test_key")
    assert value == "new_value"
    
    # Check version
    version = await context.get_version("test_key")
    assert version > 0
    
    # Clear context
    await context.clear()


@pytest.mark.asyncio
async def test_communication_protocol():
    """Test communication protocol"""
    protocol1 = get_communication_protocol("agent1")
    protocol2 = get_communication_protocol("agent2")
    
    await protocol1.initialize()
    await protocol2.initialize()
    
    # Create and send message
    message = AgentMessage(
        sender="agent1",
        receiver="agent2",
        type=MessageType.REQUEST,
        payload={"question": "What is 2+2?"},
    )
    
    success = await protocol1.send_message("agent2", message)
    assert success
    
    # Receive messages
    await asyncio.sleep(0.1)
    messages = await protocol2.receive_messages()
    
    assert len(messages) > 0
    assert messages[0].sender == "agent1"
    assert messages[0].payload["question"] == "What is 2+2?"


@pytest.mark.asyncio
async def test_request_response():
    """Test request-response pattern"""
    protocol1 = get_communication_protocol("agent1")
    protocol2 = get_communication_protocol("agent2")
    
    await protocol1.initialize()
    await protocol2.initialize()
    
    # Simulate agent2 responding to requests
    async def respond_to_requests():
        await asyncio.sleep(0.1)
        messages = await protocol2.receive_messages()
        for msg in messages:
            if msg.is_request():
                response_payload = {"answer": "4"}
                await protocol2.respond(msg, response_payload)
    
    # Start responder
    responder_task = asyncio.create_task(respond_to_requests())
    
    # Send request
    response = await protocol1.request(
        to_agent="agent2",
        payload={"question": "What is 2+2?"},
        timeout=2.0,
    )
    
    await responder_task
    
    assert response is not None
    assert response["answer"] == "4"


@pytest.mark.asyncio
async def test_broadcast():
    """Test broadcast messaging"""
    protocol1 = get_communication_protocol("agent1")
    protocol2 = get_communication_protocol("agent2")
    protocol3 = get_communication_protocol("agent3")
    
    await protocol1.initialize()
    await protocol2.initialize()
    await protocol3.initialize()
    
    # Broadcast message
    sent_count = await protocol1.broadcast(
        payload={"announcement": "System update"},
        recipients=["agent2", "agent3"],
    )
    
    assert sent_count == 2
    
    # Check recipients received
    await asyncio.sleep(0.1)
    messages2 = await protocol2.receive_messages()
    messages3 = await protocol3.receive_messages()
    
    assert len(messages2) > 0
    assert len(messages3) > 0


@pytest.mark.asyncio
async def test_collaboration_sequential():
    """Test sequential collaboration pattern"""
    # This is a simplified test - full test would use real agents
    collaboration_manager = get_collaboration_manager()
    
    # Mock agents
    class MockAgent:
        def __init__(self, agent_id, name):
            self.id = agent_id
            self.name = name
        
        async def execute(self, task_id, target, parameters):
            return {
                "success": True,
                "output": f"{self.name} processed: {parameters.get('input', 'none')}",
            }
    
    agents = [
        MockAgent("agent1", "Agent 1"),
        MockAgent("agent2", "Agent 2"),
        MockAgent("agent3", "Agent 3"),
    ]
    
    result = await collaboration_manager.execute_sequential(
        agents=agents,
        task_id="test_task",
        target="test_target",
        parameters={"input": "test"},
    )
    
    assert result["success"]
    assert result["pattern"] == "sequential"
    assert result["success_count"] == 3
    assert result["total_agents"] == 3


@pytest.mark.asyncio
async def test_collaboration_parallel():
    """Test parallel collaboration pattern"""
    collaboration_manager = get_collaboration_manager()
    
    # Mock agents
    class MockAgent:
        def __init__(self, agent_id, name):
            self.id = agent_id
            self.name = name
        
        async def execute(self, task_id, target, parameters):
            await asyncio.sleep(0.1)  # Simulate work
            return {
                "success": True,
                "output": f"{self.name} result",
            }
    
    agents = [
        MockAgent("agent1", "Agent 1"),
        MockAgent("agent2", "Agent 2"),
        MockAgent("agent3", "Agent 3"),
    ]
    
    result = await collaboration_manager.execute_parallel(
        agents=agents,
        task_id="test_task",
        target="test_target",
        parameters={"input": "test"},
    )
    
    assert result["success"]
    assert result["pattern"] == "parallel"
    assert result["success_count"] == 3
    assert len(result["all_outputs"]) == 3


if __name__ == "__main__":
    # Run tests
    asyncio.run(test_message_creation())
    asyncio.run(test_event_bus())
    asyncio.run(test_shared_context())
    asyncio.run(test_communication_protocol())
    asyncio.run(test_request_response())
    asyncio.run(test_broadcast())
    asyncio.run(test_collaboration_sequential())
    asyncio.run(test_collaboration_parallel())
    
    print("✅ All communication tests passed!")


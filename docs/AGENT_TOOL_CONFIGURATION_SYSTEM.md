# Agent Tool Configuration System

## Overview

Complete system for configuring and monitoring agent tools in the AMAS dashboard. Each agent can now have its tools configured with options for authentication, API keys, and execution settings, with real-time status monitoring.

## Features

### ✅ Backend API Endpoints

**File**: `src/api/routes/agent_tools.py`

1. **GET `/api/v1/agents/{agent_id}/tools`**
   - Get all tools available for an agent
   - Returns tool metadata, configuration, and requirements

2. **GET `/api/v1/agents/{agent_id}/tools/{tool_name}/status`**
   - Get status of a specific tool
   - Checks API key configuration, service availability

3. **GET `/api/v1/agents/{agent_id}/tools/status`**
   - Get status of all tools for an agent
   - Returns aggregated status information

4. **PUT `/api/v1/agents/{agent_id}/tools/{tool_name}/config`**
   - Update configuration for a specific tool
   - Supports enabling/disabling, API keys, custom config

5. **PUT `/api/v1/agents/{agent_id}/tools/config`**
   - Update configuration for all tools
   - Includes agent-level tool strategy settings

6. **POST `/api/v1/agents/{agent_id}/tools/{tool_name}/test`**
   - Test a tool to verify it's working
   - Returns test results and error messages

### ✅ Frontend Components

#### 1. AgentToolConfiguration Component

**File**: `frontend/src/components/Agents/AgentToolConfiguration.tsx`

**Features**:
- **Two-tab interface**:
  - **Tools Tab**: Configure individual tools
  - **Settings Tab**: Configure agent-level tool strategy

- **Tool Management**:
  - Enable/disable tools per agent
  - View tool status (available, needs_config, unavailable, error)
  - Configure API keys for tools that require them
  - Test individual tools
  - View tool metadata (category, cost tier, execution time)

- **Tool Status Indicators**:
  - ✅ Available (green)
  - ⚠️ Needs Config (yellow)
  - ❌ Unavailable/Error (red)
  - API Key status (configured/not configured)

- **Agent-Level Settings**:
  - Tool strategy selection (comprehensive, efficient, reliable, cost_optimized)
  - Max tools per execution
  - AI synthesis toggle

- **Real-time Updates**:
  - Auto-refreshes tool status
  - WebSocket integration for live updates

#### 2. ToolStatusIndicator Component

**File**: `frontend/src/components/Agents/ToolStatusIndicator.tsx`

**Features**:
- Compact status indicator for individual tools
- Real-time status monitoring (refreshes every 30 seconds)
- Tooltip with detailed status information
- Visual status icons (check, warning, error)

#### 3. AgentList Integration

**File**: `frontend/src/components/Agents/AgentList.tsx`

**Changes**:
- Added "Configure Tools" button to each agent card
- Opens AgentToolConfiguration dialog
- Integrated ToolStatusIndicator for tool status display

### ✅ API Service Methods

**File**: `frontend/src/services/api.ts`

**New Methods**:
- `getAgentTools(agentId)` - Get all tools for an agent
- `getToolStatus(agentId, toolName)` - Get status of a tool
- `getAllToolsStatus(agentId)` - Get status of all tools
- `updateToolConfig(agentId, toolName, config)` - Update tool config
- `updateAgentToolsConfig(agentId, config)` - Update all tools config
- `testTool(agentId, toolName)` - Test a tool

## Tool Status System

### Status Types

1. **available** ✅
   - Tool is ready to use
   - All requirements met (API keys, services)

2. **needs_config** ⚠️
   - Tool requires configuration
   - Missing API key or service URL

3. **unavailable** ❌
   - Tool service is not available
   - External service is down

4. **error** ❌
   - Tool has an error
   - Check error message for details

### Status Checks

The system automatically checks:
- **API Key Configuration**: Verifies if required API keys are set
- **Service Availability**: Checks if external services are running (AgenticSeek, Robin, Prometheus, etc.)
- **Tool Execution**: Tests tool execution with minimal parameters

## Configuration Options

### Per-Tool Configuration

Each tool can be configured with:
- **Enabled/Disabled**: Toggle tool usage for this agent
- **API Key**: Set API key for tools that require authentication
- **Custom Config**: Tool-specific configuration parameters

### Agent-Level Configuration

- **Tool Strategy**: How tools are selected and executed
  - `comprehensive`: Use all available tools
  - `efficient`: Fastest tools first
  - `reliable`: Most reliable tools
  - `cost_optimized`: Lowest cost tools

- **Max Tools**: Maximum number of tools to use per execution (1-10)

- **AI Synthesis**: Whether to use AI to combine results from multiple tools

## Usage

### Configuring Agent Tools

1. Navigate to **Agents** page
2. Click **"Configure Tools"** button on an agent card
3. In the **Tools** tab:
   - Enable/disable tools using the toggle switch
   - Configure API keys for tools that require them
   - Test tools to verify they're working
   - View tool status and requirements

4. In the **Settings** tab:
   - Select tool strategy
   - Set max tools per execution
   - Toggle AI synthesis

5. Click **"Save Configuration"** to apply changes

### Monitoring Tool Status

- Tool status is displayed with color-coded indicators:
  - ✅ Green: Available
  - ⚠️ Yellow: Needs configuration
  - ❌ Red: Unavailable or error

- Status automatically refreshes every 30 seconds
- Click "Test" button to manually test a tool

## Integration Points

### Backend Integration

- **Tool Registry**: Uses `get_tool_registry()` to access all registered tools
- **Tool Categories**: Uses `TOOL_CATEGORY_MAP` for tool metadata
- **Agent Storage**: Stores tool config in agent's `tool_config` attribute
- **WebSocket**: Broadcasts configuration updates in real-time

### Frontend Integration

- **API Service**: All tool operations go through `apiService`
- **WebSocket**: Receives real-time tool status updates
- **Material-UI**: Uses MUI components for consistent UI
- **TypeScript**: Fully typed for type safety

## Security Considerations

- **API Keys**: Stored securely (in production, use encrypted vault)
- **Authentication**: All endpoints require authentication
- **Authorization**: Checks user permissions before allowing configuration changes
- **Audit Logging**: All configuration changes are logged

## Future Enhancements

1. **Tool Dependencies**: Visualize and configure tool dependencies
2. **Tool Performance Metrics**: Track tool success rates and execution times
3. **Tool Recommendations**: AI-powered tool selection recommendations
4. **Bulk Configuration**: Configure multiple agents at once
5. **Tool Templates**: Save and reuse tool configurations
6. **Advanced Testing**: More comprehensive tool testing with custom parameters

## Files Created/Modified

### New Files
- `src/api/routes/agent_tools.py` - Backend API endpoints
- `frontend/src/components/Agents/AgentToolConfiguration.tsx` - Main configuration component
- `frontend/src/components/Agents/ToolStatusIndicator.tsx` - Status indicator component

### Modified Files
- `src/amas/api/main.py` - Added agent_tools router
- `frontend/src/services/api.ts` - Added tool configuration methods
- `frontend/src/components/Agents/AgentList.tsx` - Integrated tool configuration

## Testing

### Manual Testing

1. **Test Tool Configuration**:
   - Open agent configuration dialog
   - Enable/disable tools
   - Configure API keys
   - Save and verify changes persist

2. **Test Tool Status**:
   - Check status indicators
   - Verify status updates automatically
   - Test tools with "Test" button

3. **Test Tool Strategy**:
   - Change tool strategy
   - Set max tools
   - Toggle AI synthesis
   - Verify settings are saved

### API Testing

```bash
# Get agent tools
curl -X GET http://localhost:8000/api/v1/agents/{agent_id}/tools

# Get tool status
curl -X GET http://localhost:8000/api/v1/agents/{agent_id}/tools/{tool_name}/status

# Update tool config
curl -X PUT http://localhost:8000/api/v1/agents/{agent_id}/tools/{tool_name}/config \
  -H "Content-Type: application/json" \
  -d '{"enabled": true, "config": {}}'

# Test tool
curl -X POST http://localhost:8000/api/v1/agents/{agent_id}/tools/{tool_name}/test
```

## Status

✅ **COMPLETE** - All features implemented and integrated

- ✅ Backend API endpoints
- ✅ Frontend configuration UI
- ✅ Tool status monitoring
- ✅ API key management
- ✅ Tool testing
- ✅ Real-time updates
- ✅ Integration with AgentList

---

**Last Updated**: January 2025  
**Status**: ✅ Production Ready


// frontend/src/services/testing.ts - Testing API Service
import { AxiosError, AxiosInstance } from 'axios';
import { apiService } from './api';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

export interface TestResult {
  test_name: string;
  success: boolean;
  message: string;
  duration: number;
  data?: Record<string, any>;
  error?: string;
}

export interface AgentTestResponse {
  agent_id: string;
  agent_name: string;
  available: boolean;
  test_result?: TestResult;
}

export interface ProviderTestResponse {
  provider: string;
  available: boolean;
  test_result?: TestResult;
  latency?: number;
}

export interface DatabaseTestResponse {
  connected: boolean;
  test_result?: TestResult;
  query_time?: number;
}

export interface CacheTestResponse {
  connected: boolean;
  test_result?: TestResult;
  operations?: Record<string, any>;
}

export interface WebSocketTestResponse {
  connected: boolean;
  test_result?: TestResult;
}

export interface IntegrationTestResponse {
  platform: string;
  connected: boolean;
  test_result?: TestResult;
}

export interface MLTestResponse {
  available: boolean;
  test_result?: TestResult;
  prediction?: Record<string, any>;
}

export interface GraphDBTestResponse {
  connected: boolean;
  test_result?: TestResult;
  node_count?: number;
}

export interface SystemTestResponse {
  component: string;
  status: string;
  test_result?: TestResult;
}

// ============================================================================
// TESTING API SERVICE
// ============================================================================

class TestingService {
  private client: AxiosInstance;

  constructor() {
    // Access the internal axios client from apiService
    this.client = (apiService as any).client as AxiosInstance;
  }

  // ============================================================================
  // AGENTS TESTING
  // ============================================================================

  async listAgents(): Promise<AgentTestResponse[]> {
    try {
      console.log('[Testing] Listing agents for testing');
      const response = await this.client.get<AgentTestResponse[]>('/testing/agents');
      console.log('[Testing] Agents listed:', response.data);
      return response.data;
    } catch (error) {
      console.error('[Testing] Failed to list agents:', error);
      const axiosError = error as AxiosError;
      throw new Error((axiosError.response?.data as any)?.detail || 'Failed to list agents');
    }
  }

  async testAgent(agentId: string, target: string): Promise<AgentTestResponse> {
    try {
      console.log(`[Testing] Testing agent: ${agentId} with target: ${target}`);
      const response = await this.client.post<AgentTestResponse>(
        `/testing/agents/${agentId}/test`,
        null,
        { params: { target } }
      );
      console.log(`[Testing] Agent test completed:`, response.data);
      return response.data;
    } catch (error) {
      console.error(`[Testing] Agent test failed:`, error);
      const axiosError = error as AxiosError;
      throw new Error((axiosError.response?.data as any)?.detail || `Failed to test agent ${agentId}`);
    }
  }

  // ============================================================================
  // AI PROVIDERS TESTING
  // ============================================================================

  async listProviders(): Promise<ProviderTestResponse[]> {
    try {
      console.log('[Testing] Listing AI providers for testing');
      const response = await this.client.get<ProviderTestResponse[]>('/testing/providers');
      console.log('[Testing] Providers listed:', response.data);
      return response.data;
    } catch (error) {
      console.error('[Testing] Failed to list providers:', error);
      const axiosError = error as AxiosError;
      throw new Error((axiosError.response?.data as any)?.detail || 'Failed to list providers');
    }
  }

  async testProvider(provider: string, prompt: string = 'Hello, this is a test'): Promise<ProviderTestResponse> {
    try {
      console.log(`[Testing] Testing provider: ${provider}`);
      const response = await this.client.post<ProviderTestResponse>(
        `/testing/providers/${provider}/test`,
        null,
        { params: { prompt } }
      );
      console.log(`[Testing] Provider test completed:`, response.data);
      return response.data;
    } catch (error) {
      console.error(`[Testing] Provider test failed:`, error);
      const axiosError = error as AxiosError;
      throw new Error((axiosError.response?.data as any)?.detail || `Failed to test provider ${provider}`);
    }
  }

  // ============================================================================
  // DATABASE TESTING
  // ============================================================================

  async testDatabaseStatus(): Promise<DatabaseTestResponse> {
    try {
      console.log('[Testing] Testing database status');
      const response = await this.client.get<DatabaseTestResponse>('/testing/database/status');
      console.log('[Testing] Database status test completed:', response.data);
      return response.data;
    } catch (error) {
      console.error('[Testing] Database status test failed:', error);
      const axiosError = error as AxiosError;
      throw new Error((axiosError.response?.data as any)?.detail || 'Failed to test database status');
    }
  }

  async testDatabaseQuery(query: string = 'SELECT COUNT(*) FROM tasks'): Promise<TestResult> {
    try {
      console.log('[Testing] Testing database query:', query);
      const response = await this.client.post<TestResult>(
        '/testing/database/query',
        null,
        { params: { query } }
      );
      console.log('[Testing] Database query test completed:', response.data);
      return response.data;
    } catch (error) {
      console.error('[Testing] Database query test failed:', error);
      const axiosError = error as AxiosError;
      throw new Error((axiosError.response?.data as any)?.detail || 'Failed to test database query');
    }
  }

  // ============================================================================
  // CACHE TESTING
  // ============================================================================

  async testCacheStatus(): Promise<CacheTestResponse> {
    try {
      console.log('[Testing] Testing cache status');
      const response = await this.client.get<CacheTestResponse>('/testing/cache/status');
      console.log('[Testing] Cache status test completed:', response.data);
      return response.data;
    } catch (error) {
      console.error('[Testing] Cache status test failed:', error);
      const axiosError = error as AxiosError;
      throw new Error((axiosError.response?.data as any)?.detail || 'Failed to test cache status');
    }
  }

  // ============================================================================
  // WEBSOCKET TESTING
  // ============================================================================

  async testWebSocketStatus(): Promise<WebSocketTestResponse> {
    try {
      console.log('[Testing] Testing WebSocket status');
      const response = await this.client.get<WebSocketTestResponse>('/testing/websocket/status');
      console.log('[Testing] WebSocket status test completed:', response.data);
      return response.data;
    } catch (error) {
      console.error('[Testing] WebSocket status test failed:', error);
      const axiosError = error as AxiosError;
      throw new Error((axiosError.response?.data as any)?.detail || 'Failed to test WebSocket status');
    }
  }

  // ============================================================================
  // INTEGRATIONS TESTING
  // ============================================================================

  async testIntegration(platform: string): Promise<IntegrationTestResponse> {
    try {
      console.log(`[Testing] Testing integration: ${platform}`);
      const response = await this.client.post<IntegrationTestResponse>(
        `/testing/integrations/${platform}/test`
      );
      console.log(`[Testing] Integration test completed:`, response.data);
      return response.data;
    } catch (error) {
      console.error(`[Testing] Integration test failed:`, error);
      const axiosError = error as AxiosError;
      throw new Error((axiosError.response?.data as any)?.detail || `Failed to test integration ${platform}`);
    }
  }

  // ============================================================================
  // ML PREDICTIONS TESTING
  // ============================================================================

  async testMLPrediction(
    taskType: string = 'security_scan',
    target: string = 'example.com'
  ): Promise<MLTestResponse> {
    try {
      console.log(`[Testing] Testing ML prediction: taskType=${taskType}, target=${target}`);
      const response = await this.client.post<MLTestResponse>(
        '/testing/ml/predict',
        null,
        { params: { task_type: taskType, target } }
      );
      console.log(`[Testing] ML prediction test completed:`, response.data);
      return response.data;
    } catch (error) {
      console.error(`[Testing] ML prediction test failed:`, error);
      const axiosError = error as AxiosError;
      throw new Error((axiosError.response?.data as any)?.detail || 'Failed to test ML prediction');
    }
  }

  // ============================================================================
  // GRAPH DATABASE (NEO4J) TESTING
  // ============================================================================

  async testGraphDBStatus(): Promise<GraphDBTestResponse> {
    try {
      console.log('[Testing] Testing Neo4j graph database status');
      const response = await this.client.get<GraphDBTestResponse>('/testing/graphdb/status');
      console.log('[Testing] Neo4j status test completed:', response.data);
      return response.data;
    } catch (error) {
      console.error('[Testing] Neo4j status test failed:', error);
      const axiosError = error as AxiosError;
      throw new Error((axiosError.response?.data as any)?.detail || 'Failed to test Neo4j status');
    }
  }

  // ============================================================================
  // SYSTEM TESTING
  // ============================================================================

  async testSystemHealth(): Promise<SystemTestResponse> {
    try {
      console.log('[Testing] Testing system health');
      const response = await this.client.get<SystemTestResponse>('/testing/system/health');
      console.log('[Testing] System health test completed:', response.data);
      return response.data;
    } catch (error) {
      console.error('[Testing] System health test failed:', error);
      const axiosError = error as AxiosError;
      throw new Error((axiosError.response?.data as any)?.detail || 'Failed to test system health');
    }
  }
}

// Export singleton instance
export const testingService = new TestingService();


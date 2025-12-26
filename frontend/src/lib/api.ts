/**
 * AMAS Frontend API Client
 * 
 * SECURITY FEATURES (per AI audit):
 * - Separate mock/real clients (no production leak)
 * - Environment-based switching
 * - Tree-shakeable for production builds
 */

// Types
export interface MetricsData {
  activeAgents: number;
  tasksProcessed: number;
  avgResponseTime: number;
  successRate: number;
  timestamp: string;
}

export interface SystemStatus {
  status: 'healthy' | 'degraded' | 'down';
  uptime: number;
  version: string;
}

// ============================================================================
// MOCK DATA (Development Only)
// ============================================================================
const MOCK_METRICS: MetricsData = {
  activeAgents: 12,
  tasksProcessed: 1543,
  avgResponseTime: 145,
  successRate: 98.7,
  timestamp: new Date().toISOString()
};

const MOCK_STATUS: SystemStatus = {
  status: 'healthy',
  uptime: 99.94,
  version: '1.0.0-alpha'
};

// ============================================================================
// MOCK API CLIENT (Never bundled in production)
// ============================================================================
class MockApiClient {
  async getMetrics(): Promise<MetricsData> {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 300));
    return { ...MOCK_METRICS, timestamp: new Date().toISOString() };
  }

  async getSystemStatus(): Promise<SystemStatus> {
    await new Promise(resolve => setTimeout(resolve, 200));
    return MOCK_STATUS;
  }
}

// ============================================================================
// REAL API CLIENT (Production)
// ============================================================================
class RealApiClient {
  private baseUrl: string;

  constructor() {
    // SECURITY: Use environment variable (never hardcode)
    this.baseUrl = import.meta.env.VITE_API_URL || '/api';
  }

  async getMetrics(): Promise<MetricsData> {
    const response = await fetch(`${this.baseUrl}/metrics`);
    if (!response.ok) throw new Error('Failed to fetch metrics');
    return response.json();
  }

  async getSystemStatus(): Promise<SystemStatus> {
    const response = await fetch(`${this.baseUrl}/status`);
    if (!response.ok) throw new Error('Failed to fetch status');
    return response.json();
  }
}

// ============================================================================
// API CLIENT FACTORY (Security-Audited Switch)
// ============================================================================

/**
 * SECURITY: Strict environment check
 * - Uses import.meta.env.PROD (Vite's built-in flag)
 * - Tree-shaking removes MockApiClient in production builds
 * - No risk of mock data in production
 */
function createApiClient() {
  // PROD is a compile-time constant in Vite - tree-shaken
  if (import.meta.env.PROD) {
    console.info('[API] Using REAL API client');
    return new RealApiClient();
  } else {
    console.warn('[API] Using MOCK API client (development only)');
    return new MockApiClient();
  }
}

// Export singleton instance
export const api = createApiClient();

// Export types
export type ApiClient = MockApiClient | RealApiClient;

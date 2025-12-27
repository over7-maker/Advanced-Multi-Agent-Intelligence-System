/// <reference types="../../vite-env" />
/**
 * Landing Page API Client
 * Handles all API calls for landing page components
 */

import axios, { AxiosInstance } from 'axios';

// ============================================================================
// TYPES
// ============================================================================

export interface SystemMetrics {
  cpu_usage_percent: number;
  memory_usage_percent: number;
  active_tasks: number;
  completed_tasks: number;
  failed_tasks: number;
  active_agents: number;
  queue_depth: number;
  uptime_hours: number;
  avg_task_duration: number;
  success_rate: number;
}

export interface AgentStatus {
  agent_id: string;
  name: string;
  status: 'active' | 'inactive' | 'error';
  executions_today: number;
  success_rate: number;
  avg_response_time: number;
  specialization: string;
}

export interface DemoData {
  sample_task_id: string;
  sample_agents: string[];
  estimated_duration: number;
  estimated_cost: number;
  quality_prediction: number;
}

export interface FeedbackRequest {
  email: string;
  name: string;
  message: string;
  sentiment?: 'positive' | 'neutral' | 'negative';
  page_context?: string;
}

export interface FeedbackResponse {
  feedback_id: string;
  message: string;
  timestamp: string;
}

export interface HealthResponse {
  status: string;
  timestamp: string;
  service: string;
}

// ============================================================================
// LANDING PAGE API CLIENT
// ============================================================================

class LandingAPIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_URL || '/api/v1',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * Get system metrics for dashboard
   */
  async getSystemMetrics(): Promise<SystemMetrics> {
    try {
      const response = await this.client.get<SystemMetrics>('/landing/metrics');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch system metrics:', error);
      throw error;
    }
  }

  /**
   * Get agent status information
   */
  async getAgentsStatus(): Promise<AgentStatus[]> {
    try {
      const response = await this.client.get<AgentStatus[]>('/landing/agents-status');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch agents status:', error);
      throw error;
    }
  }

  /**
   * Get demo data for interactive examples
   */
  async getDemoData(): Promise<DemoData> {
    try {
      const response = await this.client.get<DemoData>('/landing/demo-data');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch demo data:', error);
      throw error;
    }
  }

  /**
   * Submit user feedback
   */
  async submitFeedback(feedback: FeedbackRequest): Promise<FeedbackResponse> {
    try {
      const response = await this.client.post<FeedbackResponse>(
        '/landing/feedback',
        feedback
      );
      return response.data;
    } catch (error) {
      console.error('Failed to submit feedback:', error);
      throw error;
    }
  }

  /**
   * Check API health
   */
  async getHealth(): Promise<HealthResponse> {
    try {
      const response = await this.client.get<HealthResponse>('/landing/health');
      return response.data;
    } catch (error) {
      console.error('Failed to check health:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const landingAPI = new LandingAPIClient();

export default LandingAPIClient;

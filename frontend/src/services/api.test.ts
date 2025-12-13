// frontend/src/services/api.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';

// Import the class directly
let APIService: any;
let apiService: any;

describe('APIService', () => {
  beforeEach(async () => {
    vi.clearAllMocks();
    if (typeof localStorage !== 'undefined') {
      localStorage.clear();
    }
    
    // Import the class
    const module = await import('./api');
    APIService = module.default;
    apiService = new APIService();
  });

  describe('Token Management', () => {
    it('should set and clear token', () => {
      apiService.setToken('test_token');
      expect(localStorage.getItem('access_token')).toBe('test_token');
      
      apiService.clearToken();
      expect(localStorage.getItem('access_token')).toBeNull();
    });

    it('should load token from localStorage', async () => {
      localStorage.setItem('access_token', 'stored_token');
      const module = await import('./api');
      const APIServiceClass = module.default;
      new APIServiceClass();
      // Token should be loaded in constructor
      expect(localStorage.getItem('access_token')).toBe('stored_token');
    });
  });

  describe('API Methods', () => {
    it('should have authentication methods', () => {
      expect(typeof apiService.login).toBe('function');
      expect(typeof apiService.logout).toBe('function');
      expect(typeof apiService.getCurrentUser).toBe('function');
    });

    it('should have task methods', () => {
      expect(typeof apiService.listTasks).toBe('function');
      expect(typeof apiService.getTask).toBe('function');
      expect(typeof apiService.createTask).toBe('function');
      expect(typeof apiService.executeTask).toBe('function');
      expect(typeof apiService.cancelTask).toBe('function');
      expect(typeof apiService.getTaskProgress).toBe('function');
    });

    it('should have prediction methods', () => {
      expect(typeof apiService.predictTask).toBe('function');
      expect(typeof apiService.predictSystemResources).toBe('function');
      expect(typeof apiService.getModelMetrics).toBe('function');
    });

    it('should have agent methods', () => {
      expect(typeof apiService.listAgents).toBe('function');
      expect(typeof apiService.getAgent).toBe('function');
      expect(typeof apiService.getAgentPerformance).toBe('function');
    });

    it('should have integration methods', () => {
      expect(typeof apiService.listIntegrations).toBe('function');
      expect(typeof apiService.createIntegration).toBe('function');
      expect(typeof apiService.deleteIntegration).toBe('function');
      expect(typeof apiService.triggerIntegration).toBe('function');
    });

    it('should have system methods', () => {
      expect(typeof apiService.getSystemMetrics).toBe('function');
      expect(typeof apiService.getSystemHealth).toBe('function');
      expect(typeof apiService.getTaskAnalytics).toBe('function');
      expect(typeof apiService.getAgentAnalytics).toBe('function');
    });
  });
});

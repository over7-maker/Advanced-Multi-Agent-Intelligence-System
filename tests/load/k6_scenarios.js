// k6 load testing scenarios for AMAS
// Install: brew install k6 (or see https://k6.io/docs/get-started/installation/)
// Run: k6 run tests/load/k6_scenarios.js

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Custom metrics
const orchestratorLatency = new Trend('orchestrator_latency');
const agentSuccessRate = new Rate('agent_success_rate');
const tokenUsage = new Counter('token_usage');

export const options = {
  stages: [
    { duration: '2m', target: 10 },   // Ramp up to 10 users
    { duration: '5m', target: 10 },     // Stay at 10 users
    { duration: '2m', target: 50 },     // Ramp up to 50 users
    { duration: '5m', target: 50 },     // Stay at 50 users
    { duration: '2m', target: 100 },    // Ramp up to 100 users
    { duration: '5m', target: 100 },    // Stay at 100 users
    { duration: '2m', target: 0 },      // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000', 'p(99)<5000'], // 95% < 2s, 99% < 5s
    http_req_failed: ['rate<0.01'],                  // < 1% errors
    orchestrator_latency: ['p(95)<1500'],            // Orchestrator p95 < 1.5s
    agent_success_rate: ['rate>0.95'],               // > 95% success
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const AUTH_TOKEN = __ENV.AUTH_TOKEN || 'test_token';

export default function () {
  // Scenario 1: Orchestrator end-to-end flow
  let response = http.post(
    `${BASE_URL}/api/v1/orchestrator/execute`,
    JSON.stringify({
      workflow: 'code_review',
      input: {
        code: 'def hello(): print("world")',
        language: 'python',
      },
    }),
    {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${AUTH_TOKEN}`,
      },
      tags: { name: 'orchestrator_execute' },
    }
  );

  const success = check(response, {
    'orchestrator status is 200': (r) => r.status === 200,
    'orchestrator response time < 2s': (r) => r.timings.duration < 2000,
  });

  orchestratorLatency.add(response.timings.duration);
  agentSuccessRate.add(success);

  sleep(1);

  // Scenario 2: AI Router request
  response = http.post(
    `${BASE_URL}/api/v1/ai/generate`,
    JSON.stringify({
      prompt: 'Analyze this code for security issues',
      system_prompt: 'You are a security expert',
      max_tokens: 500,
    }),
    {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${AUTH_TOKEN}`,
      },
      tags: { name: 'ai_router' },
    }
  );

  check(response, {
    'ai router status is 200': (r) => r.status === 200,
    'ai router response time < 3s': (r) => r.timings.duration < 3000,
  });

  if (response.json('token_usage')) {
    tokenUsage.add(response.json('token_usage'));
  }

  sleep(2);

  // Scenario 3: Health check
  response = http.get(`${BASE_URL}/health`, {
    tags: { name: 'health_check' },
  });

  check(response, {
    'health check status is 200': (r) => r.status === 200,
  });

  sleep(0.5);
}

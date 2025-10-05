"""Performance load tests for AMAS using Locust"""

from locust import HttpUser, between, task


class AMASUser(HttpUser):
    """Simulated AMAS user for load testing"""

    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    @task(3)
    def check_health(self):
        """Check health endpoint (most common)"""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")

    @task(2)
    def get_api_info(self):
        """Get API information"""
        self.client.get("/")

    @task(1)
    def get_agents_status(self):
        """Get agents status (if endpoint exists)"""
        with self.client.get("/api/v1/agents/status", catch_response=True) as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"Unexpected status: {response.status_code}")

    def on_start(self):
        """Called when a user starts"""
        # Could add authentication here if needed
        pass

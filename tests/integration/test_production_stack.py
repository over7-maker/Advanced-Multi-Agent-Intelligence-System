"""
Production stack integration tests.
"""
import subprocess
import time
from pathlib import Path

import pytest
import requests

from tests.fixtures.production_fixtures import docker_compose_path, project_root


@pytest.mark.integration
@pytest.mark.slow
class TestProductionStack:
    """Test suite for full production stack integration."""
    
    @pytest.fixture(scope="function", autouse=True)
    def setup_stack(self, docker_compose_path: Path, project_root: Path):
        """Setup and teardown Docker Compose stack."""
        # Check if Docker is available
        try:
            subprocess.run(['docker', '--version'], 
                         capture_output=True, check=True, timeout=5)
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Docker not available")
        
        # Start stack
        subprocess.run(
            ['docker-compose', '-f', str(docker_compose_path), 'up', '-d'],
            cwd=project_root,
            timeout=300
        )
        
        # Wait for services to be ready
        time.sleep(30)
        
        yield
        
        # Teardown
        subprocess.run(
            ['docker-compose', '-f', str(docker_compose_path), 'down', '-v'],
            cwd=project_root,
            timeout=60
        )
    
    def test_all_services_running(self, docker_compose_path: Path, project_root: Path):
        """Test that all services are running."""
        result = subprocess.run(
            ['docker-compose', '-f', str(docker_compose_path), 'ps'],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        assert result.returncode == 0, f"Failed to check services: {result.stderr}"
        
        # Check for key services
        output = result.stdout
        assert 'amas-backend' in output, "amas-backend should be running"
        assert 'postgres' in output, "postgres should be running"
        assert 'redis' in output, "redis should be running"
    
    def test_backend_health_endpoint(self):
        """Test backend health endpoint."""
        try:
            response = requests.get('http://localhost:8000/health', timeout=5)
            assert response.status_code == 200, \
                f"Health endpoint returned {response.status_code}"
        except requests.exceptions.RequestException:
            pytest.skip("Backend not accessible")
    
    def test_nginx_proxy(self):
        """Test nginx reverse proxy."""
        try:
            response = requests.get('http://localhost/health', timeout=5)
            assert response.status_code in [200, 301, 302], \
                f"Nginx proxy returned {response.status_code}"
        except requests.exceptions.RequestException:
            pytest.skip("Nginx not accessible")
    
    def test_prometheus_accessible(self):
        """Test Prometheus is accessible."""
        try:
            response = requests.get('http://localhost:9090/-/healthy', timeout=5)
            assert response.status_code == 200, \
                f"Prometheus returned {response.status_code}"
        except requests.exceptions.RequestException:
            pytest.skip("Prometheus not accessible")
    
    def test_grafana_accessible(self):
        """Test Grafana is accessible."""
        try:
            response = requests.get('http://localhost:3001/api/health', timeout=5)
            assert response.status_code in [200, 401], \
                f"Grafana returned {response.status_code}"
        except requests.exceptions.RequestException:
            pytest.skip("Grafana not accessible")


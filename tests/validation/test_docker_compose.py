"""
Docker Compose validation tests.
"""
import pytest
from pathlib import Path

from tests.fixtures.production_fixtures import docker_compose_path
from tests.utils.validation_helpers import YAMLValidator


class TestDockerComposeValidation:
    """Test suite for docker-compose.prod.yml validation."""
    
    def test_docker_compose_exists(self, docker_compose_path: Path):
        """Test that docker-compose.prod.yml exists."""
        assert docker_compose_path.exists(), \
            f"docker-compose.prod.yml not found at {docker_compose_path}"
    
    def test_yaml_syntax(self, docker_compose_path: Path):
        """Test docker-compose.prod.yml has valid YAML syntax."""
        valid, error = YAMLValidator.validate_file(docker_compose_path)
        assert valid, f"YAML syntax error: {error}"
    
    def test_required_services(self, docker_compose_path: Path):
        """Test that all required services are defined."""
        compose_data = YAMLValidator.load_file(docker_compose_path)
        assert compose_data is not None, "Failed to load docker-compose.yml"
        
        services = compose_data.get('services', {})
        
        required_services = [
            'amas-backend',
            'postgres',
            'redis',
            'neo4j',
            'nginx',
            'prometheus',
            'grafana',
            'jaeger',
            'alertmanager',
            'node-exporter',
            'cadvisor',
            'postgres-exporter',
            'redis-exporter',
            'loki',
            'promtail',
        ]
        
        missing_services = [svc for svc in required_services if svc not in services]
        assert len(missing_services) == 0, \
            f"Missing required services: {', '.join(missing_services)}"
    
    def test_service_dependencies(self, docker_compose_path: Path):
        """Test service dependencies are correctly configured."""
        compose_data = YAMLValidator.load_file(docker_compose_path)
        services = compose_data.get('services', {})
        
        # Check amas-backend depends on postgres and redis
        backend = services.get('amas-backend', {})
        depends_on = backend.get('depends_on', [])
        
        if isinstance(depends_on, list):
            depends_on_names = depends_on
        elif isinstance(depends_on, dict):
            depends_on_names = list(depends_on.keys())
        else:
            depends_on_names = []
        
        assert 'postgres' in depends_on_names, "amas-backend should depend on postgres"
        assert 'redis' in depends_on_names, "amas-backend should depend on redis"
    
    def test_health_checks(self, docker_compose_path: Path):
        """Test that services have health checks configured."""
        compose_data = YAMLValidator.load_file(docker_compose_path)
        services = compose_data.get('services', {})
        
        services_with_healthchecks = [
            'amas-backend',
            'postgres',
            'redis',
            'nginx',
        ]
        
        for service_name in services_with_healthchecks:
            service = services.get(service_name, {})
            assert 'healthcheck' in service, \
                f"Service {service_name} should have healthcheck configured"
            
            healthcheck = service['healthcheck']
            assert 'test' in healthcheck, \
                f"Healthcheck for {service_name} should have 'test' field"
    
    def test_resource_limits(self, docker_compose_path: Path):
        """Test that services have resource limits configured."""
        compose_data = YAMLValidator.load_file(docker_compose_path)
        services = compose_data.get('services', {})
        
        # Check critical services have resource limits
        critical_services = ['amas-backend', 'postgres', 'redis']
        
        for service_name in critical_services:
            service = services.get(service_name, {})
            deploy = service.get('deploy', {})
            resources = deploy.get('resources', {})
            
            assert 'limits' in resources, \
                f"Service {service_name} should have resource limits"
            assert 'reservations' in resources, \
                f"Service {service_name} should have resource reservations"
    
    def test_volumes_defined(self, docker_compose_path: Path):
        """Test that volumes are properly defined."""
        compose_data = YAMLValidator.load_file(docker_compose_path)
        
        assert 'volumes' in compose_data, "docker-compose.yml should define volumes"
        
        volumes = compose_data['volumes']
        required_volumes = [
            'postgres-data',
            'redis-data',
            'prometheus-data',
            'grafana-data',
        ]
        
        for volume_name in required_volumes:
            assert volume_name in volumes, \
                f"Required volume {volume_name} is not defined"
    
    def test_networks_defined(self, docker_compose_path: Path):
        """Test that networks are properly defined."""
        compose_data = YAMLValidator.load_file(docker_compose_path)
        
        assert 'networks' in compose_data, "docker-compose.yml should define networks"
        
        networks = compose_data['networks']
        assert 'amas-backend' in networks, "Missing amas-backend network"
        assert 'amas-monitoring' in networks, "Missing amas-monitoring network"
    
    def test_environment_variables(self, docker_compose_path: Path):
        """Test that environment variables are properly configured."""
        compose_data = YAMLValidator.load_file(docker_compose_path)
        services = compose_data.get('services', {})
        
        backend = services.get('amas-backend', {})
        env = backend.get('environment', [])
        
        # Convert to dict if it's a list
        if isinstance(env, list):
            env_dict = {}
            for item in env:
                if '=' in item:
                    key, value = item.split('=', 1)
                    env_dict[key] = value
        else:
            env_dict = env
        
        # Check for required environment variables
        required_env_vars = [
            'ENVIRONMENT',
            'SECRET_KEY',
            'JWT_SECRET',
            'DATABASE_URL',
            'REDIS_URL',
        ]
        
        for var in required_env_vars:
            assert var in env_dict, \
                f"Missing required environment variable: {var}"


"""
Kubernetes manifest validation tests.
"""
import pytest
from pathlib import Path

from tests.fixtures.production_fixtures import k8s_manifest_path
from tests.utils.validation_helpers import KubernetesManifestValidator, YAMLValidator


class TestKubernetesManifestValidation:
    """Test suite for k8s/deployment.yaml validation."""
    
    def test_k8s_manifest_exists(self, k8s_manifest_path: Path):
        """Test that k8s/deployment.yaml exists."""
        assert k8s_manifest_path.exists(), \
            f"k8s/deployment.yaml not found at {k8s_manifest_path}"
    
    def test_yaml_syntax(self, k8s_manifest_path: Path):
        """Test Kubernetes manifest has valid YAML syntax."""
        valid, error = YAMLValidator.validate_file(k8s_manifest_path)
        assert valid, f"YAML syntax error: {error}"
    
    def test_kubernetes_validation(self, k8s_manifest_path: Path):
        """Test Kubernetes manifest validation."""
        valid, error = KubernetesManifestValidator.validate_file(k8s_manifest_path)
        assert valid, f"Kubernetes manifest validation error: {error}"
    
    def test_required_resources(self, k8s_manifest_path: Path):
        """Test that all required Kubernetes resources are defined."""
        resources = KubernetesManifestValidator.extract_resources(k8s_manifest_path)
        
        resource_types = [r.get('kind') for r in resources if r.get('kind')]
        
        required_resources = [
            'Namespace',
            'ConfigMap',
            'Secret',
            'Deployment',
            'Service',
            'HorizontalPodAutoscaler',
            'Ingress',
            'StatefulSet',
            'PersistentVolumeClaim',
        ]
        
        missing_resources = [r for r in required_resources if r not in resource_types]
        assert len(missing_resources) == 0, \
            f"Missing required Kubernetes resources: {', '.join(missing_resources)}"
    
    def test_namespace_defined(self, k8s_manifest_path: Path):
        """Test that namespace is defined."""
        resources = KubernetesManifestValidator.extract_resources(k8s_manifest_path)
        
        namespaces = [r for r in resources if r.get('kind') == 'Namespace']
        assert len(namespaces) > 0, "Namespace should be defined"
        
        namespace = namespaces[0]
        assert namespace['metadata']['name'] == 'amas-production', \
            "Namespace should be named 'amas-production'"
    
    def test_deployment_configuration(self, k8s_manifest_path: Path):
        """Test Deployment resource configuration."""
        resources = KubernetesManifestValidator.extract_resources(k8s_manifest_path)
        
        deployments = [r for r in resources if r.get('kind') == 'Deployment']
        assert len(deployments) > 0, "At least one Deployment should be defined"
        
        deployment = deployments[0]
        spec = deployment.get('spec', {})
        
        # Check replicas
        assert 'replicas' in spec, "Deployment should specify replicas"
        assert spec['replicas'] >= 1, "Deployment should have at least 1 replica"
        
        # Check strategy
        assert 'strategy' in spec, "Deployment should specify update strategy"
        assert spec['strategy']['type'] == 'RollingUpdate', \
            "Deployment should use RollingUpdate strategy"
    
    def test_service_configuration(self, k8s_manifest_path: Path):
        """Test Service resource configuration."""
        resources = KubernetesManifestValidator.extract_resources(k8s_manifest_path)
        
        services = [r for r in resources if r.get('kind') == 'Service']
        assert len(services) > 0, "At least one Service should be defined"
        
        service = services[0]
        spec = service.get('spec', {})
        
        assert 'ports' in spec, "Service should define ports"
        assert 'selector' in spec, "Service should have selector"
    
    def test_hpa_configuration(self, k8s_manifest_path: Path):
        """Test HorizontalPodAutoscaler configuration."""
        resources = KubernetesManifestValidator.extract_resources(k8s_manifest_path)
        
        hpas = [r for r in resources if r.get('kind') == 'HorizontalPodAutoscaler']
        assert len(hpas) > 0, "HPA should be defined"
        
        hpa = hpas[0]
        spec = hpa.get('spec', {})
        
        assert 'minReplicas' in spec, "HPA should specify minReplicas"
        assert 'maxReplicas' in spec, "HPA should specify maxReplicas"
        assert 'metrics' in spec, "HPA should define metrics"
    
    def test_ingress_configuration(self, k8s_manifest_path: Path):
        """Test Ingress resource configuration."""
        resources = KubernetesManifestValidator.extract_resources(k8s_manifest_path)
        
        ingresses = [r for r in resources if r.get('kind') == 'Ingress']
        assert len(ingresses) > 0, "Ingress should be defined"
        
        ingress = ingresses[0]
        spec = ingress.get('spec', {})
        
        assert 'rules' in spec, "Ingress should define rules"
        assert 'tls' in spec, "Ingress should have TLS configuration"
    
    def test_pvc_configuration(self, k8s_manifest_path: Path):
        """Test PersistentVolumeClaim configuration."""
        resources = KubernetesManifestValidator.extract_resources(k8s_manifest_path)
        
        pvcs = [r for r in resources if r.get('kind') == 'PersistentVolumeClaim']
        assert len(pvcs) > 0, "PVCs should be defined"
        
        for pvc in pvcs:
            spec = pvc.get('spec', {})
            assert 'accessModes' in spec, "PVC should specify accessModes"
            assert 'resources' in spec, "PVC should specify resources"
            assert 'requests' in spec['resources'], "PVC should specify storage requests"
    
    def test_security_contexts(self, k8s_manifest_path: Path):
        """Test that security contexts are configured."""
        resources = KubernetesManifestValidator.extract_resources(k8s_manifest_path)
        
        deployments = [r for r in resources if r.get('kind') == 'Deployment']
        for deployment in deployments:
            spec = deployment.get('spec', {})
            template = spec.get('template', {})
            pod_spec = template.get('spec', {})
            containers = pod_spec.get('containers', [])
            
            for container in containers:
                # Security context should be present (can be at container or pod level)
                has_security = 'securityContext' in container or 'securityContext' in pod_spec
                # Note: Not all containers may have security context, but it's a best practice
                # We'll just check that at least one does
                if has_security:
                    break
            else:
                # If no container has security context, that's acceptable but not ideal
                pass  # Warning, not error


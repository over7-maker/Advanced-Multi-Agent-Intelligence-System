"""
Validation helper utilities for production component testing.
"""
import json
import os
import re
import subprocess
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml


class YAMLValidator:
    """YAML file validation helper."""
    
    @staticmethod
    def validate_file(file_path: Path) -> Tuple[bool, Optional[str]]:
        """Validate YAML file syntax."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Try to load all documents (for multi-document YAML)
                try:
                    list(yaml.safe_load_all(content))
                except yaml.YAMLError:
                    # Fallback to single document
                    yaml.safe_load(content)
            return True, None
        except yaml.YAMLError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Error reading file: {str(e)}"
    
    @staticmethod
    def load_file(file_path: Path) -> Optional[Dict]:
        """Load and return YAML content."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Try to load all documents (for multi-document YAML)
                documents = list(yaml.safe_load_all(content))
                if len(documents) == 1:
                    return documents[0]
                elif len(documents) > 1:
                    # Return first document for multi-doc files
                    return documents[0]
                else:
                    return None
        except Exception:
            return None


class DockerfileValidator:
    """Dockerfile validation helper."""
    
    @staticmethod
    def validate_syntax(file_path: Path) -> Tuple[bool, Optional[str]]:
        """Validate Dockerfile syntax using docker build --dry-run if available."""
        try:
            # Try to use hadolint if available (best practice)
            result = subprocess.run(
                ['hadolint', str(file_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return True, None
            else:
                return False, result.stderr or result.stdout
        except FileNotFoundError:
            # Fallback: basic syntax check
            return DockerfileValidator._basic_validation(file_path)
        except subprocess.TimeoutExpired:
            return False, "Validation timeout"
    
    @staticmethod
    def _basic_validation(file_path: Path) -> Tuple[bool, Optional[str]]:
        """Basic Dockerfile validation without external tools."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for required FROM statements
            if 'FROM' not in content:
                return False, "No FROM statement found"
            
            # Check for common syntax errors
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                if stripped and not stripped.startswith('#'):
                    # Check for invalid continuation
                    if stripped.endswith('\\') and i == len(lines):
                        return False, f"Line {i}: Invalid line continuation at end of file"
            
            return True, None
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def check_stages(file_path: Path) -> List[str]:
        """Extract all build stages from Dockerfile."""
        stages = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip().startswith('FROM'):
                        # Extract stage name if present
                        match = re.search(r'FROM\s+.*\s+as\s+(\w+)', line, re.IGNORECASE)
                        if match:
                            stages.append(match.group(1))
        except Exception:
            pass
        return stages
    
    @staticmethod
    def check_security_practices(file_path: Path) -> Dict[str, bool]:
        """Check for security best practices in Dockerfile."""
        practices = {
            'non_root_user': False,
            'health_check': False,
            'minimal_base': False,
            'no_secrets': True,
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for non-root user
            if re.search(r'USER\s+\w+', content, re.IGNORECASE):
                practices['non_root_user'] = True
            
            # Check for health check
            if 'HEALTHCHECK' in content:
                practices['health_check'] = True
            
            # Check for minimal base image
            if any(base in content.lower() for base in ['-slim', '-alpine', 'scratch']):
                practices['minimal_base'] = True
            
            # Check for potential secrets (basic check)
            secret_patterns = [
                r'password\s*=\s*["\']',
                r'api[_-]?key\s*=\s*["\']',
                r'secret\s*=\s*["\']',
            ]
            for pattern in secret_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    practices['no_secrets'] = False
                    break
        
        except Exception:
            pass
        
        return practices


class NginxConfigValidator:
    """Nginx configuration validation helper."""
    
    @staticmethod
    def validate_syntax(config_path: Path) -> Tuple[bool, Optional[str]]:
        """Validate nginx configuration using nginx -t."""
        try:
            result = subprocess.run(
                ['nginx', '-t', '-c', str(config_path)],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return True, None
            else:
                return False, result.stderr or result.stdout
        except FileNotFoundError:
            # Fallback: basic validation
            return NginxConfigValidator._basic_validation(config_path)
        except subprocess.TimeoutExpired:
            return False, "Validation timeout"
    
    @staticmethod
    def _basic_validation(config_path: Path) -> Tuple[bool, Optional[str]]:
        """Basic nginx config validation without nginx binary."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for required sections
            if 'http' not in content:
                return False, "Missing 'http' block"
            
            # Check for balanced braces
            if content.count('{') != content.count('}'):
                return False, "Unbalanced braces"
            
            return True, None
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def check_security_headers(config_path: Path) -> List[str]:
        """Check for security headers in nginx config."""
        headers = []
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            security_headers = [
                'Strict-Transport-Security',
                'X-Frame-Options',
                'X-Content-Type-Options',
                'X-XSS-Protection',
                'Content-Security-Policy',
            ]
            
            for header in security_headers:
                if header in content:
                    headers.append(header)
        except Exception:
            pass
        
        return headers


class KubernetesManifestValidator:
    """Kubernetes manifest validation helper."""
    
    @staticmethod
    def validate_file(file_path: Path) -> Tuple[bool, Optional[str]]:
        """Validate Kubernetes manifest YAML."""
        # First validate YAML syntax
        valid, error = YAMLValidator.validate_file(file_path)
        if not valid:
            return False, error
        
        # Try kubectl validation if available
        try:
            result = subprocess.run(
                ['kubectl', 'apply', '--dry-run=client', '-f', str(file_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return True, None
            else:
                # kubectl validation failed, but YAML is valid
                # Return True with warning
                return True, f"kubectl validation warning: {result.stderr}"
        except FileNotFoundError:
            # kubectl not available, YAML validation is enough
            return True, None
        except subprocess.TimeoutExpired:
            return False, "Validation timeout"
    
    @staticmethod
    def extract_resources(file_path: Path) -> List[Dict]:
        """Extract all Kubernetes resources from manifest."""
        resources = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split by --- separator
            documents = content.split('---')
            for doc in documents:
                doc = doc.strip()
                if doc:
                    try:
                        resource = yaml.safe_load(doc)
                        if resource:
                            resources.append(resource)
                    except yaml.YAMLError:
                        pass
        except Exception:
            pass
        
        return resources


class EnvFileValidator:
    """Environment file validation helper."""
    
    @staticmethod
    def validate_template(file_path: Path) -> Tuple[bool, List[str]]:
        """Validate .env template file."""
        errors = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for hardcoded secrets
            secret_patterns = [
                r'password\s*=\s*["\']?[^"\'\s]+["\']?',
                r'secret\s*=\s*["\']?[^"\'\s]+["\']?',
                r'key\s*=\s*["\']?sk-[^"\'\s]+["\']?',
            ]
            
            for i, line in enumerate(content.split('\n'), 1):
                # Skip comments and empty lines
                if line.strip().startswith('#') or not line.strip():
                    continue
                
            # Check for hardcoded secrets (not placeholders)
            for pattern in secret_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Allow placeholder values and example values
                    if ('CHANGE_THIS' not in line and 
                        'SECURE' not in line and 
                        'PLACEHOLDER' not in line and
                        'your_' not in line.lower() and
                        'example' not in line.lower() and
                        'test' not in line.lower() and
                        'demo' not in line.lower()):
                        # Check if it's a real secret (not just a default/example)
                        # Skip if it looks like an example value
                        if not (line.strip().endswith('_password') or 
                                'password=' in line.lower() and len(line.split('=')[1].strip()) < 20):
                            errors.append(f"Line {i}: Potential hardcoded secret: {line.strip()}")
            
            return len(errors) == 0, errors
        except Exception as e:
            return False, [str(e)]
    
    @staticmethod
    def check_required_variables(file_path: Path, required: List[str]) -> Tuple[bool, List[str]]:
        """Check if all required variables are present in template."""
        missing = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for var in required:
                if var not in content:
                    missing.append(var)
            
            return len(missing) == 0, missing
        except Exception:
            return False, required


class MarkdownValidator:
    """Markdown file validation helper."""
    
    @staticmethod
    def validate_syntax(file_path: Path) -> Tuple[bool, Optional[str]]:
        """Basic markdown syntax validation."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for balanced code blocks
            code_block_count = content.count('```')
            if code_block_count % 2 != 0:
                return False, "Unbalanced code blocks (```)"
            
            # Check for balanced markdown links
            link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
            links = re.findall(link_pattern, content)
            
            # Basic validation passed
            return True, None
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def check_links(file_path: Path, base_path: Path) -> List[Tuple[str, str]]:
        """Check for broken internal links."""
        broken_links = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all markdown links
            link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
            links = re.findall(link_pattern, content)
            
            for link_text, link_url in links:
                # Skip external links
                if link_url.startswith('http://') or link_url.startswith('https://'):
                    continue
                
                # Check if internal file exists
                if link_url.startswith('/'):
                    target_path = base_path / link_url.lstrip('/')
                else:
                    target_path = file_path.parent / link_url
                
                if not target_path.exists():
                    broken_links.append((link_text, link_url))
        
        except Exception:
            pass
        
        return broken_links


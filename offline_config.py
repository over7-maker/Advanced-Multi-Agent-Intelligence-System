#!/usr/bin/env python3
"""
AMAS Intelligence System - Offline-First Configuration
Complete local isolation with optional internet access
"""

import os
import logging
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

class OfflineConfig:
    """Offline-first configuration for AMAS Intelligence System"""
    
    def __init__(self):
        self.offline_mode = True
        self.internet_access = False
        self.local_services = {}
        self.isolation_settings = {}
        
    def get_offline_config(self) -> Dict[str, Any]:
        """Get complete offline configuration"""
        return {
            # Core System Settings
            'system_mode': 'offline',
            'isolation_level': 'complete',
            'internet_access': False,
            'local_only': True,
            
            # Local Service Configuration
            'local_services': {
                'llm_service': {
                    'type': 'ollama_local',
                    'host': 'localhost',
                    'port': 11434,
                    'models': ['llama3.1:8b', 'llama3.1:70b', 'codellama:34b'],
                    'offline_mode': True
                },
                'vector_service': {
                    'type': 'faiss_local',
                    'host': 'localhost',
                    'port': 8001,
                    'offline_mode': True,
                    'local_storage': './data/vectors'
                },
                'knowledge_graph': {
                    'type': 'neo4j_local',
                    'host': 'localhost',
                    'port': 7474,
                    'bolt_port': 7687,
                    'offline_mode': True,
                    'local_storage': './data/neo4j'
                },
                'database_service': {
                    'type': 'postgresql_local',
                    'host': 'localhost',
                    'port': 5432,
                    'database': 'amas_offline',
                    'offline_mode': True,
                    'local_storage': './data/postgres'
                },
                'cache_service': {
                    'type': 'redis_local',
                    'host': 'localhost',
                    'port': 6379,
                    'offline_mode': True,
                    'local_storage': './data/redis'
                }
            },
            
            # Network Isolation Settings
            'network_isolation': {
                'block_external_connections': True,
                'allowed_domains': [],  # Empty = no external access
                'proxy_mode': False,
                'firewall_enabled': True,
                'dns_resolution': 'local_only'
            },
            
            # Security Settings
            'security': {
                'encryption_key': Fernet.generate_key(),
                'jwt_secret': 'amas_offline_jwt_secret_2024_secure',
                'audit_logging': True,
                'local_authentication': True,
                'no_external_auth': True
            },
            
            # Agent Configuration
            'agents': {
                'offline_capable': True,
                'local_processing': True,
                'no_external_apis': True,
                'local_data_sources': True,
                'offline_workflows': True
            },
            
            # Data Storage
            'data_storage': {
                'local_only': True,
                'encrypted_storage': True,
                'backup_location': './data/backups',
                'no_cloud_sync': True,
                'offline_datasets': True
            },
            
            # Workflow Settings
            'workflows': {
                'offline_execution': True,
                'local_automation': True,
                'no_external_triggers': True,
                'air_gapped': True
            }
        }
    
    def get_hybrid_config(self, internet_access: bool = False) -> Dict[str, Any]:
        """Get hybrid configuration with optional internet access"""
        base_config = self.get_offline_config()
        
        if internet_access:
            base_config.update({
                'system_mode': 'hybrid',
                'internet_access': True,
                'network_isolation': {
                    'block_external_connections': False,
                    'allowed_domains': [
                        'api.openai.com',
                        'api.anthropic.com',
                        'api.cohere.ai',
                        'api.huggingface.co'
                    ],
                    'proxy_mode': True,
                    'firewall_enabled': True,
                    'dns_resolution': 'selective'
                },
                'agents': {
                    'offline_capable': True,
                    'local_processing': True,
                    'external_apis': 'on_demand',
                    'hybrid_workflows': True
                }
            })
        
        return base_config
    
    def create_offline_environment(self) -> Dict[str, Any]:
        """Create complete offline environment setup"""
        return {
            'environment': {
                'PYTHONPATH': '/workspace',
                'AMAS_MODE': 'offline',
                'AMAS_OFFLINE_MODE': 'true',
                'AMAS_LOCAL_ONLY': 'true',
                'AMAS_NO_INTERNET': 'true',
                'AMAS_ISOLATION_LEVEL': 'complete'
            },
            'docker_compose': {
                'version': '3.8',
                'services': {
                    'amas-core': {
                        'build': '.',
                        'container_name': 'amas-offline',
                        'ports': ['8000:8000'],
                        'environment': [
                            'AMAS_MODE=offline',
                            'AMAS_OFFLINE_MODE=true',
                            'AMAS_LOCAL_ONLY=true',
                            'AMAS_NO_INTERNET=true'
                        ],
                        'volumes': [
                            './data:/app/data',
                            './logs:/app/logs',
                            './models:/app/models'
                        ],
                        'networks': ['amas-offline-network'],
                        'restart': 'unless-stopped'
                    },
                    'ollama': {
                        'image': 'ollama/ollama:latest',
                        'container_name': 'amas-ollama',
                        'ports': ['11434:11434'],
                        'volumes': [
                            'ollama_data:/root/.ollama'
                        ],
                        'networks': ['amas-offline-network'],
                        'restart': 'unless-stopped'
                    },
                    'postgres': {
                        'image': 'postgres:15-alpine',
                        'container_name': 'amas-postgres',
                        'ports': ['5432:5432'],
                        'environment': [
                            'POSTGRES_DB=amas_offline',
                            'POSTGRES_USER=amas',
                            'POSTGRES_PASSWORD=amas_offline_secure'
                        ],
                        'volumes': [
                            'postgres_data:/var/lib/postgresql/data'
                        ],
                        'networks': ['amas-offline-network'],
                        'restart': 'unless-stopped'
                    },
                    'redis': {
                        'image': 'redis:7.2-alpine',
                        'container_name': 'amas-redis',
                        'ports': ['6379:6379'],
                        'volumes': [
                            'redis_data:/data'
                        ],
                        'networks': ['amas-offline-network'],
                        'restart': 'unless-stopped'
                    },
                    'neo4j': {
                        'image': 'neo4j:5.15.0',
                        'container_name': 'amas-neo4j',
                        'ports': ['7474:7474', '7687:7687'],
                        'environment': [
                            'NEO4J_AUTH=neo4j/amas_offline_secure',
                            'NEO4J_PLUGINS=["apoc"]'
                        ],
                        'volumes': [
                            'neo4j_data:/data',
                            'neo4j_logs:/logs'
                        ],
                        'networks': ['amas-offline-network'],
                        'restart': 'unless-stopped'
                    }
                },
                'volumes': {
                    'ollama_data': {},
                    'postgres_data': {},
                    'redis_data': {},
                    'neo4j_data': {},
                    'neo4j_logs': {}
                },
                'networks': {
                    'amas-offline-network': {
                        'driver': 'bridge',
                        'internal': True  # No external network access
                    }
                }
            }
        }

def create_offline_setup():
    """Create complete offline setup"""
    config = OfflineConfig()
    
    # Create offline configuration
    offline_config = config.get_offline_config()
    
    # Create hybrid configuration (optional internet)
    hybrid_config = config.get_hybrid_config(internet_access=True)
    
    # Create environment setup
    environment_setup = config.create_offline_environment()
    
    return {
        'offline_config': offline_config,
        'hybrid_config': hybrid_config,
        'environment_setup': environment_setup
    }

if __name__ == "__main__":
    setup = create_offline_setup()
    print("🔒 AMAS Offline-First Configuration Created")
    print("=" * 50)
    print(f"✅ Offline Mode: {setup['offline_config']['system_mode']}")
    print(f"✅ Internet Access: {setup['offline_config']['internet_access']}")
    print(f"✅ Local Services: {len(setup['offline_config']['local_services'])}")
    print(f"✅ Network Isolation: {setup['offline_config']['network_isolation']['block_external_connections']}")
    print("=" * 50)
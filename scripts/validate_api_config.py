#!/usr/bin/env python3
"""
API Configuration Validator and Setup Assistant
Helps validate and configure API keys for all AI providers
"""

import os
import sys
import json
from typing import Dict, Optional, Tuple
from pathlib import Path
import requests
from openai import OpenAI
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class APIConfigValidator:
    """Validates and tests API configurations for all AI providers"""
    
    def __init__(self):
        self.api_providers = {
            'deepseek': {
                'env_key': 'DEEPSEEK_API_KEY',
                'base_url': 'https://api.deepseek.com/v1',
                'test_model': 'deepseek-chat',
                'test_endpoint': 'chat/completions'
            },
            'openai': {
                'env_key': 'OPENAI_API_KEY',
                'base_url': 'https://api.openai.com/v1',
                'test_model': 'gpt-3.5-turbo',
                'test_endpoint': 'chat/completions'
            },
            'claude': {
                'env_key': 'CLAUDE_API_KEY',
                'base_url': 'https://api.anthropic.com/v1',
                'test_model': 'claude-3-opus-20240229',
                'test_endpoint': 'messages',
                'requires_anthropic_sdk': True
            },
            'glm': {
                'env_key': 'GLM_API_KEY',
                'base_url': 'https://open.bigmodel.cn/api/paas/v4',
                'test_model': 'glm-4',
                'test_endpoint': 'chat/completions'
            },
            'grok': {
                'env_key': 'GROK_API_KEY',
                'base_url': 'https://api.x.ai/v1',
                'test_model': 'grok-beta',
                'test_endpoint': 'chat/completions'
            },
            'qwen': {
                'env_key': 'QWEN_API_KEY',
                'base_url': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
                'test_model': 'qwen-turbo',
                'test_endpoint': 'chat/completions'
            },
            'openrouter': {
                'env_key': 'OPENROUTER_API_KEY',
                'base_url': 'https://openrouter.ai/api/v1',
                'test_model': 'openai/gpt-3.5-turbo',
                'test_endpoint': 'chat/completions'
            }
        }
        
        self.results = {}
        self.valid_keys = {}
        
    def load_env_file(self, env_path: str = '.env') -> Dict[str, str]:
        """Load environment variables from .env file"""
        env_vars = {}
        
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip().strip('"\'')
        
        return env_vars
    
    def test_api_key(self, provider: str, api_key: str) -> Tuple[bool, str]:
        """Test if an API key is valid by making a minimal request"""
        config = self.api_providers.get(provider)
        if not config:
            return False, f"Unknown provider: {provider}"
        
        try:
            if provider == 'claude' and config.get('requires_anthropic_sdk'):
                # Special handling for Claude/Anthropic
                import anthropic
                client = anthropic.Anthropic(api_key=api_key)
                response = client.messages.create(
                    model=config['test_model'],
                    max_tokens=10,
                    messages=[{"role": "user", "content": "Hi"}]
                )
                return True, "Valid API key"
            else:
                # OpenAI-compatible APIs
                client = OpenAI(
                    api_key=api_key,
                    base_url=config['base_url']
                )
                
                response = client.chat.completions.create(
                    model=config['test_model'],
                    messages=[{"role": "user", "content": "Hi"}],
                    max_tokens=10
                )
                return True, "Valid API key"
                
        except Exception as e:
            error_msg = str(e)
            if 'authentication' in error_msg.lower() or '401' in error_msg:
                return False, "Invalid API key"
            elif 'rate limit' in error_msg.lower() or '429' in error_msg:
                return True, "Valid API key (rate limited)"
            elif '404' in error_msg:
                return False, "Invalid endpoint or model"
            else:
                return False, f"Error: {error_msg}"
    
    def validate_all_keys(self) -> Dict[str, Dict]:
        """Validate all configured API keys"""
        logger.info("Starting API key validation...")
        
        # Load from environment and .env file
        env_vars = os.environ.copy()
        file_vars = self.load_env_file()
        env_vars.update(file_vars)
        
        for provider, config in self.api_providers.items():
            env_key = config['env_key']
            api_key = env_vars.get(env_key)
            
            if not api_key:
                self.results[provider] = {
                    'status': 'missing',
                    'message': f'No API key found for {env_key}',
                    'valid': False
                }
            else:
                logger.info(f"Testing {provider} API key...")
                valid, message = self.test_api_key(provider, api_key)
                
                self.results[provider] = {
                    'status': 'valid' if valid else 'invalid',
                    'message': message,
                    'valid': valid,
                    'key_prefix': api_key[:8] + '...' if len(api_key) > 8 else 'SHORT_KEY'
                }
                
                if valid:
                    self.valid_keys[provider] = api_key
        
        return self.results
    
    def generate_config_template(self) -> str:
        """Generate a configuration template for missing/invalid keys"""
        template_lines = ["# AMAS API Configuration Template", 
                         "# Copy this to .env and fill in your API keys", 
                         ""]
        
        for provider, config in self.api_providers.items():
            result = self.results.get(provider, {})
            status = result.get('status', 'unknown')
            
            template_lines.append(f"# {provider.upper()} - Status: {status}")
            if not result.get('valid', False):
                template_lines.append(f"{config['env_key']}=your_{provider}_api_key_here")
            else:
                template_lines.append(f"# {config['env_key']} is already configured and valid")
            template_lines.append("")
        
        return '\n'.join(template_lines)
    
    def generate_fallback_config(self) -> Dict[str, list]:
        """Generate intelligent fallback configuration based on valid keys"""
        fallback_config = {
            'primary_providers': [],
            'fallback_providers': [],
            'offline_providers': ['llama3.1:70b', 'codellama:34b']
        }
        
        # Categorize providers by reliability
        high_reliability = ['deepseek', 'openai', 'claude']
        medium_reliability = ['glm', 'qwen', 'openrouter']
        low_reliability = ['grok']
        
        for provider in high_reliability:
            if self.valid_keys.get(provider):
                fallback_config['primary_providers'].append(provider)
        
        for provider in medium_reliability:
            if self.valid_keys.get(provider):
                fallback_config['fallback_providers'].append(provider)
        
        for provider in low_reliability:
            if self.valid_keys.get(provider):
                fallback_config['fallback_providers'].append(provider)
        
        return fallback_config
    
    def save_validation_report(self) -> str:
        """Save validation report to file"""
        report_path = 'api_validation_report.json'
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'validation_results': self.results,
            'valid_providers': list(self.valid_keys.keys()),
            'fallback_config': self.generate_fallback_config(),
            'recommendations': self.generate_recommendations()
        }
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report_path
    
    def generate_recommendations(self) -> list:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        valid_count = len(self.valid_keys)
        total_count = len(self.api_providers)
        
        if valid_count == 0:
            recommendations.append({
                'priority': 'critical',
                'message': 'No valid API keys found. The system will only work in offline mode.',
                'action': 'Configure at least one API key to enable online features.'
            })
        elif valid_count < 3:
            recommendations.append({
                'priority': 'high',
                'message': f'Only {valid_count} valid API keys found.',
                'action': 'Configure more API keys for better redundancy and load balancing.'
            })
        
        # Check for specific providers
        if 'deepseek' not in self.valid_keys and 'openai' not in self.valid_keys:
            recommendations.append({
                'priority': 'medium',
                'message': 'No primary AI provider (DeepSeek/OpenAI) configured.',
                'action': 'Consider adding DeepSeek or OpenAI for optimal performance.'
            })
        
        if 'openrouter' in self.valid_keys:
            recommendations.append({
                'priority': 'info',
                'message': 'OpenRouter detected - good for accessing multiple models.',
                'action': 'Ensure your OpenRouter account has sufficient credits.'
            })
        
        return recommendations
    
    def print_summary(self):
        """Print a summary of validation results"""
        print("\n" + "="*60)
        print("API Configuration Validation Summary")
        print("="*60 + "\n")
        
        # Status counts
        valid_count = sum(1 for r in self.results.values() if r.get('valid'))
        invalid_count = sum(1 for r in self.results.values() if r.get('status') == 'invalid')
        missing_count = sum(1 for r in self.results.values() if r.get('status') == 'missing')
        
        print(f"✓ Valid API Keys: {valid_count}")
        print(f"✗ Invalid API Keys: {invalid_count}")
        print(f"? Missing API Keys: {missing_count}")
        print(f"Total Providers: {len(self.results)}\n")
        
        # Detailed results
        print("Provider Status:")
        print("-" * 40)
        for provider, result in self.results.items():
            status_symbol = "✓" if result.get('valid') else "✗"
            print(f"{status_symbol} {provider.ljust(15)} - {result.get('message', 'Unknown')}")
        
        # Recommendations
        print("\n" + "="*60)
        print("Recommendations:")
        print("="*60)
        
        recommendations = self.generate_recommendations()
        for rec in recommendations:
            print(f"\n[{rec['priority'].upper()}] {rec['message']}")
            print(f"  → {rec['action']}")
        
        print("\n" + "="*60)


def main():
    """Main entry point"""
    validator = APIConfigValidator()
    
    # Validate all keys
    results = validator.validate_all_keys()
    
    # Print summary
    validator.print_summary()
    
    # Generate configuration template
    template = validator.generate_config_template()
    template_path = '.env.template'
    with open(template_path, 'w') as f:
        f.write(template)
    print(f"\n✓ Configuration template saved to: {template_path}")
    
    # Save validation report
    report_path = validator.save_validation_report()
    print(f"✓ Validation report saved to: {report_path}")
    
    # Generate fallback configuration
    fallback_config = validator.generate_fallback_config()
    fallback_path = 'ai_fallback_config.json'
    with open(fallback_path, 'w') as f:
        json.dump(fallback_config, f, indent=2)
    print(f"✓ Fallback configuration saved to: {fallback_path}")
    
    # Exit with appropriate code
    if len(validator.valid_keys) == 0:
        sys.exit(1)  # No valid keys
    elif len(validator.valid_keys) < 3:
        sys.exit(2)  # Limited keys
    else:
        sys.exit(0)  # Good configuration


if __name__ == "__main__":
    main()
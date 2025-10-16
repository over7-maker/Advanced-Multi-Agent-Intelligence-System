#!/usr/bin/env python3
"""
AI Dependency Resolver - Comprehensive dependency analysis and resolution
Uses 16 AI providers with intelligent fallback and health monitoring
"""

import os
import sys
import json
import asyncio
import subprocess
import importlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from bulletproof_real_ai import BulletproofRealAI
except ImportError as e:
    print(f"❌ Failed to import bulletproof_real_ai: {e}")
    print("Installing required dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "aiohttp", "openai", "anthropic", "google-generativeai", "groq", "cohere", "mistralai"], check=True)
    from bulletproof_real_ai import BulletproofRealAI

class AIDependencyResolver:
    """AI-powered dependency resolver with comprehensive analysis"""
    
    def __init__(self):
        self.issues_detected = {
            'missing_modules': [],
            'import_errors': [],
            'version_conflicts': [],
            'error_count': 0
        }
        self.fixes_applied = {
            'total_applied': 0,
            'total_failed': 0,
            'applied_fixes': [],
            'failed_fixes': []
        }
        self.ai_analysis = {}
        
    def detect_missing_modules(self) -> List[str]:
        """Detect missing Python modules by testing imports"""
        print("🔍 Detecting missing modules...")
        
        # Common modules that might be missing
        test_modules = [
            'aiohttp', 'openai', 'cohere', 'multidict', 'yarl', 
            'attrs', 'aiosignal', 'frozenlist', 'httpx', 'requests',
            'numpy', 'pandas', 'scikit-learn', 'matplotlib', 'seaborn',
            'plotly', 'sqlalchemy', 'redis', 'neo4j', 'bcrypt',
            'cryptography', 'jwt', 'beautifulsoup4', 'selenium',
            'sentence_transformers', 'faiss', 'yaml', 'pydantic'
        ]
        
        missing_modules = []
        
        for module in test_modules:
            try:
                importlib.import_module(module)
                print(f"✅ {module} - OK")
            except ImportError as e:
                missing_modules.append(module)
                print(f"❌ {module} - MISSING: {e}")
                self.issues_detected['error_count'] += 1
        
        self.issues_detected['missing_modules'] = missing_modules
        return missing_modules
    
    def analyze_requirements_txt(self) -> Dict[str, Any]:
        """Analyze requirements.txt for potential issues"""
        print("📋 Analyzing requirements.txt...")
        
        requirements_analysis = {
            'file_exists': False,
            'total_packages': 0,
            'version_pinned': 0,
            'potential_conflicts': [],
            'missing_dependencies': []
        }
        
        if os.path.exists('requirements.txt'):
            requirements_analysis['file_exists'] = True
            
            with open('requirements.txt', 'r') as f:
                lines = f.readlines()
            
            packages = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    packages.append(line)
                    if '==' in line or '>=' in line or '<=' in line:
                        requirements_analysis['version_pinned'] += 1
            
            requirements_analysis['total_packages'] = len(packages)
            
            # Check for common missing dependencies
            common_deps = ['aiohttp', 'multidict', 'yarl', 'attrs', 'aiosignal', 'frozenlist']
            for dep in common_deps:
                if not any(dep in pkg for pkg in packages):
                    requirements_analysis['missing_dependencies'].append(dep)
        
        return requirements_analysis
    
    async def get_ai_analysis(self, missing_modules: List[str], requirements_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Get AI analysis for dependency issues"""
        print("🤖 Getting AI analysis...")
        
        # Create comprehensive prompt
        prompt = f"""
        Analyze these Python dependency issues and provide specific, actionable solutions:
        
        Missing Modules: {missing_modules}
        Requirements Analysis: {json.dumps(requirements_analysis, indent=2)}
        
        Please provide:
        1. Root cause analysis
        2. Priority level (low/medium/high)
        3. Confidence score (0-1)
        4. Specific pip install commands to fix issues
        5. Updated requirements.txt content
        6. Long-term recommendations
        
        Format your response as JSON with these keys:
        - root_cause: string
        - priority: string
        - confidence: float
        - pip_commands: array of strings
        - requirements_txt: string
        - analysis: string
        - recommendations: object with immediate_actions, long_term_improvements, workflow_changes arrays
        """
        
        try:
            result = await ai_agent.analyze_with_fallback(prompt, "dependency_analysis")
            
            if result['success']:
                # Parse AI response
                try:
                    ai_data = json.loads(result['content'])
                    self.ai_analysis = ai_data
                except json.JSONDecodeError:
                    # If not JSON, create structured response
                    self.ai_analysis = {
                        'root_cause': 'Dependency installation failures',
                        'priority': 'high',
                        'confidence': 0.8,
                        'pip_commands': [
                            'pip install --upgrade pip',
                            'pip install aiohttp multidict yarl attrs aiosignal frozenlist',
                            'pip install -r requirements.txt'
                        ],
                        'requirements_txt': '',
                        'analysis': result['content'],
                        'recommendations': {
                            'immediate_actions': [
                                'Install missing dependencies',
                                'Update requirements.txt',
                                'Verify all imports work'
                            ],
                            'long_term_improvements': [
                                'Pin all dependency versions',
                                'Use virtual environments',
                                'Regular dependency audits'
                            ],
                            'workflow_changes': [
                                'Add dependency installation step',
                                'Test imports in CI/CD',
                                'Use requirements.txt in workflows'
                            ]
                        }
                    }
                
                return self.ai_analysis
            else:
                print(f"❌ AI analysis failed: {result.get('error', 'Unknown error')}")
                return {}
                
        except Exception as e:
            print(f"❌ Error getting AI analysis: {e}")
            return {}
    
    def apply_fixes(self, ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Apply AI-suggested fixes"""
        print("🔧 Applying AI-suggested fixes...")
        
        applied_fixes = []
        failed_fixes = []
        
        # Apply pip commands
        pip_commands = ai_analysis.get('pip_commands', [])
        for cmd in pip_commands[:5]:  # Limit to 5 commands
            try:
                print(f"Running: {cmd}")
                result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    applied_fixes.append({
                        'type': 'pip_command',
                        'command': cmd,
                        'status': 'success'
                    })
                    print(f"✅ Success: {cmd}")
                else:
                    failed_fixes.append({
                        'type': 'pip_command',
                        'command': cmd,
                        'status': 'failed',
                        'error': result.stderr
                    })
                    print(f"❌ Failed: {cmd} - {result.stderr}")
                    
            except Exception as e:
                failed_fixes.append({
                    'type': 'pip_command',
                    'command': cmd,
                    'status': 'failed',
                    'error': str(e)
                })
                print(f"❌ Exception: {cmd} - {e}")
        
        # Update requirements.txt if provided
        requirements_content = ai_analysis.get('requirements_txt', '')
        if requirements_content.strip():
            try:
                with open('requirements.txt', 'w') as f:
                    f.write(requirements_content)
                applied_fixes.append({
                    'type': 'requirements_update',
                    'status': 'success'
                })
                print("✅ Updated requirements.txt")
            except Exception as e:
                failed_fixes.append({
                    'type': 'requirements_update',
                    'status': 'failed',
                    'error': str(e)
                })
                print(f"❌ Failed to update requirements.txt: {e}")
        
        self.fixes_applied = {
            'total_applied': len(applied_fixes),
            'total_failed': len(failed_fixes),
            'applied_fixes': applied_fixes,
            'failed_fixes': failed_fixes
        }
        
        return self.fixes_applied
    
    async def run_analysis(self) -> Dict[str, Any]:
        """Run complete dependency analysis"""
        print("🚀 Starting AI Dependency Resolver...")
        print("=" * 60)
        
        try:
            # Step 1: Detect missing modules
            missing_modules = self.detect_missing_modules()
            
            # Step 2: Analyze requirements.txt
            requirements_analysis = self.analyze_requirements_txt()
            
            # Step 3: Get AI analysis
            ai_analysis = await self.get_ai_analysis(missing_modules, requirements_analysis)
            
            # Step 4: Apply fixes
            if ai_analysis:
                fix_results = self.apply_fixes(ai_analysis)
            
            # Step 5: Verify fixes
            print("🧪 Verifying fixes...")
            final_missing = self.detect_missing_modules()
            
            # Create results
            results = {
                'metadata': {
                    'timestamp': datetime.utcnow().isoformat(),
                    'status': 'completed',
                    'ai_provider_used': ai_analysis.get('provider_used', 'unknown'),
                    'response_time': ai_analysis.get('response_time', 0)
                },
                'issues_detected': self.issues_detected,
                'requirements_analysis': requirements_analysis,
                'ai_analysis': ai_analysis,
                'fixes_applied': self.fixes_applied,
                'verification': {
                    'modules_before': len(missing_modules),
                    'modules_after': len(final_missing),
                    'improvement': len(missing_modules) - len(final_missing)
                }
            }
            
            return results
            
        except Exception as e:
            print(f"❌ Critical error in dependency resolver: {e}")
            return {
                'metadata': {
                    'timestamp': datetime.utcnow().isoformat(),
                    'status': 'failed',
                    'error': str(e)
                },
                'issues_detected': self.issues_detected,
                'ai_analysis': {},
                'fixes_applied': self.fixes_applied
            }

async def main():
    """Main function to run dependency resolver"""
    print("🤖 AI Dependency Resolver Starting...")
    
    # Create artifacts directory
    os.makedirs("artifacts", exist_ok=True)
    
    # Run resolver
    resolver = AIDependencyResolver()
    results = await resolver.run_analysis()
    
    # Save results
    with open("artifacts/dependency_resolution.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 60)
    print("🎉 AI DEPENDENCY RESOLVER COMPLETE!")
    print("=" * 60)
    print(f"📊 Status: {results['metadata']['status']}")
    print(f"🔍 Issues Detected: {results['issues_detected']['error_count']}")
    print(f"🔧 Fixes Applied: {results['fixes_applied']['total_applied']}")
    print(f"❌ Fixes Failed: {results['fixes_applied']['total_failed']}")
    
    if results['fixes_applied']['total_applied'] > 0:
        print("✅ Some fixes were successfully applied")
    else:
        print("⚠️ No fixes were applied")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())
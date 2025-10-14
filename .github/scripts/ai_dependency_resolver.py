#!/usr/bin/env python3
"""
AI-Powered Dependency Resolver & Code Auto-Fix Agent
AMAS - using 16-provider fallback system
"""

import os
import sys
import subprocess
import json
import asyncio
import aiohttp
import re
from datetime import datetime
from typing import Dict, List, Any, Optional

# Import our AI agent fallback system
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ai_agent_fallback import ai_agent

class AIDependencyResolver:
    """AI-powered dependency resolver with 16-provider fallback"""
    
    def __init__(self):
        self.start_time = datetime.utcnow()
        self.errors = []
        self.fixes_applied = []
        
    async def collect_dependency_data(self) -> Dict[str, Any]:
        """Collect comprehensive dependency and error data"""
        print("🔍 Collecting dependency data...")
        
        data = {
            "timestamp": self.start_time.isoformat(),
            "python_version": sys.version,
            "platform": os.name,
            "pip_freeze": "",
            "error_logs": [],
            "missing_modules": [],
            "conflict_errors": [],
            "import_errors": [],
            "workflow_logs": []
        }
        
        try:
            # Get current pip freeze
            result = subprocess.run(["pip", "freeze"], capture_output=True, text=True, timeout=30)
            data["pip_freeze"] = result.stdout
            if result.stderr:
                data["error_logs"].append(f"pip freeze stderr: {result.stderr}")
        except Exception as e:
            data["error_logs"].append(f"pip freeze failed: {e}")
        
        # Check for common error patterns
        error_patterns = [
            r"ModuleNotFoundError: No module named '([^']+)'",
            r"ImportError: No module named '([^']+)'",
            r"ModuleNotFoundError: No module named \"([^\"]+)\"",
            r"ImportError: No module named \"([^\"]+)\"",
            r"ERROR: Could not find a version that satisfies the requirement ([^\s]+)",
            r"ERROR: No matching distribution found for ([^\s]+)",
            r"ERROR: Failed building wheel for ([^\s]+)",
            r"ERROR: Command errored out with exit status \d+",
        ]
        
        # Look for error logs in common locations
        log_locations = [
            "/tmp/github_workflow_logs.txt",
            "artifacts/error_logs.txt",
            ".github/logs/",
            "logs/",
            "/var/log/",
        ]
        
        for location in log_locations:
            if os.path.exists(location):
                try:
                    if os.path.isfile(location):
                        with open(location, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            for pattern in error_patterns:
                                matches = re.findall(pattern, content, re.IGNORECASE)
                                data["missing_modules"].extend(matches)
                                if matches:
                                    data["error_logs"].append(f"Found in {location}: {matches}")
                    elif os.path.isdir(location):
                        for root, dirs, files in os.walk(location):
                            for file in files:
                                if file.endswith(('.log', '.txt', '.err')):
                                    filepath = os.path.join(root, file)
                                    try:
                                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                                            content = f.read()
                                            for pattern in error_patterns:
                                                matches = re.findall(pattern, content, re.IGNORECASE)
                                                data["missing_modules"].extend(matches)
                                                if matches:
                                                    data["error_logs"].append(f"Found in {filepath}: {matches}")
                                    except Exception:
                                        continue
                except Exception as e:
                    data["error_logs"].append(f"Error reading {location}: {e}")
        
        # Remove duplicates and clean up
        data["missing_modules"] = list(set(data["missing_modules"]))
        data["error_logs"] = data["error_logs"][:20]  # Limit to 20 most recent errors
        
        return data
    
    async def analyze_with_ai(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to analyze dependency issues and suggest fixes"""
        print("🤖 Analyzing dependency issues with AI...")
        
        # Create comprehensive prompt for AI analysis
        prompt = f"""
As an expert Python dependency and DevOps engineer, analyze these dependency issues and provide actionable fixes.

## Current Environment:
- Python Version: {data['python_version']}
- Platform: {data['platform']}
- Timestamp: {data['timestamp']}

## Error Logs:
{chr(10).join(data['error_logs'][:10])}

## Missing Modules Detected:
{', '.join(data['missing_modules'][:20])}

## Current Installed Packages:
{data['pip_freeze'][:2000]}

## Task:
1. **Identify the root cause** of dependency failures
2. **Provide exact pip install commands** to fix missing dependencies
3. **Suggest requirements.txt updates** with proper version pins
4. **Recommend workflow YAML changes** if needed
5. **Provide code patches** if import errors exist
6. **Suggest preventive measures** to avoid future issues

## Response Format:
Provide your analysis in this exact JSON format:
```json
{{
  "analysis": "Brief analysis of the issues",
  "root_cause": "Primary cause of failures",
  "pip_commands": ["pip install package1==version1", "pip install package2==version2"],
  "requirements_txt": "Updated requirements.txt content",
  "workflow_fixes": ["YAML changes needed"],
  "code_patches": ["Code changes if needed"],
  "prevention": ["Steps to prevent future issues"],
  "confidence": 0.95,
  "priority": "high|medium|low"
}}
```

Be specific, actionable, and focus on immediate fixes that will resolve the current failures.
"""
        
        try:
            print("📝 Sending comprehensive analysis to AI providers...")
            result = await ai_agent.analyze_with_fallback(prompt, "dependency_analysis")
            
            if result.get('success'):
                print(f"✅ AI analysis completed using {result.get('provider_used', 'unknown')} provider")
                print(f"⏱️ Response Time: {result.get('response_time', 0):.2f}s")
                
                # Try to extract JSON from AI response
                content = result.get('content', '')
                try:
                    # Look for JSON in the response
                    json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
                    if json_match:
                        ai_analysis = json.loads(json_match.group(1))
                    else:
                        # Fallback: create structured response
                        ai_analysis = {
                            "analysis": content[:500],
                            "root_cause": "Dependency installation issues",
                            "pip_commands": self._extract_pip_commands(content),
                            "requirements_txt": self._extract_requirements(content),
                            "workflow_fixes": self._extract_workflow_fixes(content),
                            "code_patches": [],
                            "prevention": ["Regular dependency updates", "Version pinning"],
                            "confidence": 0.8,
                            "priority": "high"
                        }
                except json.JSONDecodeError:
                    # Fallback if JSON parsing fails
                    ai_analysis = {
                        "analysis": content[:500],
                        "root_cause": "Dependency installation issues",
                        "pip_commands": self._extract_pip_commands(content),
                        "requirements_txt": "",
                        "workflow_fixes": [],
                        "code_patches": [],
                        "prevention": ["Regular dependency updates"],
                        "confidence": 0.7,
                        "priority": "high"
                    }
                
                return {
                    "success": True,
                    "provider_used": result.get('provider_used'),
                    "response_time": result.get('response_time', 0),
                    "analysis": ai_analysis,
                    "raw_response": content
                }
            else:
                print(f"❌ AI analysis failed: {result.get('error', 'Unknown error')}")
                return {
                    "success": False,
                    "error": result.get('error', 'AI analysis failed'),
                    "analysis": self._create_fallback_analysis(data)
                }
                
        except Exception as e:
            print(f"❌ Exception during AI analysis: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis": self._create_fallback_analysis(data)
            }
    
    def _extract_pip_commands(self, content: str) -> List[str]:
        """Extract pip install commands from AI response"""
        commands = []
        # Look for pip install patterns
        pip_patterns = [
            r'pip install[^\\n]*',
            r'pip3 install[^\\n]*',
            r'python -m pip install[^\\n]*'
        ]
        
        for pattern in pip_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            commands.extend(matches)
        
        return commands[:10]  # Limit to 10 commands
    
    def _extract_requirements(self, content: str) -> str:
        """Extract requirements.txt content from AI response"""
        # Look for requirements.txt content
        req_match = re.search(r'requirements\.txt[:\s]*\n(.*?)(?:\n\n|\Z)', content, re.DOTALL | re.IGNORECASE)
        if req_match:
            return req_match.group(1).strip()
        return ""
    
    def _extract_workflow_fixes(self, content: str) -> List[str]:
        """Extract workflow YAML fixes from AI response"""
        fixes = []
        # Look for YAML or workflow-related suggestions
        yaml_patterns = [
            r'```yaml\s*(.*?)\s*```',
            r'workflow[^\\n]*',
            r'pip install[^\\n]*'
        ]
        
        for pattern in yaml_patterns:
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            fixes.extend(matches)
        
        return fixes[:5]  # Limit to 5 fixes
    
    def _create_fallback_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback analysis when AI fails"""
        missing_modules = data.get('missing_modules', [])
        
        pip_commands = []
        for module in missing_modules[:10]:  # Limit to 10 modules
            pip_commands.append(f"pip install {module}")
        
        return {
            "analysis": f"Detected {len(missing_modules)} missing modules. Applying standard fixes.",
            "root_cause": "Missing Python dependencies",
            "pip_commands": pip_commands,
            "requirements_txt": "",
            "workflow_fixes": ["Ensure all dependencies are installed with proper versions"],
            "code_patches": [],
            "prevention": ["Add missing dependencies to requirements.txt", "Pin versions"],
            "confidence": 0.6,
            "priority": "high"
        }
    
    async def apply_fixes(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Apply suggested fixes automatically"""
        print("🔧 Applying AI-suggested fixes...")
        
        applied_fixes = []
        failed_fixes = []
        
        # Apply pip commands
        pip_commands = analysis.get('pip_commands', [])
        for cmd in pip_commands[:5]:  # Limit to 5 commands
            try:
                print(f"📦 Running: {cmd}")
                result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=60)
                if result.returncode == 0:
                    applied_fixes.append(f"✅ {cmd}")
                    print(f"✅ Success: {cmd}")
                else:
                    failed_fixes.append(f"❌ {cmd}: {result.stderr}")
                    print(f"❌ Failed: {cmd} - {result.stderr}")
            except Exception as e:
                failed_fixes.append(f"❌ {cmd}: {e}")
                print(f"❌ Exception: {cmd} - {e}")
        
        return {
            "applied_fixes": applied_fixes,
            "failed_fixes": failed_fixes,
            "total_applied": len(applied_fixes),
            "total_failed": len(failed_fixes)
        }
    
    async def generate_report(self, data: Dict[str, Any], analysis: Dict[str, Any], fixes: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive report"""
        report = {
            "metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "resolver_version": "1.0.0",
                "execution_time": (datetime.utcnow() - self.start_time).total_seconds(),
                "ai_success": analysis.get('success', False),
                "provider_used": analysis.get('provider_used'),
                "response_time": analysis.get('response_time', 0)
            },
            "issues_detected": {
                "missing_modules": data.get('missing_modules', []),
                "error_count": len(data.get('error_logs', [])),
                "python_version": data.get('python_version'),
                "platform": data.get('platform')
            },
            "ai_analysis": analysis.get('analysis', {}),
            "fixes_applied": fixes,
            "recommendations": {
                "immediate_actions": analysis.get('analysis', {}).get('pip_commands', []),
                "long_term_improvements": analysis.get('analysis', {}).get('prevention', []),
                "workflow_changes": analysis.get('analysis', {}).get('workflow_fixes', [])
            },
            "status": "completed" if analysis.get('success') else "partial"
        }
        
        return report

async def main():
    """Main function to run AI dependency resolver"""
    print("🚀 Starting AI Dependency Resolver...")
    print("=" * 60)
    
    resolver = AIDependencyResolver()
    
    try:
        # Step 1: Collect dependency data
        data = await resolver.collect_dependency_data()
        print(f"📊 Collected data: {len(data['missing_modules'])} missing modules, {len(data['error_logs'])} errors")
        
        # Step 2: Analyze with AI
        analysis = await resolver.analyze_with_ai(data)
        
        # Step 3: Apply fixes if analysis was successful
        fixes = {}
        if analysis.get('success'):
            fixes = await resolver.apply_fixes(analysis['analysis'])
        
        # Step 4: Generate comprehensive report
        report = await resolver.generate_report(data, analysis, fixes)
        
        # Step 5: Save results
        os.makedirs("artifacts", exist_ok=True)
        with open("artifacts/dependency_resolution.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Step 6: Print summary
        print("\n" + "=" * 60)
        print("🎉 AI DEPENDENCY RESOLVER COMPLETE!")
        print("=" * 60)
        print(f"📊 Status: {report['status']}")
        print(f"🤖 AI Provider: {report['metadata'].get('provider_used', 'None')}")
        print(f"⏱️ Response Time: {report['metadata'].get('response_time', 0):.2f}s")
        print(f"🔧 Fixes Applied: {fixes.get('total_applied', 0)}")
        print(f"❌ Fixes Failed: {fixes.get('total_failed', 0)}")
        print(f"📄 Report saved to: artifacts/dependency_resolution.json")
        
        # Print AI recommendations
        if analysis.get('success') and analysis.get('analysis'):
            ai_analysis = analysis['analysis']
            print(f"\n🎯 AI RECOMMENDATIONS:")
            print(f"Root Cause: {ai_analysis.get('root_cause', 'Unknown')}")
            print(f"Priority: {ai_analysis.get('priority', 'Unknown')}")
            print(f"Confidence: {ai_analysis.get('confidence', 0):.2f}")
            
            if ai_analysis.get('pip_commands'):
                print(f"\n📦 Suggested Commands:")
                for cmd in ai_analysis['pip_commands'][:5]:
                    print(f"  {cmd}")
        
        return report
        
    except Exception as e:
        print(f"❌ Critical error in dependency resolver: {e}")
        import traceback
        print(f"🔍 Traceback: {traceback.format_exc()}")
        
        # Create minimal error report
        error_report = {
            "metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "status": "failed",
                "error": str(e)
            },
            "issues_detected": {"error_count": 1},
            "ai_analysis": {"analysis": "Failed to analyze due to critical error"},
            "fixes_applied": {"total_applied": 0, "total_failed": 1},
            "recommendations": {"immediate_actions": ["Check logs and retry"]}
        }
        
        os.makedirs("artifacts", exist_ok=True)
        with open("artifacts/dependency_resolution.json", "w") as f:
            json.dump(error_report, f, indent=2)
        
        return error_report

if __name__ == "__main__":
    asyncio.run(main())
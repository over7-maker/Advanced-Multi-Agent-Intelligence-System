#!/usr/bin/env python3
"""
AI Dependency Pinner - Intelligently manage and pin safe dependency versions
Proactively prevents future dependency issues
"""

import os
import sys
import json
import asyncio
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# Import our AI agent fallback system
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ai_agent_fallback import ai_agent

class AIDependencyPinner:
    """AI-powered dependency version pinning and management"""
    
    def __init__(self):
        self.requirements_file = "requirements.txt"
        self.pinned_versions_file = "artifacts/pinned_versions.json"
        self.vulnerability_db_file = "artifacts/vulnerability_database.json"
        self.load_pinned_versions()
    
    def load_pinned_versions(self):
        """Load existing pinned versions data"""
        self.pinned_versions = {
            "pinned_packages": {},
            "vulnerability_scores": {},
            "stability_scores": {},
            "last_updated": None,
            "pinning_history": []
        }
        
        if os.path.exists(self.pinned_versions_file):
            try:
                with open(self.pinned_versions_file, 'r') as f:
                    self.pinned_versions = json.load(f)
            except Exception as e:
                print(f"⚠️ Error loading pinned versions: {e}")
    
    def save_pinned_versions(self):
        """Save pinned versions data"""
        self.pinned_versions["last_updated"] = datetime.now().isoformat()
        os.makedirs("artifacts", exist_ok=True)
        with open(self.pinned_versions_file, "w") as f:
            json.dump(self.pinned_versions, f, indent=2)
    
    async def analyze_current_dependencies(self) -> Dict[str, Any]:
        """Analyze current dependencies and their versions"""
        print("🔍 Analyzing current dependencies...")
        
        dependencies = {}
        
        try:
            # Get pip freeze output
            result = subprocess.run(['pip', 'freeze'], capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if '==' in line:
                        package, version = line.split('==', 1)
                        dependencies[package.lower()] = {
                            "current_version": version,
                            "package_name": package,
                            "pinned": False,
                            "vulnerability_score": 0,
                            "stability_score": 0
                        }
        except Exception as e:
            print(f"⚠️ Error getting pip freeze: {e}")
        
        # Check requirements.txt
        if os.path.exists(self.requirements_file):
            try:
                with open(self.requirements_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            if '==' in line:
                                package, version = line.split('==', 1)
                                package = package.strip().lower()
                                if package in dependencies:
                                    dependencies[package]["pinned"] = True
                                    dependencies[package]["requirements_version"] = version.strip()
            except Exception as e:
                print(f"⚠️ Error reading requirements.txt: {e}")
        
        return dependencies
    
    async def get_ai_version_recommendations(self, dependencies: Dict[str, Any]) -> Dict[str, Any]:
        """Get AI recommendations for version pinning"""
        print("🤖 Getting AI version recommendations...")
        
        # Create analysis prompt
        prompt = f"""
As an expert Python dependency manager and security analyst, analyze these dependencies and provide intelligent version pinning recommendations.

## Current Dependencies:
{json.dumps(dependencies, indent=2)}

## Analysis Tasks:
1. **Security Analysis**: Identify packages with known vulnerabilities
2. **Stability Analysis**: Recommend stable versions for each package
3. **Compatibility Analysis**: Ensure version compatibility
4. **Pinning Strategy**: Suggest optimal pinning approach (exact, compatible, latest-stable)

## Response Format:
Provide your analysis in this JSON format:
```json
{{
  "recommendations": {{
    "package_name": {{
      "recommended_version": "1.2.3",
      "pinning_strategy": "exact|compatible|latest-stable",
      "security_score": 0.95,
      "stability_score": 0.90,
      "reasoning": "Explanation for this recommendation",
      "vulnerabilities": ["CVE-2023-1234", "CVE-2023-5678"],
      "breaking_changes": false,
      "compatibility_notes": "Compatible with Python 3.11+"
    }}
  }},
  "overall_security_score": 0.85,
  "pinning_strategy": "mixed",
  "priority_fixes": [
    "Package with critical vulnerabilities",
    "Package with breaking changes"
  ],
  "requirements_txt_content": "Updated requirements.txt content"
}}
```

Focus on security, stability, and compatibility. Prioritize packages with vulnerabilities or breaking changes.
"""
        
        try:
            result = await ai_agent.analyze_with_fallback(prompt, "dependency_pinning_analysis")
            
            if result.get('success'):
                # Extract JSON from response
                content = result.get('content', '')
                try:
                    import re
                    json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
                    if json_match:
                        ai_recommendations = json.loads(json_match.group(1))
                    else:
                        # Fallback recommendations
                        ai_recommendations = {
                            "recommendations": {},
                            "overall_security_score": 0.7,
                            "pinning_strategy": "exact",
                            "priority_fixes": [],
                            "requirements_txt_content": ""
                        }
                    
                    return {
                        "success": True,
                        "recommendations": ai_recommendations,
                        "provider_used": result.get('provider_used'),
                        "response_time": result.get('response_time', 0)
                    }
                except json.JSONDecodeError:
                    return {
                        "success": False,
                        "error": "Failed to parse AI recommendations"
                    }
            else:
                return {
                    "success": False,
                    "error": result.get('error', 'AI analysis failed')
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Exception in AI analysis: {e}"
            }
    
    async def apply_version_pinning(self, recommendations: Dict[str, Any]) -> Dict[str, Any]:
        """Apply AI-recommended version pinning"""
        print("📌 Applying AI-recommended version pinning...")
        
        applied_pins = []
        failed_pins = []
        
        if not recommendations.get('success'):
            return {
                "success": False,
                "error": "No valid recommendations to apply"
            }
        
        ai_recs = recommendations['recommendations']
        package_recommendations = ai_recs.get('recommendations', {})
        
        for package_name, rec in package_recommendations.items():
            try:
                recommended_version = rec.get('recommended_version')
                pinning_strategy = rec.get('pinning_strategy', 'exact')
                
                if not recommended_version:
                    continue
                
                # Apply the pinning
                if pinning_strategy == 'exact':
                    pin_spec = f"{package_name}=={recommended_version}"
                elif pinning_strategy == 'compatible':
                    pin_spec = f"{package_name}~={recommended_version}"
                else:  # latest-stable
                    pin_spec = f"{package_name}>={recommended_version}"
                
                # Update pinned versions data
                self.pinned_versions["pinned_packages"][package_name] = {
                    "version": recommended_version,
                    "strategy": pinning_strategy,
                    "security_score": rec.get('security_score', 0),
                    "stability_score": rec.get('stability_score', 0),
                    "reasoning": rec.get('reasoning', ''),
                    "vulnerabilities": rec.get('vulnerabilities', []),
                    "pinned_at": datetime.now().isoformat()
                }
                
                applied_pins.append({
                    "package": package_name,
                    "version": recommended_version,
                    "strategy": pinning_strategy,
                    "pin_spec": pin_spec
                })
                
                print(f"✅ Pinned {package_name} to {recommended_version} ({pinning_strategy})")
                
            except Exception as e:
                failed_pins.append({
                    "package": package_name,
                    "error": str(e)
                })
                print(f"❌ Failed to pin {package_name}: {e}")
        
        # Update requirements.txt if provided
        requirements_content = ai_recs.get('requirements_txt_content', '')
        if requirements_content.strip():
            try:
                with open(self.requirements_file, 'w') as f:
                    f.write(requirements_content)
                print(f"✅ Updated {self.requirements_file}")
            except Exception as e:
                print(f"⚠️ Failed to update requirements.txt: {e}")
        
        # Save updated pinned versions
        self.save_pinned_versions()
        
        return {
            "success": True,
            "applied_pins": applied_pins,
            "failed_pins": failed_pins,
            "total_applied": len(applied_pins),
            "total_failed": len(failed_pins)
        }
    
    async def generate_pinning_report(self) -> Dict[str, Any]:
        """Generate comprehensive pinning report"""
        print("📊 Generating dependency pinning report...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_pinned": len(self.pinned_versions["pinned_packages"]),
                "security_issues": 0,
                "stability_issues": 0,
                "recommendations_count": 0
            },
            "pinned_packages": self.pinned_versions["pinned_packages"],
            "security_analysis": {},
            "stability_analysis": {},
            "recommendations": []
        }
        
        # Analyze security and stability
        for package, data in self.pinned_versions["pinned_packages"].items():
            security_score = data.get('security_score', 0)
            stability_score = data.get('stability_score', 0)
            
            if security_score < 0.8:
                report["summary"]["security_issues"] += 1
                report["security_analysis"][package] = {
                    "score": security_score,
                    "vulnerabilities": data.get('vulnerabilities', []),
                    "status": "needs_attention"
                }
            
            if stability_score < 0.8:
                report["summary"]["stability_issues"] += 1
                report["stability_analysis"][package] = {
                    "score": stability_score,
                    "status": "unstable"
                }
        
        # Generate recommendations
        if report["summary"]["security_issues"] > 0:
            report["recommendations"].append("Address packages with security issues")
        
        if report["summary"]["stability_issues"] > 0:
            report["recommendations"].append("Consider more stable versions for unstable packages")
        
        if report["summary"]["total_pinned"] < 10:
            report["recommendations"].append("Consider pinning more dependencies for better reproducibility")
        
        return report

async def main():
    """Main function to run AI dependency pinner"""
    print("📌 AI Dependency Pinner Starting...")
    print("=" * 60)
    
    pinner = AIDependencyPinner()
    
    try:
        # Step 1: Analyze current dependencies
        dependencies = await pinner.analyze_current_dependencies()
        print(f"📦 Found {len(dependencies)} dependencies")
        
        # Step 2: Get AI recommendations
        recommendations = await pinner.get_ai_version_recommendations(dependencies)
        
        if recommendations.get('success'):
            print(f"✅ AI recommendations received from {recommendations.get('provider_used')}")
            
            # Step 3: Apply version pinning
            pinning_result = await pinner.apply_version_pinning(recommendations)
            
            if pinning_result.get('success'):
                print(f"📌 Applied {pinning_result['total_applied']} version pins")
                if pinning_result['total_failed'] > 0:
                    print(f"❌ {pinning_result['total_failed']} pins failed")
            else:
                print(f"❌ Failed to apply pinning: {pinning_result.get('error')}")
        else:
            print(f"❌ Failed to get AI recommendations: {recommendations.get('error')}")
        
        # Step 4: Generate report
        report = await pinner.generate_pinning_report()
        
        # Save report
        os.makedirs("artifacts", exist_ok=True)
        with open("artifacts/dependency_pinning_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 DEPENDENCY PINNING REPORT")
        print("=" * 60)
        print(f"📌 Total Pinned: {report['summary']['total_pinned']}")
        print(f"🔒 Security Issues: {report['summary']['security_issues']}")
        print(f"⚖️ Stability Issues: {report['summary']['stability_issues']}")
        
        if report['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in report['recommendations']:
                print(f"  - {rec}")
        
        return report
        
    except Exception as e:
        print(f"❌ Critical error in dependency pinner: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    asyncio.run(main())
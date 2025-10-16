#!/usr/bin/env python3
"""
Smart Workflow Integrator - AI-Powered Workflow Enhancement
Integrates AI dependency resolution into existing workflows
"""

import os
import sys
import json
import yaml
import asyncio
from pathlib import Path
from typing import Dict, List, Any

# Import our AI agent fallback system
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ai_agent_fallback import ai_agent

class SmartWorkflowIntegrator:
    """AI-powered workflow integration and enhancement"""
    
    def __init__(self):
        self.workflow_dir = Path(".github/workflows")
        self.scripts_dir = Path(".github/scripts")
        
    async def analyze_workflow_issues(self, workflow_file: str) -> Dict[str, Any]:
        """Analyze workflow for potential issues using AI"""
        print(f"🔍 Analyzing workflow: {workflow_file}")
        
        try:
            with open(workflow_file, 'r') as f:
                workflow_content = yaml.safe_load(f)
        except Exception as e:
            return {"error": f"Failed to parse workflow: {e}"}
        
        # Create analysis prompt
        prompt = f"""
As an expert GitHub Actions and DevOps engineer, analyze this workflow file for potential issues and improvements.

## Workflow Content:
```yaml
{workflow_content}
```

## Analysis Tasks:
1. **Identify potential dependency issues** (missing packages, version conflicts)
2. **Find error-prone steps** (commands that might fail)
3. **Suggest resilience improvements** (retry logic, fallbacks)
4. **Recommend AI integration points** (where to add auto-repair)
5. **Propose workflow optimizations** (parallel jobs, caching, etc.)

## Response Format:
Provide your analysis in this JSON format:
```json
{{
  "workflow_name": "{workflow_file}",
  "issues_found": [
    {{
      "type": "dependency|command|resilience|optimization",
      "severity": "high|medium|low",
      "description": "Issue description",
      "location": "job.step",
      "suggestion": "How to fix"
    }}
  ],
  "ai_integration_points": [
    {{
      "step_name": "Step to enhance",
      "integration_type": "auto-repair|dependency-resolver|error-handler",
      "suggestion": "How to integrate AI"
    }}
  ],
  "optimization_suggestions": [
    "Suggestion 1",
    "Suggestion 2"
  ],
  "confidence": 0.95
}}
```

Focus on actionable improvements that will make this workflow more reliable and intelligent.
"""
        
        try:
            result = await ai_agent.analyze_with_fallback(prompt, "workflow_analysis")
            
            if result.get('success'):
                print(f"✅ Workflow analysis completed using {result.get('provider_used')}")
                return {
                    "success": True,
                    "provider_used": result.get('provider_used'),
                    "analysis": result.get('content', ''),
                    "raw_response": result.get('content', '')
                }
            else:
                return {
                    "success": False,
                    "error": result.get('error', 'AI analysis failed')
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Exception during analysis: {e}"
            }
    
    def enhance_workflow_with_ai(self, workflow_file: str, analysis: Dict[str, Any]) -> bool:
        """Enhance workflow file with AI suggestions"""
        print(f"🔧 Enhancing workflow: {workflow_file}")
        
        try:
            with open(workflow_file, 'r') as f:
                content = f.read()
            
            # Add AI dependency resolver step if not present
            if "AI Dependency Auto-Repair" not in content:
                # Find a good place to insert the AI repair step
                if "pip install" in content:
                    # Insert after pip install steps
                    lines = content.split('\n')
                    new_lines = []
                    in_pip_section = False
                    
                    for i, line in enumerate(lines):
                        new_lines.append(line)
                        
                        if "pip install" in line and not in_pip_section:
                            in_pip_section = True
                        elif in_pip_section and not line.strip().startswith('-') and not line.strip().startswith(' ') and line.strip():
                            # End of pip section, insert AI repair step
                            new_lines.insert(-1, "")
                            new_lines.insert(-1, "      - name: 🤖 AI Dependency Auto-Repair")
                            new_lines.insert(-1, "        if: failure()")
                            new_lines.insert(-1, "        run: |")
                            new_lines.insert(-1, "          echo \"🚀 Running AI Dependency Resolver for auto-repair...\"")
                            new_lines.insert(-1, "          python .github/scripts/ai_dependency_resolver.py || echo \"AI resolver completed with warnings\"")
                            new_lines.insert(-1, "")
                            in_pip_section = False
                    
                    content = '\n'.join(new_lines)
            
            # Add AI dependency resolver to environment variables if not present
            if "CEREBRAS_API_KEY" not in content:
                # Find env section and add AI provider keys
                env_section = """
env:
  # AI Provider API Keys for auto-repair
  CEREBRAS_API_KEY: ${{ secrets.CEREBRAS_API_KEY }}
  CODESTRAL_API_KEY: ${{ secrets.CODESTRAL_API_KEY }}
  DEEPSEEK_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
  GEMINIAI_API_KEY: ${{ secrets.GEMINIAI_API_KEY }}
  GLM_API_KEY: ${{ secrets.GLM_API_KEY }}
  GPTOSS_API_KEY: ${{ secrets.GPTOSS_API_KEY }}
  GROK_API_KEY: ${{ secrets.GROK_API_KEY }}
  GROQAI_API_KEY: ${{ secrets.GROQAI_API_KEY }}
  KIMI_API_KEY: ${{ secrets.KIMI_API_KEY }}
  NVIDIA_API_KEY: ${{ secrets.NVIDIA_API_KEY }}
  QWEN_API_KEY: ${{ secrets.QWEN_API_KEY }}
  GEMINI2_API_KEY: ${{ secrets.GEMINI2_API_KEY }}
  GROQ2_API_KEY: ${{ secrets.GROQ2_API_KEY }}
  COHERE_API_KEY: ${{ secrets.COHERE_API_KEY }}
  CHUTES_API_KEY: ${{ secrets.CHUTES_API_KEY }}
  CLAUDE_API_KEY: ${{ secrets.CLAUDE_API_KEY }}
  GPT4_API_KEY: ${{ secrets.GPT4_API_KEY }}
"""
                
                # Insert env section after name
                if "name:" in content and "env:" not in content:
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if line.strip().startswith('name:'):
                            lines.insert(i + 1, env_section)
                            break
                    content = '\n'.join(lines)
            
            # Write enhanced workflow
            with open(workflow_file, 'w') as f:
                f.write(content)
            
            print(f"✅ Workflow enhanced: {workflow_file}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to enhance workflow: {e}")
            return False
    
    async def process_all_workflows(self) -> Dict[str, Any]:
        """Process all workflow files for AI integration"""
        print("🚀 Processing all workflows for AI integration...")
        
        results = {
            "processed_workflows": [],
            "enhanced_workflows": [],
            "failed_workflows": [],
            "total_processed": 0,
            "total_enhanced": 0
        }
        
        if not self.workflow_dir.exists():
            print(f"❌ Workflow directory not found: {self.workflow_dir}")
            return results
        
        workflow_files = list(self.workflow_dir.glob("*.yml")) + list(self.workflow_dir.glob("*.yaml"))
        
        for workflow_file in workflow_files:
            if workflow_file.name.startswith("ai-"):
                continue  # Skip AI workflows to avoid recursion
            
            print(f"\n📄 Processing: {workflow_file.name}")
            results["total_processed"] += 1
            
            try:
                # Analyze workflow
                analysis = await self.analyze_workflow_issues(str(workflow_file))
                results["processed_workflows"].append({
                    "file": workflow_file.name,
                    "analysis": analysis
                })
                
                # Enhance workflow if analysis was successful
                if analysis.get("success"):
                    enhanced = self.enhance_workflow_with_ai(str(workflow_file), analysis)
                    if enhanced:
                        results["enhanced_workflows"].append(workflow_file.name)
                        results["total_enhanced"] += 1
                    else:
                        results["failed_workflows"].append({
                            "file": workflow_file.name,
                            "reason": "Enhancement failed"
                        })
                else:
                    results["failed_workflows"].append({
                        "file": workflow_file.name,
                        "reason": f"Analysis failed: {analysis.get('error', 'Unknown error')}"
                    })
                    
            except Exception as e:
                results["failed_workflows"].append({
                    "file": workflow_file.name,
                    "reason": f"Exception: {e}"
                })
        
        return results

async def main():
    """Main function to run smart workflow integration"""
    print("🚀 Starting Smart Workflow Integrator...")
    print("=" * 60)
    
    integrator = SmartWorkflowIntegrator()
    
    try:
        # Process all workflows
        results = await integrator.process_all_workflows()
        
        # Save results
        os.makedirs("artifacts", exist_ok=True)
        with open("artifacts/workflow_integration_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        # Print summary
        print("\n" + "=" * 60)
        print("🎉 SMART WORKFLOW INTEGRATION COMPLETE!")
        print("=" * 60)
        print(f"📊 Total Workflows Processed: {results['total_processed']}")
        print(f"✅ Successfully Enhanced: {results['total_enhanced']}")
        print(f"❌ Failed: {len(results['failed_workflows'])}")
        
        if results["enhanced_workflows"]:
            print(f"\n🔧 Enhanced Workflows:")
            for workflow in results["enhanced_workflows"]:
                print(f"  ✅ {workflow}")
        
        if results["failed_workflows"]:
            print(f"\n❌ Failed Workflows:")
            for failure in results["failed_workflows"]:
                print(f"  ❌ {failure['file']}: {failure['reason']}")
        
        print(f"\n📄 Results saved to: artifacts/workflow_integration_results.json")
        
        return results
        
    except Exception as e:
        print(f"❌ Critical error in workflow integrator: {e}")
        import traceback
        print(f"🔍 Traceback: {traceback.format_exc()}")
        return {"error": str(e)}

if __name__ == "__main__":
    asyncio.run(main())
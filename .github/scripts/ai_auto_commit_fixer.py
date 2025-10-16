#!/usr/bin/env python3
"""
AI Auto-Commit Fixer - Automatically commits AI-suggested fixes
Creates a bot branch and commits dependency/code fixes automatically
"""

import os
import sys
import json
import subprocess
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import our AI agent fallback system with error handling
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Try to import AI agent, install dependencies if needed
try:
    from ai_agent_fallback import ai_agent
except ImportError as e:
    print(f"⚠️ AI agent import failed: {e}")
    print("Installing required dependencies...")
    
    # Install required dependencies
    import subprocess
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "aiohttp", "openai", "cohere", "python-dotenv"], check=True)
        from ai_agent_fallback import ai_agent
        print("✅ Dependencies installed and AI agent loaded")
    except Exception as install_error:
        print(f"❌ Failed to install dependencies: {install_error}")
        # Create a mock AI agent for fallback
        class MockAIAgent:
            async def analyze_with_fallback(self, prompt, task_type="analysis"):
                return {
                    'success': False,
                    'error': 'AI agent not available - dependencies not installed',
                    'content': 'Mock analysis: Please install dependencies manually'
                }
        ai_agent = MockAIAgent()

class AIAutoCommitFixer:
    """AI-powered automatic commit and fix application"""
    
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.pr_number = os.getenv('GITHUB_PR_NUMBER', '')
        self.branch_name = f"ai-auto-fix-{self.pr_number}-{int(datetime.now().timestamp())}"
        self.fixes_applied = []
        self.commits_created = []
        
    async def analyze_and_fix(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze AI suggestions and apply fixes automatically"""
        print("🤖 Analyzing AI suggestions for automatic fixes...")
        
        if not analysis_data.get('ai_analysis'):
            return {"success": False, "error": "No AI analysis available"}
        
        ai_analysis = analysis_data['ai_analysis']
        fixes_to_apply = []
        
        # Extract pip commands for automatic application
        pip_commands = ai_analysis.get('pip_commands', [])
        for cmd in pip_commands[:5]:  # Limit to 5 commands
            fixes_to_apply.append({
                "type": "pip_install",
                "command": cmd,
                "description": f"Install dependency: {cmd}"
            })
        
        # Extract requirements.txt updates
        requirements_content = ai_analysis.get('requirements_txt', '')
        if requirements_content.strip():
            fixes_to_apply.append({
                "type": "requirements_update",
                "content": requirements_content,
                "description": "Update requirements.txt with AI suggestions"
            })
        
        # Extract code patches
        code_patches = ai_analysis.get('code_patches', [])
        for i, patch in enumerate(code_patches[:3]):  # Limit to 3 patches
            fixes_to_apply.append({
                "type": "code_patch",
                "content": patch,
                "description": f"Apply code patch {i+1}"
            })
        
        return {
            "success": True,
            "fixes_to_apply": fixes_to_apply,
            "total_fixes": len(fixes_to_apply)
        }
    
    async def create_bot_branch(self) -> bool:
        """Create a new branch for AI fixes"""
        try:
            print(f"🌿 Creating bot branch: {self.branch_name}")
            
            # Create and checkout new branch
            subprocess.run(['git', 'checkout', '-b', self.branch_name], check=True)
            print(f"✅ Created branch: {self.branch_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create branch: {e}")
            return False
    
    async def apply_fixes(self, fixes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply AI-suggested fixes automatically"""
        print(f"🔧 Applying {len(fixes)} AI-suggested fixes...")
        
        applied_fixes = []
        failed_fixes = []
        
        for fix in fixes:
            try:
                if fix['type'] == 'pip_install':
                    # Apply pip install command
                    cmd = fix['command'].split()
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                    
                    if result.returncode == 0:
                        applied_fixes.append(fix)
                        print(f"✅ Applied: {fix['description']}")
                    else:
                        failed_fixes.append({**fix, 'error': result.stderr})
                        print(f"❌ Failed: {fix['description']} - {result.stderr}")
                
                elif fix['type'] == 'requirements_update':
                    # Update requirements.txt
                    with open('requirements.txt', 'w') as f:
                        f.write(fix['content'])
                    applied_fixes.append(fix)
                    print(f"✅ Updated: {fix['description']}")
                
                elif fix['type'] == 'code_patch':
                    # Apply code patch (simplified - would need more sophisticated patching)
                    patch_file = f"ai_patch_{len(applied_fixes)}.patch"
                    with open(patch_file, 'w') as f:
                        f.write(fix['content'])
                    applied_fixes.append(fix)
                    print(f"✅ Created: {fix['description']}")
                
            except Exception as e:
                failed_fixes.append({**fix, 'error': str(e)})
                print(f"❌ Exception: {fix['description']} - {e}")
        
        return {
            "applied_fixes": applied_fixes,
            "failed_fixes": failed_fixes,
            "total_applied": len(applied_fixes),
            "total_failed": len(failed_fixes)
        }
    
    async def commit_changes(self, fix_results: Dict[str, Any]) -> bool:
        """Commit the applied fixes"""
        try:
            print("📝 Committing AI-applied fixes...")
            
            # Add all changes
            subprocess.run(['git', 'add', '.'], check=True)
            
            # Create commit message
            commit_message = f"""🤖 AI Auto-Fix: Applied {fix_results['total_applied']} fixes

✅ Applied Fixes:
{chr(10).join([f"- {fix['description']}" for fix in fix_results['applied_fixes']])}

❌ Failed Fixes:
{chr(10).join([f"- {fix['description']}: {fix.get('error', 'Unknown error')}" for fix in fix_results['failed_fixes']])}

🤖 Generated by AI Auto-Commit Fixer
Provider: {os.getenv('AI_PROVIDER_USED', 'Unknown')}
Timestamp: {datetime.now().isoformat()}
"""
            
            # Commit changes
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            print("✅ Changes committed successfully")
            
            # Push branch
            subprocess.run(['git', 'push', 'origin', self.branch_name], check=True)
            print(f"🚀 Pushed branch: {self.branch_name}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to commit changes: {e}")
            return False
    
    async def create_pull_request(self, fix_results: Dict[str, Any]) -> Optional[str]:
        """Create a pull request for the AI fixes"""
        try:
            print("🔀 Creating pull request for AI fixes...")
            
            pr_title = f"🤖 AI Auto-Fix: {fix_results['total_applied']} fixes applied"
            pr_body = f"""## 🤖 AI-Generated Fixes

This PR contains automatically generated fixes based on AI analysis.

### 📊 Fix Summary
- **Total Fixes Applied:** {fix_results['total_applied']}
- **Failed Fixes:** {fix_results['total_failed']}
- **AI Provider:** {os.getenv('AI_PROVIDER_USED', 'Unknown')}
- **Generated:** {datetime.now().isoformat()}

### ✅ Applied Fixes
{chr(10).join([f"- {fix['description']}" for fix in fix_results['applied_fixes']])}

### ❌ Failed Fixes
{chr(10).join([f"- {fix['description']}: {fix.get('error', 'Unknown error')}" for fix in fix_results['failed_fixes']])}

### 🔍 Review Required
Please review these AI-generated fixes before merging.

---
*Generated by AI Auto-Commit Fixer*
"""
            
            # Use GitHub CLI to create PR
            cmd = [
                'gh', 'pr', 'create',
                '--title', pr_title,
                '--body', pr_body,
                '--head', self.branch_name,
                '--base', 'main'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                pr_url = result.stdout.strip()
                print(f"✅ Created PR: {pr_url}")
                return pr_url
            else:
                print(f"❌ Failed to create PR: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ Exception creating PR: {e}")
            return None
    
    async def run_auto_fix(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main function to run automatic fixing"""
        print("🚀 Starting AI Auto-Commit Fixer...")
        print("=" * 60)
        
        try:
            # Step 1: Analyze AI suggestions
            analysis_result = await self.analyze_and_fix(analysis_data)
            if not analysis_result['success']:
                return {"success": False, "error": analysis_result['error']}
            
            # Step 2: Create bot branch
            if not await self.create_bot_branch():
                return {"success": False, "error": "Failed to create bot branch"}
            
            # Step 3: Apply fixes
            fix_results = await self.apply_fixes(analysis_result['fixes_to_apply'])
            
            # Step 4: Commit changes
            if fix_results['total_applied'] > 0:
                if not await self.commit_changes(fix_results):
                    return {"success": False, "error": "Failed to commit changes"}
                
                # Step 5: Create PR (optional)
                pr_url = await self.create_pull_request(fix_results)
                
                return {
                    "success": True,
                    "branch_name": self.branch_name,
                    "pr_url": pr_url,
                    "fixes_applied": fix_results['total_applied'],
                    "fixes_failed": fix_results['total_failed']
                }
            else:
                return {
                    "success": True,
                    "message": "No fixes to apply",
                    "fixes_applied": 0,
                    "fixes_failed": fix_results['total_failed']
                }
                
        except Exception as e:
            print(f"❌ Critical error in auto-fixer: {e}")
            return {"success": False, "error": str(e)}

async def main():
    """Main function to run AI auto-commit fixer"""
    print("🤖 AI Auto-Commit Fixer Starting...")
    
    # Check if we have analysis data
    analysis_file = "artifacts/dependency_resolution.json"
    if not os.path.exists(analysis_file):
        print("❌ No analysis data found. Run AI dependency resolver first.")
        return
    
    # Load analysis data
    with open(analysis_file, 'r') as f:
        analysis_data = json.load(f)
    
    # Run auto-fixer
    fixer = AIAutoCommitFixer()
    result = await fixer.run_auto_fix(analysis_data)
    
    # Save results
    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/auto_fix_results.json", "w") as f:
        json.dump(result, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 60)
    print("🎉 AI AUTO-COMMIT FIXER COMPLETE!")
    print("=" * 60)
    print(f"📊 Success: {result['success']}")
    if result.get('branch_name'):
        print(f"🌿 Branch: {result['branch_name']}")
    if result.get('pr_url'):
        print(f"🔀 PR: {result['pr_url']}")
    print(f"🔧 Fixes Applied: {result.get('fixes_applied', 0)}")
    print(f"❌ Fixes Failed: {result.get('fixes_failed', 0)}")
    
    return result

if __name__ == "__main__":
    asyncio.run(main())
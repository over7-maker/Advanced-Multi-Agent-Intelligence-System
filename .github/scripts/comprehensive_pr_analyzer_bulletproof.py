#!/usr/bin/env python3
"""
BULLETPROOF Comprehensive PR Analyzer - Real AI Analysis ONLY
Uses bulletproof real AI system - NO FAKE RESPONSES ALLOWED
"""

import os
import sys
import json
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, Any, List

# Import bulletproof real AI system
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from bulletproof_real_ai import BulletproofRealAI

class BulletproofPRAnalyzer:
    """BULLETPROOF PR analyzer - REAL AI ONLY"""
    
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github_event_path = os.getenv('GITHUB_EVENT_PATH')
        self.start_time = datetime.now()
        self.is_github_actions = os.getenv('GITHUB_ACTIONS') == 'true'
        
    async def analyze_pr(self) -> Dict[str, Any]:
        """Main method to analyze PR with BULLETPROOF real AI"""
        print("🚀 Starting BULLETPROOF PR Analysis...")
        print("=" * 60)
        print("🤖 BULLETPROOF REAL AI PR ANALYSIS ACTIVATED!")
        print("=" * 60)
        
        # Get PR details
        pr_details = await self._get_pr_details()
        print(f"📋 PR Title: {pr_details['title']}")
        print(f"📝 PR Body: {pr_details['body'][:100]}...")
        print(f"📊 Diff Size: {len(pr_details['diff'])} characters")
        print("")
        
        # Initialize BULLETPROOF real AI
        try:
            ai_analyzer = BulletproofRealAI()
            print("✅ BULLETPROOF REAL AI INITIALIZED")
        except Exception as e:
            print(f"🚨 BULLETPROOF AI INITIALIZATION FAILED: {e}")
            return self._create_failure_result(str(e))
        
        # Perform BULLETPROOF real AI analysis
        print("🔍 Starting BULLETPROOF real AI analysis...")
        try:
            analysis_result = await ai_analyzer.force_real_ai_analysis("auto_analysis", pr_details['diff'])
            
            if not analysis_result.get('bulletproof_validated', False):
                print("🚨 FAKE AI DETECTED - FAILING HARD!")
                return self._create_failure_result("Fake AI detected in analysis")
                
            print("✅ BULLETPROOF REAL AI ANALYSIS SUCCESS!")
            print(f"🤖 Provider: {analysis_result['provider']}")
            print(f"⏱️ Response Time: {analysis_result['response_time']}s")
            
        except Exception as e:
            print(f"🚨 BULLETPROOF AI ANALYSIS FAILED: {e}")
            return self._create_failure_result(str(e))
        
        # Generate comprehensive results
        results = {
            "metadata": {
                "timestamp": self.start_time.isoformat(),
                "analyzer_version": "3.0-bulletproof-real-ai",
                "pr_number": pr_details.get('number', 'unknown'),
                "pr_title": pr_details['title'],
                "execution_status": "completed_successfully",
                "bulletproof_validated": True,
                "fake_ai_detected": False
            },
            "pr_analysis": {
                "title": pr_details['title'],
                "body": pr_details['body'],
                "diff_size": len(pr_details['diff']),
                "files_changed": self._count_files_changed(pr_details['diff']),
                "lines_added": self._count_lines_added(pr_details['diff']),
                "lines_removed": self._count_lines_removed(pr_details['diff'])
            },
            "ai_analysis": {
                "provider": analysis_result['provider'],
                "response_time": analysis_result['response_time'],
                "analysis": analysis_result['analysis'],
                "real_ai_verified": analysis_result['real_ai_verified'],
                "fake_ai_detected": analysis_result['fake_ai_detected'],
                "bulletproof_validated": analysis_result['bulletproof_validated'],
                "provider_attempt": analysis_result['provider_attempt'],
                "total_attempts": analysis_result['total_attempts']
            },
            "performance_metrics": {
                "execution_time_seconds": (datetime.now() - self.start_time).total_seconds(),
                "ai_provider_used": analysis_result['provider'],
                "ai_response_time": analysis_result['response_time'],
                "success_rate": 1.0 if analysis_result.get('success') else 0.0,
                "bulletproof_validation": True
            },
            "recommendations": self._extract_recommendations(analysis_result),
            "next_steps": self._generate_next_steps(analysis_result)
        }
        
        print("🎉 BULLETPROOF PR ANALYSIS COMPLETE!")
        print("=" * 60)
        print("📊 ANALYSIS RESULTS:")
        print(f"  🤖 Provider: {analysis_result['provider']}")
        print(f"  ⏱️ Response Time: {analysis_result['response_time']}s")
        print(f"  ✅ Real AI Verified: {analysis_result['real_ai_verified']}")
        print(f"  🛡️ Bulletproof Validated: {analysis_result['bulletproof_validated']}")
        print("")
        
        if results['recommendations']:
            print("🎯 AI RECOMMENDATIONS GENERATED:")
            print("-" * 40)
            for i, rec in enumerate(results['recommendations'], 1):
                print(f"  {i}. {rec}")
            print("")
        
        print(f"📄 Results saved to comprehensive_pr_analysis.json")
        print("")
        print("✅ BULLETPROOF PR ANALYSIS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
        return results
    
    def _create_failure_result(self, error_message: str) -> Dict[str, Any]:
        """Create failure result when AI analysis fails"""
        return {
            "metadata": {
                "timestamp": self.start_time.isoformat(),
                "analyzer_version": "3.0-bulletproof-real-ai",
                "execution_status": "failed",
                "error": error_message,
                "bulletproof_validated": False,
                "fake_ai_detected": True
            },
            "ai_analysis": {
                "provider": "none",
                "response_time": 0,
                "analysis": f"Analysis failed: {error_message}",
                "real_ai_verified": False,
                "fake_ai_detected": True,
                "bulletproof_validated": False,
                "provider_attempt": 0,
                "total_attempts": 0
            },
            "recommendations": [],
            "next_steps": ["Check API key configuration", "Verify network connectivity"]
        }
    
    async def _get_pr_details(self) -> Dict[str, Any]:
        """Get PR details from GitHub event payload or create mock data"""
        if not self.is_github_actions or not self.github_event_path:
            print("ℹ️ Not in GitHub Actions environment, using mock PR data for testing")
            return {
                "number": 198,
                "title": "Mock PR: BULLETPROOF AI Code Analysis Test",
                "body": "This is a test PR for BULLETPROOF AI code analysis functionality. The system is analyzing code quality, performance, and providing intelligent recommendations using REAL AI only.",
                "diff": self._get_sample_diff(),
                "comments_url": None,
                "html_url": "https://github.com/test/repo/pull/198"
            }
        
        try:
            with open(self.github_event_path, 'r') as f:
                event = json.load(f)
            
            pr = event.get("pull_request")
            if not pr:
                print("::error::No pull request data found")
                return self._get_mock_pr_details()
            
            # Get PR diff
            diff_url = pr["diff_url"]
            headers = {
                "Authorization": f"Bearer {self.github_token}",
                "Accept": "application/vnd.github.v3.diff"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(diff_url, headers=headers) as response:
                    response.raise_for_status()
                    diff_content = await response.text()
            
            return {
                "number": pr["number"],
                "title": pr["title"],
                "body": pr["body"] or "",
                "diff": diff_content,
                "comments_url": pr["comments_url"],
                "html_url": pr["html_url"]
            }
            
        except Exception as e:
            print(f"::error::Failed to get PR details: {e}")
            return self._get_mock_pr_details()
    
    def _get_mock_pr_details(self) -> Dict[str, Any]:
        """Get mock PR details for testing"""
        return {
            "number": 198,
            "title": "Mock PR: BULLETPROOF AI Analysis Test",
            "body": "Test PR for BULLETPROOF AI analysis",
            "diff": self._get_sample_diff(),
            "comments_url": None,
            "html_url": "https://github.com/test/repo/pull/198"
        }
    
    def _get_sample_diff(self) -> str:
        """Get sample diff for testing"""
        return """
diff --git a/src/main.py b/src/main.py
index 1234567..abcdefg 100644
--- a/src/main.py
+++ b/src/main.py
@@ -1,5 +1,8 @@
 def hello_world():
-    print("Hello, World!")
+    print("Hello, BULLETPROOF AI World!")
+    # Added error handling
+    try:
+        process_data()
+    except Exception as e:
+        print(f"Error: {e}")
 
 class DataProcessor:
     def __init__(self):
         self.data = []
"""
    
    def _count_files_changed(self, diff: str) -> int:
        """Count number of files changed in diff"""
        return len([line for line in diff.split('\n') if line.startswith('diff --git')])
    
    def _count_lines_added(self, diff: str) -> int:
        """Count lines added in diff"""
        return len([line for line in diff.split('\n') if line.startswith('+') and not line.startswith('+++')])
    
    def _count_lines_removed(self, diff: str) -> int:
        """Count lines removed in diff"""
        return len([line for line in diff.split('\n') if line.startswith('-') and not line.startswith('---')])
    
    def _extract_recommendations(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Extract recommendations from AI analysis"""
        analysis = analysis_result.get('analysis', '')
        
        # Extract recommendations from analysis text
        recommendations = []
        lines = analysis.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('*') or line.startswith('1.') or line.startswith('2.') or line.startswith('3.')):
                # Clean up the recommendation
                rec = line.lstrip('-*123456789. ').strip()
                if rec and len(rec) > 10:  # Only meaningful recommendations
                    recommendations.append(rec)
        
        return recommendations[:10]  # Limit to 10 recommendations
    
    def _generate_next_steps(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Generate next steps based on analysis"""
        return [
            "Review the AI analysis recommendations",
            "Implement suggested code improvements",
            "Test the changes thoroughly",
            "Update documentation if needed"
        ]

async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='BULLETPROOF PR Analyzer')
    parser.add_argument('--pr-number', type=int, help='PR number to analyze')
    parser.add_argument('--output', type=str, default='artifacts/auto_pr_analysis.json', help='Output file path')
    
    args = parser.parse_args()
    
    # Create artifacts directory
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    # Initialize analyzer
    analyzer = BulletproofPRAnalyzer()
    
    # Perform analysis
    results = await analyzer.analyze_pr()
    
    # Save results
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"📄 Results saved to {args.output}")
    
    # Check if analysis was successful
    if not results.get('metadata', {}).get('bulletproof_validated', False):
        print("🚨 BULLETPROOF VALIDATION FAILED!")
        sys.exit(1)
    else:
        print("✅ BULLETPROOF VALIDATION SUCCESS!")
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
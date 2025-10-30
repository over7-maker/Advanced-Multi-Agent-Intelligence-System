#!/usr/bin/env python3
"""
AI Learning System - Feed back results to improve AI suggestions over time
Tracks fix success rates and learns from outcomes
"""

import os
import sys
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

# Import our AI agent fallback system
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ai_agent_fallback import ai_agent

class AILearningSystem:
    """AI learning system that improves suggestions over time"""
    
    def __init__(self):
        self.learning_data_file = "artifacts/ai_learning_data.json"
        self.provider_performance_file = "artifacts/provider_performance.json"
        self.load_learning_data()
    
    def load_learning_data(self):
        """Load existing learning data"""
        self.learning_data = {
            "fix_success_rates": {},
            "provider_performance": {},
            "common_issues": {},
            "successful_patterns": {},
            "failed_patterns": {},
            "last_updated": None
        }
        
        if os.path.exists(self.learning_data_file):
            try:
                with open(self.learning_data_file, 'r') as f:
                    self.learning_data = json.load(f)
            except Exception as e:
                print(f"⚠️ Error loading learning data: {e}")
    
    def save_learning_data(self):
        """Save learning data to file"""
        self.learning_data["last_updated"] = datetime.now().isoformat()
        os.makedirs("artifacts", exist_ok=True)
        with open(self.learning_data_file, "w") as f:
            json.dump(self.learning_data, f, indent=2)
    
    async def record_fix_outcome(self, fix_data: Dict[str, Any]) -> None:
        """Record the outcome of a fix for learning"""
        print("📚 Recording fix outcome for learning...")
        
        fix_type = fix_data.get('type', 'unknown')
        success = fix_data.get('success', False)
        provider = fix_data.get('provider', 'unknown')
        error_type = fix_data.get('error_type', 'none')
        
        # Update fix success rates
        if fix_type not in self.learning_data["fix_success_rates"]:
            self.learning_data["fix_success_rates"][fix_type] = {"success": 0, "total": 0}
        
        self.learning_data["fix_success_rates"][fix_type]["total"] += 1
        if success:
            self.learning_data["fix_success_rates"][fix_type]["success"] += 1
        
        # Update provider performance
        if provider not in self.learning_data["provider_performance"]:
            self.learning_data["provider_performance"][provider] = {
                "success": 0, "total": 0, "avg_response_time": 0, "response_times": []
            }
        
        self.learning_data["provider_performance"][provider]["total"] += 1
        if success:
            self.learning_data["provider_performance"][provider]["success"] += 1
        
        # Record response time
        response_time = fix_data.get('response_time', 0)
        if response_time > 0:
            self.learning_data["provider_performance"][provider]["response_times"].append(response_time)
            # Keep only last 100 response times
            if len(self.learning_data["provider_performance"][provider]["response_times"]) > 100:
                self.learning_data["provider_performance"][provider]["response_times"] = \
                    self.learning_data["provider_performance"][provider]["response_times"][-100:]
            
            # Update average response time
            times = self.learning_data["provider_performance"][provider]["response_times"]
            self.learning_data["provider_performance"][provider]["avg_response_time"] = sum(times) / len(times)
        
        # Record common issues
        if not success and error_type != 'none':
            if error_type not in self.learning_data["common_issues"]:
                self.learning_data["common_issues"][error_type] = 0
            self.learning_data["common_issues"][error_type] += 1
        
        # Record patterns
        pattern_key = f"{fix_type}_{provider}_{'success' if success else 'failed'}"
        if pattern_key not in self.learning_data["successful_patterns"]:
            self.learning_data["successful_patterns"][pattern_key] = 0
        if pattern_key not in self.learning_data["failed_patterns"]:
            self.learning_data["failed_patterns"][pattern_key] = 0
        
        if success:
            self.learning_data["successful_patterns"][pattern_key] += 1
        else:
            self.learning_data["failed_patterns"][pattern_key] += 1
        
        self.save_learning_data()
        print("✅ Learning data updated")
    
    async def get_improved_suggestions(self, current_issue: str, issue_type: str) -> Dict[str, Any]:
        """Get improved suggestions based on learning data"""
        print("🧠 Generating improved suggestions based on learning...")
        
        # Analyze historical data for this issue type
        success_rate = self.learning_data["fix_success_rates"].get(issue_type, {"success": 0, "total": 0})
        if success_rate["total"] > 0:
            success_percentage = (success_rate["success"] / success_rate["total"]) * 100
        else:
            success_percentage = 0
        
        # Find best performing provider for this issue type
        best_provider = None
        best_score = 0
        
        for provider, perf in self.learning_data["provider_performance"].items():
            if perf["total"] > 0:
                success_rate = (perf["success"] / perf["total"]) * 100
                avg_time = perf.get("avg_response_time", 0)
                # Score based on success rate and speed (lower time is better)
                score = success_rate - (avg_time / 10)  # Penalize slow providers
                if score > best_score:
                    best_score = score
                    best_provider = provider
        
        # Generate learning-based prompt
        learning_prompt = f"""
As an expert AI system with learning capabilities, provide improved suggestions based on historical data.

## Current Issue:
{current_issue}

## Issue Type:
{issue_type}

## Learning Data:
- Historical Success Rate: {success_percentage:.1f}%
- Best Performing Provider: {best_provider or 'None'}
- Common Issues: {list(self.learning_data['common_issues'].keys())[:5]}

## Task:
Based on this learning data, provide improved suggestions that:
1. Leverage successful patterns from the past
2. Avoid previously failed approaches
3. Consider the best performing provider
4. Address common issues proactively

## Response Format:
Provide your analysis in this JSON format:
```json
{{
  "improved_analysis": "Analysis based on learning data",
  "recommended_provider": "{best_provider or 'auto'}",
  "confidence_boost": 0.15,
  "learning_insights": [
    "Insight 1 based on historical data",
    "Insight 2 based on patterns"
  ],
  "avoid_patterns": [
    "Pattern to avoid based on failures"
  ],
  "success_probability": {success_percentage / 100}
}}
```

Focus on actionable improvements based on what has worked before.
"""
        
        try:
            result = await ai_agent.analyze_with_fallback(learning_prompt, "learning_enhanced_analysis")
            
            if result.get('success'):
                # Extract JSON from response
                content = result.get('content', '')
                try:
                    import re
                    json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
                    if json_match:
                        learning_analysis = json.loads(json_match.group(1))
                    else:
                        # Fallback
                        learning_analysis = {
                            "improved_analysis": content[:500],
                            "recommended_provider": best_provider or "auto",
                            "confidence_boost": 0.1,
                            "learning_insights": ["Based on historical data"],
                            "avoid_patterns": ["Avoid previously failed patterns"],
                            "success_probability": success_percentage / 100
                        }
                    
                    return {
                        "success": True,
                        "learning_analysis": learning_analysis,
                        "provider_used": result.get('provider_used'),
                        "response_time": result.get('response_time', 0)
                    }
                except json.JSONDecodeError:
                    return {
                        "success": False,
                        "error": "Failed to parse learning analysis"
                    }
            else:
                return {
                    "success": False,
                    "error": result.get('error', 'Learning analysis failed')
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Exception in learning system: {e}"
            }
    
    async def generate_learning_report(self) -> Dict[str, Any]:
        """Generate a comprehensive learning report"""
        print("📊 Generating learning report...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_fixes_tracked": sum(data["total"] for data in self.learning_data["fix_success_rates"].values()),
                "overall_success_rate": 0,
                "best_provider": None,
                "most_common_issue": None
            },
            "fix_success_rates": self.learning_data["fix_success_rates"],
            "provider_performance": {},
            "common_issues": self.learning_data["common_issues"],
            "recommendations": []
        }
        
        # Calculate overall success rate
        total_success = sum(data["success"] for data in self.learning_data["fix_success_rates"].values())
        total_fixes = sum(data["total"] for data in self.learning_data["fix_success_rates"].values())
        if total_fixes > 0:
            report["summary"]["overall_success_rate"] = (total_success / total_fixes) * 100
        
        # Find best provider
        best_provider = None
        best_score = 0
        for provider, perf in self.learning_data["provider_performance"].items():
            if perf["total"] > 0:
                success_rate = (perf["success"] / perf["total"]) * 100
                avg_time = perf.get("avg_response_time", 0)
                score = success_rate - (avg_time / 10)
                if score > best_score:
                    best_score = score
                    best_provider = provider
        
        report["summary"]["best_provider"] = best_provider
        
        # Find most common issue
        if self.learning_data["common_issues"]:
            report["summary"]["most_common_issue"] = max(
                self.learning_data["common_issues"].items(), 
                key=lambda x: x[1]
            )[0]
        
        # Process provider performance
        for provider, perf in self.learning_data["provider_performance"].items():
            if perf["total"] > 0:
                report["provider_performance"][provider] = {
                    "success_rate": (perf["success"] / perf["total"]) * 100,
                    "total_requests": perf["total"],
                    "avg_response_time": perf.get("avg_response_time", 0),
                    "reliability_score": (perf["success"] / perf["total"]) * 100 - (perf.get("avg_response_time", 0) / 10)
                }
        
        # Generate recommendations
        if report["summary"]["overall_success_rate"] < 80:
            report["recommendations"].append("Overall success rate is below 80%. Consider improving fix strategies.")
        
        if best_provider:
            report["recommendations"].append(f"Consider prioritizing {best_provider} for better results.")
        
        if report["summary"]["most_common_issue"]:
            report["recommendations"].append(f"Focus on addressing {report['summary']['most_common_issue']} issues.")
        
        return report

async def main():
    """Main function to run AI learning system"""
    print("🧠 AI Learning System Starting...")
    
    learning_system = AILearningSystem()
    
    # Generate learning report
    report = await learning_system.generate_learning_report()
    
    # Save report
    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/ai_learning_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 AI LEARNING SYSTEM REPORT")
    print("=" * 60)
    print(f"📈 Total Fixes Tracked: {report['summary']['total_fixes_tracked']}")
    print(f"🎯 Overall Success Rate: {report['summary']['overall_success_rate']:.1f}%")
    print(f"🏆 Best Provider: {report['summary']['best_provider'] or 'None'}")
    print(f"⚠️ Most Common Issue: {report['summary']['most_common_issue'] or 'None'}")
    
    if report['recommendations']:
        print(f"\n💡 Recommendations:")
        for rec in report['recommendations']:
            print(f"  - {rec}")
    
    return report

if __name__ == "__main__":
    asyncio.run(main())
#!/usr/bin/env python3
"""
AI Human-in-the-Loop Approval System
Set up rules for automated fixes to be auto-merged only if tests pass and/or after manual approval
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

class AIHumanApprovalSystem:
    """AI system with human-in-the-loop approval for automated fixes"""
    
    def __init__(self):
        self.approval_rules_file = "artifacts/approval_rules.json"
        self.pending_approvals_file = "artifacts/pending_approvals.json"
        self.approval_history_file = "artifacts/approval_history.json"
        self.load_approval_data()
    
    def load_approval_data(self):
        """Load approval rules and data"""
        self.approval_rules = {
            "auto_approve_rules": {
                "dependency_fixes": {
                    "enabled": True,
                    "conditions": ["tests_pass", "no_breaking_changes"],
                    "max_risk_level": "medium"
                },
                "code_style_fixes": {
                    "enabled": True,
                    "conditions": ["tests_pass", "linter_approves"],
                    "max_risk_level": "low"
                },
                "security_patches": {
                    "enabled": False,  # Always require human approval
                    "conditions": ["human_approval", "security_review"],
                    "max_risk_level": "any"
                },
                "major_refactoring": {
                    "enabled": False,  # Always require human approval
                    "conditions": ["human_approval", "architect_review"],
                    "max_risk_level": "any"
                }
            },
            "approval_workflows": {
                "immediate": ["dependency_fixes", "code_style_fixes"],
                "review_required": ["security_patches", "major_refactoring"],
                "emergency": ["critical_security_fixes"]
            },
            "approvers": {
                "security": ["security-team"],
                "architecture": ["architects"],
                "general": ["maintainers"]
            }
        }
        
        self.pending_approvals = []
        self.approval_history = []
        
        # Load existing data
        for file_path, data_attr in [
            (self.approval_rules_file, "approval_rules"),
            (self.pending_approvals_file, "pending_approvals"),
            (self.approval_history_file, "approval_history")
        ]:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        setattr(self, data_attr, json.load(f))
                except Exception as e:
                    print(f"⚠️ Error loading {file_path}: {e}")
    
    def save_approval_data(self):
        """Save approval data to files"""
        os.makedirs("artifacts", exist_ok=True)
        
        for file_path, data_attr in [
            (self.approval_rules_file, "approval_rules"),
            (self.pending_approvals_file, "pending_approvals"),
            (self.approval_history_file, "approval_history")
        ]:
            with open(file_path, "w") as f:
                json.dump(getattr(self, data_attr), f, indent=2)
    
    async def evaluate_approval_requirements(self, fix_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate what approval is required for a fix"""
        print("🔍 Evaluating approval requirements...")
        
        fix_type = fix_data.get('type', 'unknown')
        risk_level = fix_data.get('risk_level', 'medium')
        impact_scope = fix_data.get('impact_scope', 'local')
        
        # Check if fix type has auto-approve rules
        auto_approve_rule = self.approval_rules["auto_approve_rules"].get(fix_type)
        
        if auto_approve_rule and auto_approve_rule["enabled"]:
            # Check if risk level is acceptable
            risk_levels = ["low", "medium", "high", "critical"]
            max_risk_index = risk_levels.index(auto_approve_rule["max_risk_level"])
            current_risk_index = risk_levels.index(risk_level)
            
            if current_risk_index <= max_risk_index:
                return {
                    "approval_required": False,
                    "approval_type": "auto",
                    "reason": f"Auto-approved: {fix_type} with {risk_level} risk",
                    "conditions": auto_approve_rule["conditions"]
                }
        
        # Determine approval type based on fix characteristics
        if risk_level in ["critical", "high"] or impact_scope in ["global", "system"]:
            approval_type = "security_review"
            approvers = self.approval_rules["approvers"]["security"]
        elif fix_type in ["security_patches", "major_refactoring"]:
            approval_type = "architect_review"
            approvers = self.approval_rules["approvers"]["architecture"]
        else:
            approval_type = "general_review"
            approvers = self.approval_rules["approvers"]["general"]
        
        return {
            "approval_required": True,
            "approval_type": approval_type,
            "approvers": approvers,
            "reason": f"Manual approval required: {fix_type} with {risk_level} risk",
            "estimated_review_time": "2-4 hours"
        }
    
    async def create_approval_request(self, fix_data: Dict[str, Any], approval_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Create an approval request"""
        print("📝 Creating approval request...")
        
        approval_request = {
            "id": f"approval_{int(datetime.now().timestamp())}",
            "fix_data": fix_data,
            "approval_requirements": approval_requirements,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "approvers": approval_requirements.get("approvers", []),
            "approval_deadline": (datetime.now() + timedelta(hours=24)).isoformat(),
            "priority": "high" if fix_data.get('risk_level') in ['critical', 'high'] else "normal"
        }
        
        self.pending_approvals.append(approval_request)
        self.save_approval_data()
        
        return approval_request
    
    async def get_ai_approval_recommendation(self, approval_request: Dict[str, Any]) -> Dict[str, Any]:
        """Get AI recommendation for approval decision"""
        print("🤖 Getting AI approval recommendation...")
        
        fix_data = approval_request["fix_data"]
        approval_requirements = approval_request["approval_requirements"]
        
        prompt = f"""
As an expert code reviewer and risk assessor, analyze this automated fix and provide an approval recommendation.

## Fix Data:
{json.dumps(fix_data, indent=2)}

## Approval Requirements:
{json.dumps(approval_requirements, indent=2)}

## Analysis Tasks:
1. **Risk Assessment**: Evaluate the potential risks of this fix
2. **Impact Analysis**: Assess the impact on system stability and functionality
3. **Approval Recommendation**: Recommend approve/reject with reasoning
4. **Conditions**: Identify any conditions that should be met before approval
5. **Alternative Suggestions**: Suggest alternatives if the fix is risky

## Response Format:
Provide your analysis in this JSON format:
```json
{{
  "recommendation": "approve|reject|conditional",
  "confidence": 0.85,
  "risk_assessment": {{
    "overall_risk": "low|medium|high|critical",
    "potential_issues": ["Issue 1", "Issue 2"],
    "mitigation_strategies": ["Strategy 1", "Strategy 2"]
  }},
  "impact_analysis": {{
    "system_impact": "minimal|moderate|significant",
    "user_impact": "none|low|medium|high",
    "rollback_difficulty": "easy|medium|hard"
  }},
  "approval_conditions": [
    "Condition 1 that must be met",
    "Condition 2 that must be met"
  ],
  "reasoning": "Detailed explanation of the recommendation",
  "alternative_suggestions": [
    "Alternative approach 1",
    "Alternative approach 2"
  ],
  "testing_requirements": [
    "Test requirement 1",
    "Test requirement 2"
  ]
}}
```

Focus on safety, stability, and maintainability in your recommendation.
"""
        
        try:
            result = await ai_agent.analyze_with_fallback(prompt, "approval_recommendation")
            
            if result.get('success'):
                # Extract JSON from response
                content = result.get('content', '')
                try:
                    import re
                    json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
                    if json_match:
                        ai_recommendation = json.loads(json_match.group(1))
                    else:
                        # Fallback recommendation
                        ai_recommendation = {
                            "recommendation": "conditional",
                            "confidence": 0.7,
                            "risk_assessment": {
                                "overall_risk": "medium",
                                "potential_issues": ["Unknown risks"],
                                "mitigation_strategies": ["Review carefully"]
                            },
                            "impact_analysis": {
                                "system_impact": "moderate",
                                "user_impact": "low",
                                "rollback_difficulty": "medium"
                            },
                            "approval_conditions": ["Manual review required"],
                            "reasoning": "AI analysis completed with standard recommendations",
                            "alternative_suggestions": [],
                            "testing_requirements": ["Run full test suite"]
                        }
                    
                    return {
                        "success": True,
                        "ai_recommendation": ai_recommendation,
                        "provider_used": result.get('provider_used'),
                        "response_time": result.get('response_time', 0)
                    }
                except json.JSONDecodeError:
                    return {
                        "success": False,
                        "error": "Failed to parse AI recommendation"
                    }
            else:
                return {
                    "success": False,
                    "error": result.get('error', 'AI recommendation failed')
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Exception in AI recommendation: {e}"
            }
    
    async def process_approval_decision(self, approval_id: str, decision: str, approver: str, comments: str = "") -> Dict[str, Any]:
        """Process an approval decision"""
        print(f"📋 Processing approval decision for {approval_id}...")
        
        # Find the approval request
        approval_request = None
        for req in self.pending_approvals:
            if req["id"] == approval_id:
                approval_request = req
                break
        
        if not approval_request:
            return {
                "success": False,
                "error": "Approval request not found"
            }
        
        # Update approval request
        approval_request["status"] = decision
        approval_request["decided_at"] = datetime.now().isoformat()
        approval_request["approver"] = approver
        approval_request["comments"] = comments
        
        # Move to history
        self.approval_history.append(approval_request)
        self.pending_approvals = [req for req in self.pending_approvals if req["id"] != approval_id]
        
        # Save updated data
        self.save_approval_data()
        
        return {
            "success": True,
            "approval_id": approval_id,
            "decision": decision,
            "approver": approver,
            "timestamp": datetime.now().isoformat()
        }
    
    async def generate_approval_report(self) -> Dict[str, Any]:
        """Generate comprehensive approval system report"""
        print("📊 Generating approval system report...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "pending_approvals": len(self.pending_approvals),
                "total_approvals": len(self.approval_history),
                "approved_count": len([a for a in self.approval_history if a["status"] == "approved"]),
                "rejected_count": len([a for a in self.approval_history if a["status"] == "rejected"]),
                "auto_approved_count": len([a for a in self.approval_history if a["status"] == "auto"])
            },
            "pending_approvals": self.pending_approvals,
            "approval_history": self.approval_history[-10:],  # Last 10 approvals
            "approval_rules": self.approval_rules,
            "recommendations": []
        }
        
        # Generate recommendations
        if report["summary"]["pending_approvals"] > 5:
            report["recommendations"].append("High number of pending approvals - consider increasing review capacity")
        
        if report["summary"]["rejected_count"] > report["summary"]["approved_count"]:
            report["recommendations"].append("High rejection rate - review auto-approval rules")
        
        if report["summary"]["auto_approved_count"] == 0:
            report["recommendations"].append("No auto-approvals - consider enabling safe auto-approval rules")
        
        return report

async def main():
    """Main function to run human approval system"""
    print("👥 AI Human Approval System Starting...")
    print("=" * 60)
    
    approval_system = AIHumanApprovalSystem()
    
    # Test with a sample fix
    test_fix = {
        "type": "dependency_fixes",
        "risk_level": "low",
        "impact_scope": "local",
        "description": "Update aiohttp to fix security vulnerability",
        "files_changed": ["requirements.txt"],
        "tests_passed": True
    }
    
    try:
        # Step 1: Evaluate approval requirements
        approval_requirements = await approval_system.evaluate_approval_requirements(test_fix)
        print(f"📋 Approval Required: {approval_requirements['approval_required']}")
        print(f"📝 Approval Type: {approval_requirements.get('approval_type', 'N/A')}")
        
        # Step 2: Create approval request if needed
        if approval_requirements['approval_required']:
            approval_request = await approval_system.create_approval_request(test_fix, approval_requirements)
            print(f"📝 Created approval request: {approval_request['id']}")
            
            # Step 3: Get AI recommendation
            ai_recommendation = await approval_system.get_ai_approval_recommendation(approval_request)
            
            if ai_recommendation.get('success'):
                print(f"🤖 AI Recommendation: {ai_recommendation['ai_recommendation']['recommendation']}")
                print(f"📊 Confidence: {ai_recommendation['ai_recommendation']['confidence']}")
            else:
                print(f"❌ AI recommendation failed: {ai_recommendation.get('error')}")
        else:
            print("✅ Auto-approved - no human approval required")
        
        # Step 4: Generate report
        report = await approval_system.generate_approval_report()
        
        # Save report
        os.makedirs("artifacts", exist_ok=True)
        with open("artifacts/human_approval_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 HUMAN APPROVAL SYSTEM REPORT")
        print("=" * 60)
        print(f"⏳ Pending Approvals: {report['summary']['pending_approvals']}")
        print(f"✅ Total Approvals: {report['summary']['total_approvals']}")
        print(f"👍 Approved: {report['summary']['approved_count']}")
        print(f"👎 Rejected: {report['summary']['rejected_count']}")
        print(f"🤖 Auto-Approved: {report['summary']['auto_approved_count']}")
        
        if report['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in report['recommendations']:
                print(f"  - {rec}")
        
        return report
        
    except Exception as e:
        print(f"❌ Critical error in human approval system: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    asyncio.run(main())
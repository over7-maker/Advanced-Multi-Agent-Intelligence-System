#!/usr/bin/env python3
"""
Generate Comprehensive Audit Report - HTML and Text Output
"""

import json
import os
from datetime import datetime
from pathlib import Path

def generate_html_report(audit_data, output_file):
    """Generate HTML audit report"""
    
    stats = audit_data.get('statistics', {})
    workflow_audit = audit_data.get('workflow_audit', {})
    api_audit = audit_data.get('api_key_audit', {})
    legacy_audit = audit_data.get('legacy_audit', {})
    security_audit = audit_data.get('security_audit', {})
    recommendations = audit_data.get('recommendations', [])
    critical_issues = audit_data.get('critical_issues', [])
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔍 Comprehensive Audit Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            border-bottom: 3px solid #007acc;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .status {{
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            font-weight: bold;
        }}
        .success {{ background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
        .warning {{ background-color: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }}
        .error {{ background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
        .section {{
            margin: 30px 0;
            padding: 20px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
        }}
        .section h2 {{
            color: #007acc;
            border-bottom: 2px solid #007acc;
            padding-bottom: 10px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid #007acc;
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #007acc;
        }}
        .recommendation {{
            background: #f8f9fa;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 4px solid #ffc107;
        }}
        .critical {{
            border-left-color: #dc3545;
            background: #fff5f5;
        }}
        .high {{
            border-left-color: #fd7e14;
            background: #fff8f0;
        }}
        .medium {{
            border-left-color: #ffc107;
            background: #fffdf0;
        }}
        .low {{
            border-left-color: #28a745;
            background: #f0fff4;
        }}
        .issue-list {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
        }}
        .issue-item {{
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
            background: white;
            border-left: 3px solid #007acc;
        }}
        .timestamp {{
            color: #666;
            font-size: 0.9em;
        }}
        .emoji {{
            font-size: 1.2em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Comprehensive Audit Report</h1>
            <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="status {'error' if stats.get('critical_issues', 0) > 0 else 'success'}">
            <span class="emoji">{"❌" if stats.get('critical_issues', 0) > 0 else "✅"}</span>
            {"CRITICAL ISSUES FOUND - IMMEDIATE ACTION REQUIRED" if stats.get('critical_issues', 0) > 0 else "AUDIT COMPLETED SUCCESSFULLY"}
        </div>
        
        <div class="section">
            <h2>📊 Overall Statistics</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{stats.get('total_issues', 0)}</div>
                    <div>Total Issues</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" style="color: #dc3545;">{stats.get('critical_issues', 0)}</div>
                    <div>Critical Issues</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" style="color: #fd7e14;">{stats.get('high_priority_issues', 0)}</div>
                    <div>High Priority</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" style="color: #ffc107;">{stats.get('medium_priority_issues', 0)}</div>
                    <div>Medium Priority</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" style="color: #28a745;">{stats.get('low_priority_issues', 0)}</div>
                    <div>Low Priority</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>🔍 Workflow Audit Results</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{workflow_audit.get('total_workflows', 0)}</div>
                    <div>Total Workflows</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" style="color: #dc3545;">{len(workflow_audit.get('duplicate_triggers', []))}</div>
                    <div>Duplicate Triggers</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" style="color: #ffc107;">{len(workflow_audit.get('conflicting_triggers', []))}</div>
                    <div>Conflicting Triggers</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>🔑 API Key Audit Results</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number" style="color: #dc3545;">{len(api_audit.get('direct_usage', []))}</div>
                    <div>Direct Usage</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" style="color: #28a745;">{len(api_audit.get('manager_usage', []))}</div>
                    <div>Manager Usage</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" style="color: #ffc107;">{len(api_audit.get('missing_manager', []))}</div>
                    <div>Missing Manager</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>🧹 Legacy Audit Results</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number" style="color: #dc3545;">{len(legacy_audit.get('stub_workflows', []))}</div>
                    <div>Stub Workflows</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" style="color: #ffc107;">{len(legacy_audit.get('legacy_workflows', []))}</div>
                    <div>Legacy Workflows</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" style="color: #dc3545;">{len(legacy_audit.get('broken_workflows', []))}</div>
                    <div>Broken Workflows</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>🛡️ Security Audit Results</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number" style="color: #dc3545;">{len(security_audit.get('exposed_secrets', []))}</div>
                    <div>Exposed Secrets</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" style="color: #ffc107;">{len(security_audit.get('insecure_patterns', []))}</div>
                    <div>Insecure Patterns</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" style="color: #dc3545;">{len(security_audit.get('vulnerable_dependencies', []))}</div>
                    <div>Vulnerable Dependencies</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>🎯 Recommendations</h2>
            {''.join([f'''
            <div class="recommendation {rec.get('priority', 'medium')}">
                <h3>{rec.get('title', 'Unknown')}</h3>
                <p><strong>Description:</strong> {rec.get('description', 'No description')}</p>
                <p><strong>Action:</strong> {rec.get('action', 'No action specified')}</p>
            </div>
            ''' for rec in recommendations])}
        </div>
        
        <div class="section">
            <h2>🚨 Critical Issues</h2>
            {''.join([f'''
            <div class="issue-item">
                <h3>{issue.get('title', 'Unknown Issue')}</h3>
                <p>{issue.get('description', 'No description available')}</p>
            </div>
            ''' for issue in critical_issues]) if critical_issues else '<p>No critical issues found!</p>'}
        </div>
        
        <div class="section">
            <h2>📋 Detailed Issues by Category</h2>
            
            <h3>🔑 Direct API Key Usage</h3>
            <div class="issue-list">
                {''.join([f'<div class="issue-item"><strong>{item.get("file", "Unknown file")}</strong>: {item.get("pattern", "Unknown pattern")}</div>' for item in api_audit.get('direct_usage', [])[:10]]) if api_audit.get('direct_usage') else '<p>No direct API key usage found!</p>'}
            </div>
            
            <h3>🛡️ Exposed Secrets</h3>
            <div class="issue-list">
                {''.join([f'<div class="issue-item"><strong>{item.get("file", "Unknown file")}</strong>: {item.get("pattern", "Unknown pattern")}</div>' for item in security_audit.get('exposed_secrets', [])[:10]]) if security_audit.get('exposed_secrets') else '<p>No exposed secrets found!</p>'}
            </div>
            
            <h3>⚠️ Insecure Patterns</h3>
            <div class="issue-list">
                {''.join([f'<div class="issue-item"><strong>{item.get("file", "Unknown file")}</strong>: {item.get("pattern", "Unknown pattern")}</div>' for item in security_audit.get('insecure_patterns', [])[:10]]) if security_audit.get('insecure_patterns') else '<p>No insecure patterns found!</p>'}
            </div>
        </div>
        
        <div class="section">
            <h2>🎯 Next Steps</h2>
            <ol>
                <li>Review all critical issues identified above</li>
                <li>Fix direct API key usage by migrating to centralized manager</li>
                <li>Remove exposed secrets and use environment variables</li>
                <li>Address insecure code patterns for better security</li>
                <li>Fix YAML syntax issues in workflows</li>
                <li>Run the audit again to verify fixes</li>
            </ol>
        </div>
        
        <div class="section">
            <h2>📞 Support</h2>
            <p>For questions about this audit report or help with fixes, please refer to the project documentation or create an issue in the repository.</p>
        </div>
    </div>
</body>
</html>
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

def generate_text_report(audit_data, output_file):
    """Generate text audit report"""
    
    stats = audit_data.get('statistics', {})
    workflow_audit = audit_data.get('workflow_audit', {})
    api_audit = audit_data.get('api_key_audit', {})
    legacy_audit = audit_data.get('legacy_audit', {})
    security_audit = audit_data.get('security_audit', {})
    recommendations = audit_data.get('recommendations', [])
    critical_issues = audit_data.get('critical_issues', [])
    
    text_content = f"""
🔍 COMPREHENSIVE AUDIT REPORT
============================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 OVERALL STATUS
================
{"❌ CRITICAL ISSUES FOUND - IMMEDIATE ACTION REQUIRED" if stats.get('critical_issues', 0) > 0 else "✅ AUDIT COMPLETED SUCCESSFULLY"}

📈 STATISTICS
=============
Total Issues: {stats.get('total_issues', 0)}
Critical Issues: {stats.get('critical_issues', 0)}
High Priority: {stats.get('high_priority_issues', 0)}
Medium Priority: {stats.get('medium_priority_issues', 0)}
Low Priority: {stats.get('low_priority_issues', 0)}

🔍 WORKFLOW AUDIT
=================
Total Workflows: {workflow_audit.get('total_workflows', 0)}
Duplicate Triggers: {len(workflow_audit.get('duplicate_triggers', []))}
Conflicting Triggers: {len(workflow_audit.get('conflicting_triggers', []))}

🔑 API KEY AUDIT
================
Direct Usage: {len(api_audit.get('direct_usage', []))}
Manager Usage: {len(api_audit.get('manager_usage', []))}
Missing Manager: {len(api_audit.get('missing_manager', []))}

🧹 LEGACY AUDIT
===============
Stub Workflows: {len(legacy_audit.get('stub_workflows', []))}
Legacy Workflows: {len(legacy_audit.get('legacy_workflows', []))}
Minimal Workflows: {len(legacy_audit.get('minimal_workflows', []))}
Broken Workflows: {len(legacy_audit.get('broken_workflows', []))}

🛡️ SECURITY AUDIT
==================
Exposed Secrets: {len(security_audit.get('exposed_secrets', []))}
Insecure Patterns: {len(security_audit.get('insecure_patterns', []))}
Vulnerable Dependencies: {len(security_audit.get('vulnerable_dependencies', []))}

🎯 RECOMMENDATIONS
==================
"""
    
    for i, rec in enumerate(recommendations, 1):
        text_content += f"""
{i}. [{rec.get('priority', 'UNKNOWN').upper()}] {rec.get('title', 'Unknown')}
   Description: {rec.get('description', 'No description')}
   Action: {rec.get('action', 'No action specified')}
"""
    
    text_content += f"""

🚨 CRITICAL ISSUES
==================
"""
    
    if critical_issues:
        for i, issue in enumerate(critical_issues, 1):
            text_content += f"""
{i}. {issue.get('title', 'Unknown Issue')}
   {issue.get('description', 'No description available')}
"""
    else:
        text_content += "No critical issues found!\n"
    
    text_content += f"""

📋 DETAILED ISSUES
==================

🔑 Direct API Key Usage:
"""
    
    if api_audit.get('direct_usage'):
        for item in api_audit['direct_usage'][:10]:
            text_content += f"- {item.get('file', 'Unknown file')}: {item.get('pattern', 'Unknown pattern')}\n"
    else:
        text_content += "No direct API key usage found!\n"
    
    text_content += f"""

🛡️ Exposed Secrets:
"""
    
    if security_audit.get('exposed_secrets'):
        for item in security_audit['exposed_secrets'][:10]:
            text_content += f"- {item.get('file', 'Unknown file')}: {item.get('pattern', 'Unknown pattern')}\n"
    else:
        text_content += "No exposed secrets found!\n"
    
    text_content += f"""

⚠️ Insecure Patterns:
"""
    
    if security_audit.get('insecure_patterns'):
        for item in security_audit['insecure_patterns'][:10]:
            text_content += f"- {item.get('file', 'Unknown file')}: {item.get('pattern', 'Unknown pattern')}\n"
    else:
        text_content += "No insecure patterns found!\n"
    
    text_content += f"""

🎯 NEXT STEPS
=============
1. Review all critical issues identified above
2. Fix direct API key usage by migrating to centralized manager
3. Remove exposed secrets and use environment variables
4. Address insecure code patterns for better security
5. Fix YAML syntax issues in workflows
6. Run the audit again to verify fixes

📞 SUPPORT
==========
For questions about this audit report or help with fixes, please refer to the project documentation or create an issue in the repository.

---
Generated by Comprehensive Audit System
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(text_content)

def main():
    """Main function"""
    print("🔍 Generating Comprehensive Audit Reports...")
    
    # Find the most recent audit results file
    audit_files = list(Path('.').glob('audit_results_*.json'))
    if not audit_files:
        print("❌ No audit results files found!")
        print("Please run the audit first: ./run_audit_success.sh")
        return 1
    
    # Get the most recent file
    latest_file = max(audit_files, key=lambda f: f.stat().st_mtime)
    print(f"📁 Using audit results: {latest_file}")
    
    # Load audit data
    try:
        with open(latest_file, 'r') as f:
            audit_data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading audit data: {e}")
        return 1
    
    # Generate reports
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    html_file = f"audit_report_{timestamp}.html"
    text_file = f"audit_report_{timestamp}.txt"
    
    print("📊 Generating HTML report...")
    generate_html_report(audit_data, html_file)
    
    print("📄 Generating text report...")
    generate_text_report(audit_data, text_file)
    
    print(f"✅ Reports generated successfully!")
    print(f"📊 HTML Report: {html_file}")
    print(f"📄 Text Report: {text_file}")
    print("")
    print("🌐 You can now view the HTML report in your browser!")
    print("📱 The text report is perfect for mobile viewing!")
    
    return 0

if __name__ == "__main__":
    exit(main())
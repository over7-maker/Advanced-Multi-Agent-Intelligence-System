#!/usr/bin/env python3
"""
AMAS Intelligence System - Simple Workflow Check
Basic workflow verification without external dependencies
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path


def check_file_exists(file_path: str) -> bool:
    """Check if a file exists"""
    return Path(file_path).exists()


def check_directory_exists(dir_path: str) -> bool:
    """Check if a directory exists"""
    return Path(dir_path).exists()


def check_file_content(file_path: str, required_content: list) -> bool:
    """Check if file contains required content"""
    try:
        if not check_file_exists(file_path):
            return False

        with open(file_path, "r") as f:
            content = f.read()

        for required in required_content:
            if required not in content:
                return False
        return True
    except Exception:
        return False


def main():
    """Main workflow check"""
    print("🔍 AMAS Intelligence System - Simple Workflow Check")
    print("=" * 60)

    results = []

    # Check core files
    core_files = [
        "main_phase5_complete.py",
        "core/orchestrator.py",
        "services/security_service.py",
        "services/security_monitoring_service.py",
        "services/audit_logging_service.py",
        "services/incident_response_service.py",
        "services/monitoring_service.py",
        "services/performance_service.py",
    ]

    print("\n📁 Checking Core Files...")
    for file_path in core_files:
        exists = check_file_exists(file_path)
        results.append({"file": file_path, "exists": exists, "type": "core_file"})
        status = "✅" if exists else "❌"
        print(f"  {status} {file_path}")

    # Check agent files
    agent_files = [
        "agents/osint/osint_agent.py",
        "agents/investigation/investigation_agent.py",
        "agents/forensics/forensics_agent.py",
        "agents/data_analysis/data_analysis_agent.py",
        "agents/reverse_engineering/reverse_engineering_agent.py",
        "agents/metadata/metadata_agent.py",
        "agents/reporting/reporting_agent.py",
        "agents/technology_monitor/technology_monitor_agent.py",
    ]

    print("\n🤖 Checking Agent Files...")
    for file_path in agent_files:
        exists = check_file_exists(file_path)
        results.append({"file": file_path, "exists": exists, "type": "agent_file"})
        status = "✅" if exists else "❌"
        print(f"  {status} {file_path}")

    # Check workflow templates in orchestrator
    print("\n🔄 Checking Workflow Templates...")
    orchestrator_path = "core/orchestrator.py"
    if check_file_exists(orchestrator_path):
        workflow_templates = [
            "osint_investigation",
            "digital_forensics",
            "threat_intelligence",
        ]

        for template in workflow_templates:
            has_template = check_file_content(orchestrator_path, [f"'{template}'"])
            results.append(
                {
                    "workflow": template,
                    "exists": has_template,
                    "type": "workflow_template",
                }
            )
            status = "✅" if has_template else "❌"
            print(f"  {status} {template} workflow template")

    # Check security workflows in main application
    print("\n🔒 Checking Security Workflows...")
    main_app_path = "main_phase5_complete.py"
    if check_file_exists(main_app_path):
        security_workflows = [
            "execute_security_workflow",
            "_execute_threat_hunting_workflow",
            "_execute_incident_response_workflow",
            "_execute_security_assessment_workflow",
        ]

        for workflow in security_workflows:
            has_workflow = check_file_content(main_app_path, [workflow])
            results.append(
                {
                    "workflow": workflow,
                    "exists": has_workflow,
                    "type": "security_workflow",
                }
            )
            status = "✅" if has_workflow else "❌"
            print(f"  {status} {workflow}")

    # Check configuration files
    print("\n⚙️ Checking Configuration Files...")
    config_files = ["docker-compose.yml", "requirements.txt", "README.md"]

    for file_path in config_files:
        exists = check_file_exists(file_path)
        results.append({"file": file_path, "exists": exists, "type": "config_file"})
        status = "✅" if exists else "❌"
        print(f"  {status} {file_path}")

    # Check test files
    print("\n🧪 Checking Test Files...")
    test_files = [
        "test_phase5_complete.py",
        "verify_workflows.py",
        "check_workflow_configuration.py",
        "check_workflow_status.py",
        "run_workflow_tests.py",
    ]

    for file_path in test_files:
        exists = check_file_exists(file_path)
        results.append({"file": file_path, "exists": exists, "type": "test_file"})
        status = "✅" if exists else "❌"
        print(f"  {status} {file_path}")

    # Calculate summary
    total_checks = len(results)
    passed_checks = len([r for r in results if r["exists"]])
    failed_checks = total_checks - passed_checks
    success_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0

    print("\n" + "=" * 60)
    print("📊 Workflow Check Summary")
    print("=" * 60)
    print(f"Total Checks: {total_checks}")
    print(f"Passed: {passed_checks}")
    print(f"Failed: {failed_checks}")
    print(f"Success Rate: {success_rate:.1f}%")

    if failed_checks > 0:
        print(f"\n❌ Failed Checks:")
        for result in results:
            if not result["exists"]:
                print(f"  - {result.get('file', result.get('workflow', 'unknown'))}")
    else:
        print(f"\n🎉 All workflow checks passed!")

    # Save results
    report = {
        "workflow_check_suite": "AMAS Simple Workflow Check",
        "timestamp": datetime.utcnow().isoformat(),
        "summary": {
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "failed_checks": failed_checks,
            "success_rate": success_rate,
        },
        "results": results,
    }

    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)

    with open("logs/simple_workflow_check_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Report saved: logs/simple_workflow_check_report.json")

    return 0 if failed_checks == 0 else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

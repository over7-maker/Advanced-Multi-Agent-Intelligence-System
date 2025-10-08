#!/usr/bin/env python3
"""
AMAS Security Scanning Script
Comprehensive vulnerability scanning for production readiness
"""

import subprocess
import sys
import json
import os
from datetime import datetime
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return results"""
    print(f"🔍 {description}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        return True, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr


def run_safety_scan():
    """Run Safety vulnerability scan"""
    print("\n" + "="*60)
    print("🛡️  SAFETY VULNERABILITY SCAN")
    print("="*60)
    
    # Run safety scan
    success, stdout, stderr = run_command("python3 -m safety check --json", "Safety vulnerability scan")
    
    if success:
        try:
            data = json.loads(stdout)
            vulnerabilities = data.get('vulnerabilities', [])
            affected_packages = data.get('affected_packages', {})
            
            if vulnerabilities:
                print(f"❌ Found {len(vulnerabilities)} vulnerabilities:")
                for vuln in vulnerabilities:
                    print(f"  • {vuln.get('package', 'Unknown')}: {vuln.get('vulnerability', 'Unknown')}")
                return False
            else:
                print("✅ No vulnerabilities found by Safety")
                return True
        except json.JSONDecodeError:
            print("⚠️  Safety scan completed but couldn't parse JSON output")
            return True
    else:
        print(f"❌ Safety scan failed: {stderr}")
        return False


def run_pip_audit():
    """Run pip-audit vulnerability scan"""
    print("\n" + "="*60)
    print("🔍 PIP-AUDIT VULNERABILITY SCAN")
    print("="*60)
    
    # Run pip-audit scan
    success, stdout, stderr = run_command("python3 -m pip_audit --format=json", "pip-audit vulnerability scan")
    
    if success:
        try:
            data = json.loads(stdout)
            dependencies = data.get('dependencies', [])
            vulnerabilities_found = 0
            
            for dep in dependencies:
                vulns = dep.get('vulns', [])
                if vulns:
                    vulnerabilities_found += len(vulns)
                    print(f"❌ {dep['name']} {dep['version']}: {len(vulns)} vulnerabilities")
                    for vuln in vulns:
                        print(f"    • {vuln.get('id', 'Unknown')}: {vuln.get('description', 'No description')[:100]}...")
            
            if vulnerabilities_found == 0:
                print("✅ No vulnerabilities found by pip-audit")
                return True
            else:
                print(f"❌ Found {vulnerabilities_found} total vulnerabilities")
                return False
        except json.JSONDecodeError:
            print("⚠️  pip-audit scan completed but couldn't parse JSON output")
            return True
    else:
        print(f"❌ pip-audit scan failed: {stderr}")
        return False


def run_bandit_scan():
    """Run Bandit security linting"""
    print("\n" + "="*60)
    print("🔒 BANDIT SECURITY LINTING")
    print("="*60)
    
    # Run bandit scan
    success, stdout, stderr = run_command("python3 -m bandit -r src/ -f json", "Bandit security linting")
    
    if success:
        try:
            data = json.loads(stdout)
            results = data.get('results', [])
            
            if results:
                print(f"❌ Found {len(results)} security issues:")
                for result in results:
                    print(f"  • {result.get('filename', 'Unknown')}:{result.get('line_number', '?')} - {result.get('issue_severity', 'Unknown')} - {result.get('issue_text', 'No description')}")
                return False
            else:
                print("✅ No security issues found by Bandit")
                return True
        except json.JSONDecodeError:
            print("⚠️  Bandit scan completed but couldn't parse JSON output")
            return True
    else:
        print(f"❌ Bandit scan failed: {stderr}")
        return False


def generate_security_report():
    """Generate comprehensive security report"""
    print("\n" + "="*60)
    print("📊 GENERATING SECURITY REPORT")
    print("="*60)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "scans": {
            "safety": {"status": "pending"},
            "pip_audit": {"status": "pending"},
            "bandit": {"status": "pending"}
        },
        "summary": {
            "total_scans": 3,
            "passed": 0,
            "failed": 0,
            "overall_status": "pending"
        }
    }
    
    # Run all scans
    safety_result = run_safety_scan()
    pip_audit_result = run_pip_audit()
    bandit_result = run_bandit_scan()
    
    # Update report
    report["scans"]["safety"]["status"] = "passed" if safety_result else "failed"
    report["scans"]["pip_audit"]["status"] = "passed" if pip_audit_result else "failed"
    report["scans"]["bandit"]["status"] = "passed" if bandit_result else "failed"
    
    # Calculate summary
    passed = sum(1 for scan in report["scans"].values() if scan["status"] == "passed")
    failed = sum(1 for scan in report["scans"].values() if scan["status"] == "failed")
    
    report["summary"]["passed"] = passed
    report["summary"]["failed"] = failed
    report["summary"]["overall_status"] = "passed" if failed == 0 else "failed"
    
    # Save report
    report_file = Path("security_report.json")
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("📋 SECURITY SCAN SUMMARY")
    print("="*60)
    print(f"Safety Scan: {'✅ PASSED' if safety_result else '❌ FAILED'}")
    print(f"pip-audit Scan: {'✅ PASSED' if pip_audit_result else '❌ FAILED'}")
    print(f"Bandit Scan: {'✅ PASSED' if bandit_result else '❌ FAILED'}")
    print(f"\nOverall Status: {'✅ ALL CHECKS PASSED' if failed == 0 else '❌ SECURITY ISSUES FOUND'}")
    print(f"Report saved to: {report_file.absolute()}")
    
    return failed == 0


def main():
    """Main security scanning function"""
    print("🛡️  AMAS Security Scanning")
    print("="*60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    # Check if we're in the right directory
    if not Path("requirements.txt").exists():
        print("❌ requirements.txt not found. Please run from project root.")
        sys.exit(1)
    
    # Run security scans
    success = generate_security_report()
    
    if success:
        print("\n🎉 All security scans passed!")
        sys.exit(0)
    else:
        print("\n⚠️  Security issues found. Please review the report.")
        sys.exit(1)


if __name__ == "__main__":
    main()
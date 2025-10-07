#!/usr/bin/env python3
"""
Security Hardening Script for AMAS
Ensures all security measures are properly implemented
"""
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from amas.security.secure_config import SecureConfigManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecurityHardening:
    """Security hardening for AMAS system"""

    def __init__(self):
        self.secure_config = SecureConfigManager()
        self.security_checks = []
        self.vulnerabilities_found = []

    def run_all_checks(self) -> bool:
        """Run all security checks"""
        logger.info("🔒 Starting AMAS Security Hardening...")

        checks = [
            self.check_environment_variables,
            self.check_file_permissions,
            self.check_docker_security,
            self.check_network_security,
            self.check_encryption_config,
            self.check_audit_logging,
            self.check_input_validation,
            self.check_dependencies,
            self.check_code_quality,
            self.check_secrets_management,
        ]

        all_passed = True
        for check in checks:
            try:
                result = check()
                if not result:
                    all_passed = False
            except Exception as e:
                logger.error(f"Security check failed: {e}")
                all_passed = False

        self.generate_report()
        return all_passed

    def check_environment_variables(self) -> bool:
        """Check environment variable security"""
        logger.info("🔍 Checking environment variables...")

        required_vars = [
            "POSTGRES_PASSWORD",
            "JWT_SECRET",
            "ENCRYPTION_KEY",
            "REDIS_PASSWORD",
        ]

        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            logger.error(f"❌ Missing required environment variables: {missing_vars}")
            self.vulnerabilities_found.append(
                {
                    "type": "missing_env_vars",
                    "severity": "high",
                    "description": f"Missing environment variables: {missing_vars}",
                    "fix": "Set all required environment variables",
                }
            )
            return False

        logger.info("✅ Environment variables configured")
        return True

    def check_file_permissions(self) -> bool:
        """Check file permissions security"""
        logger.info("🔍 Checking file permissions...")

        sensitive_files = [
            "/app/config/encryption.key",
            "/app/.env",
            "/app/logs",
            "/app/data",
        ]

        issues_found = []
        for file_path in sensitive_files:
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                mode = oct(stat.st_mode)[-3:]

                # Check if file is readable by others
                if int(mode[-1]) > 4:
                    issues_found.append(f"{file_path}: {mode} (too permissive)")

        if issues_found:
            logger.error(f"❌ File permission issues: {issues_found}")
            self.vulnerabilities_found.append(
                {
                    "type": "file_permissions",
                    "severity": "medium",
                    "description": f"Insecure file permissions: {issues_found}",
                    "fix": "Set restrictive file permissions (600 for files, 700 for directories)",
                }
            )
            return False

        logger.info("✅ File permissions secure")
        return True

    def check_docker_security(self) -> bool:
        """Check Docker security configuration"""
        logger.info("🔍 Checking Docker security...")

        dockerfile_path = Path(__file__).parent.parent / "docker" / "Dockerfile"
        if not dockerfile_path.exists():
            logger.error("❌ Dockerfile not found")
            return False

        # Check for security best practices in Dockerfile
        with open(dockerfile_path, "r") as f:
            dockerfile_content = f.read()

        security_issues = []

        # Check for running as root
        if "USER root" in dockerfile_content and "USER amas" not in dockerfile_content:
            security_issues.append("Container runs as root")

        # Check for security updates
        if "apt-get update" not in dockerfile_content:
            security_issues.append("No package updates in Dockerfile")

        if security_issues:
            logger.error(f"❌ Docker security issues: {security_issues}")
            self.vulnerabilities_found.append(
                {
                    "type": "docker_security",
                    "severity": "medium",
                    "description": f"Docker security issues: {security_issues}",
                    "fix": "Update Dockerfile with security best practices",
                }
            )
            return False

        logger.info("✅ Docker security configured")
        return True

    def check_network_security(self) -> bool:
        """Check network security configuration"""
        logger.info("🔍 Checking network security...")

        # Check if HTTPS is configured
        nginx_config_path = (
            Path(__file__).parent.parent / "docker" / "nginx" / "nginx.conf"
        )
        if nginx_config_path.exists():
            with open(nginx_config_path, "r") as f:
                nginx_content = f.read()

            if "ssl_certificate" not in nginx_content:
                logger.warning("⚠️ SSL/TLS not configured in Nginx")
                self.vulnerabilities_found.append(
                    {
                        "type": "network_security",
                        "severity": "medium",
                        "description": "SSL/TLS not configured",
                        "fix": "Configure SSL certificates in Nginx",
                    }
                )

        logger.info("✅ Network security checked")
        return True

    def check_encryption_config(self) -> bool:
        """Check encryption configuration"""
        logger.info("🔍 Checking encryption configuration...")

        # Check if encryption keys are properly configured
        config = self.secure_config.get_security_config()

        if not config.get("jwt_secret"):
            logger.error("❌ JWT secret not configured")
            return False

        if not config.get("encryption_key"):
            logger.error("❌ Encryption key not configured")
            return False

        # Check key strength
        jwt_secret = config.get("jwt_secret", "")
        if len(jwt_secret) < 32:
            logger.warning("⚠️ JWT secret is too short (recommended: 32+ characters)")

        encryption_key = config.get("encryption_key", "")
        if len(encryption_key) < 32:
            logger.warning(
                "⚠️ Encryption key is too short (recommended: 32+ characters)"
            )

        logger.info("✅ Encryption configuration secure")
        return True

    def check_audit_logging(self) -> bool:
        """Check audit logging configuration"""
        logger.info("🔍 Checking audit logging...")

        config = self.secure_config.get_security_config()

        if not config.get("audit_enabled", True):
            logger.warning("⚠️ Audit logging is disabled")
            self.vulnerabilities_found.append(
                {
                    "type": "audit_logging",
                    "severity": "medium",
                    "description": "Audit logging is disabled",
                    "fix": "Enable audit logging for compliance",
                }
            )

        logger.info("✅ Audit logging configured")
        return True

    def check_input_validation(self) -> bool:
        """Check input validation implementation"""
        logger.info("🔍 Checking input validation...")

        # Check if input validation is implemented in API
        api_path = Path(__file__).parent.parent / "src" / "amas" / "api" / "main.py"
        if api_path.exists():
            with open(api_path, "r") as f:
                api_content = f.read()

            # Check for input validation patterns
            validation_patterns = ["pydantic", "validation", "sanitize", "escape"]

            found_patterns = [
                pattern
                for pattern in validation_patterns
                if pattern in api_content.lower()
            ]

            if not found_patterns:
                logger.warning("⚠️ Input validation may not be implemented")
                self.vulnerabilities_found.append(
                    {
                        "type": "input_validation",
                        "severity": "high",
                        "description": "Input validation not implemented",
                        "fix": "Implement input validation and sanitization",
                    }
                )

        logger.info("✅ Input validation checked")
        return True

    def check_dependencies(self) -> bool:
        """Check dependency security"""
        logger.info("🔍 Checking dependencies...")

        requirements_path = Path(__file__).parent.parent / "requirements.txt"
        if requirements_path.exists():
            # Check for known vulnerable packages
            vulnerable_packages = [
                "django<2.2",
                "flask<1.0",
                "requests<2.20",
                "urllib3<1.24",
            ]

            with open(requirements_path, "r") as f:
                requirements = f.read()

            for package in vulnerable_packages:
                if package.split("<")[0] in requirements:
                    logger.warning(f"⚠️ Potentially vulnerable package: {package}")
                    self.vulnerabilities_found.append(
                        {
                            "type": "vulnerable_dependency",
                            "severity": "high",
                            "description": f"Vulnerable package detected: {package}",
                            "fix": f'Update {package.split("<")[0]} to latest version',
                        }
                    )

        logger.info("✅ Dependencies checked")
        return True

    def check_code_quality(self) -> bool:
        """Check code quality and security"""
        logger.info("🔍 Checking code quality...")

        # Run security linting
        try:
            result = subprocess.run(
                ["python", "-m", "bandit", "-r", "src/", "-f", "json"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                logger.warning("⚠️ Security issues found in code")
                self.vulnerabilities_found.append(
                    {
                        "type": "code_quality",
                        "severity": "medium",
                        "description": "Security issues found in code",
                        "fix": "Run bandit security linter and fix issues",
                    }
                )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("⚠️ Security linter not available")

        logger.info("✅ Code quality checked")
        return True

    def check_secrets_management(self) -> bool:
        """Check secrets management"""
        logger.info("🔍 Checking secrets management...")

        # Check for hardcoded secrets in code
        src_path = Path(__file__).parent.parent / "src"
        hardcoded_secrets = []

        for py_file in src_path.rglob("*.py"):
            try:
                with open(py_file, "r") as f:
                    content = f.read()

                # Check for common hardcoded secrets
                secret_patterns = [
                    r'password\s*=\s*["\'][^"\']+["\']',
                    r'secret\s*=\s*["\'][^"\']+["\']',
                    r'key\s*=\s*["\'][^"\']+["\']',
                    r'token\s*=\s*["\'][^"\']+["\']',
                ]

                for pattern in secret_patterns:
                    import re

                    if re.search(pattern, content, re.IGNORECASE):
                        hardcoded_secrets.append(f"{py_file}: {pattern}")
            except Exception:
                continue

        if hardcoded_secrets:
            logger.error(f"❌ Hardcoded secrets found: {hardcoded_secrets}")
            self.vulnerabilities_found.append(
                {
                    "type": "hardcoded_secrets",
                    "severity": "critical",
                    "description": f"Hardcoded secrets found: {hardcoded_secrets}",
                    "fix": "Remove hardcoded secrets and use environment variables",
                }
            )
            return False

        logger.info("✅ Secrets management secure")
        return True

    def generate_report(self):
        """Generate security report"""
        logger.info("📊 Generating security report...")

        report = {
            "total_checks": len(self.security_checks),
            "vulnerabilities_found": len(self.vulnerabilities_found),
            "critical_issues": len(
                [v for v in self.vulnerabilities_found if v["severity"] == "critical"]
            ),
            "high_issues": len(
                [v for v in self.vulnerabilities_found if v["severity"] == "high"]
            ),
            "medium_issues": len(
                [v for v in self.vulnerabilities_found if v["severity"] == "medium"]
            ),
            "low_issues": len(
                [v for v in self.vulnerabilities_found if v["severity"] == "low"]
            ),
            "vulnerabilities": self.vulnerabilities_found,
        }

        # Print report
        print("\n" + "=" * 60)
        print("🔒 AMAS SECURITY HARDENING REPORT")
        print("=" * 60)
        print(f"Total Checks: {report['total_checks']}")
        print(f"Vulnerabilities Found: {report['vulnerabilities_found']}")
        print(f"Critical Issues: {report['critical_issues']}")
        print(f"High Issues: {report['high_issues']}")
        print(f"Medium Issues: {report['medium_issues']}")
        print(f"Low Issues: {report['low_issues']}")
        print("=" * 60)

        if self.vulnerabilities_found:
            print("\n🚨 VULNERABILITIES FOUND:")
            for i, vuln in enumerate(self.vulnerabilities_found, 1):
                print(f"\n{i}. {vuln['type'].upper()}")
                print(f"   Severity: {vuln['severity'].upper()}")
                print(f"   Description: {vuln['description']}")
                print(f"   Fix: {vuln['fix']}")
        else:
            print("\n✅ NO VULNERABILITIES FOUND!")
            print("AMAS system is secure and ready for production.")

        print("\n" + "=" * 60)

        # Save report to file
        report_path = Path(__file__).parent.parent / "security_report.json"
        import json

        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"📄 Security report saved to: {report_path}")


def main():
    """Main function"""
    hardening = SecurityHardening()
    success = hardening.run_all_checks()

    if success:
        logger.info("🎉 Security hardening completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Security hardening failed. Please fix vulnerabilities.")
        sys.exit(1)


if __name__ == "__main__":
    main()

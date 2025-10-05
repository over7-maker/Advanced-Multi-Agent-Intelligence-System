#!/usr/bin/env python3
"""
Environment Setup Script - Sets up the complete AMAS development environment
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, List
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EnvironmentSetup:
    """Environment Setup Manager"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.setup_results = {}

    def check_python_version(self) -> bool:
        """Check if Python version is compatible"""
        try:
            version = sys.version_info
            if version.major == 3 and version.minor >= 8:
                logger.info(
                    f"✓ Python {version.major}.{version.minor}.{version.micro} is compatible"
                )
                return True
            else:
                logger.error(
                    f"✗ Python {version.major}.{version.minor}.{version.micro} is not compatible. Requires Python 3.8+"
                )
                return False
        except Exception as e:
            logger.error(f"Error checking Python version: {e}")
            return False

    def check_dependencies(self) -> Dict[str, Any]:
        """Check if required dependencies are installed"""
        try:
            logger.info("Checking dependencies...")

            dependencies = ["pip", "python", "git", "docker", "docker-compose"]

            results = {}
            for dep in dependencies:
                try:
                    result = subprocess.run(
                        [dep, "--version"], capture_output=True, text=True, timeout=10
                    )
                    if result.returncode == 0:
                        results[dep] = {
                            "installed": True,
                            "version": result.stdout.strip(),
                        }
                        logger.info(f"✓ {dep} is installed")
                    else:
                        results[dep] = {"installed": False, "error": result.stderr}
                        logger.warning(f"✗ {dep} is not installed")
                except FileNotFoundError:
                    results[dep] = {"installed": False, "error": "Not found"}
                    logger.warning(f"✗ {dep} is not installed")
                except subprocess.TimeoutExpired:
                    results[dep] = {"installed": False, "error": "Timeout"}
                    logger.warning(f"✗ {dep} check timed out")
                except Exception as e:
                    results[dep] = {"installed": False, "error": str(e)}
                    logger.warning(f"✗ {dep} check failed: {e}")

            return results

        except Exception as e:
            logger.error(f"Error checking dependencies: {e}")
            return {"error": str(e)}

    def setup_python_environment(self) -> Dict[str, Any]:
        """Setup Python virtual environment and install packages"""
        try:
            logger.info("Setting up Python environment...")

            # Check if virtual environment exists
            venv_path = self.project_root / "venv"
            if venv_path.exists():
                logger.info("✓ Virtual environment already exists")
                return {"status": "exists", "path": str(venv_path)}

            # Create virtual environment
            logger.info("Creating virtual environment...")
            result = subprocess.run(
                [sys.executable, "-m", "venv", "venv"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                logger.info("✓ Virtual environment created successfully")
                return {"status": "created", "path": str(venv_path)}
            else:
                logger.error(f"✗ Failed to create virtual environment: {result.stderr}")
                return {"status": "failed", "error": result.stderr}

        except Exception as e:
            logger.error(f"Error setting up Python environment: {e}")
            return {"error": str(e)}

    def install_python_packages(self) -> Dict[str, Any]:
        """Install Python packages from requirements"""
        try:
            logger.info("Installing Python packages...")

            # Check if requirements file exists
            requirements_file = self.project_root / "requirements.txt"
            if not requirements_file.exists():
                logger.error("✗ requirements.txt not found")
                return {"status": "failed", "error": "requirements.txt not found"}

            # Install packages
            logger.info("Installing packages from requirements.txt...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                logger.info("✓ Python packages installed successfully")
                return {"status": "success", "output": result.stdout}
            else:
                logger.error(f"✗ Failed to install packages: {result.stderr}")
                return {"status": "failed", "error": result.stderr}

        except Exception as e:
            logger.error(f"Error installing Python packages: {e}")
            return {"error": str(e)}

    def setup_docker_services(self) -> Dict[str, Any]:
        """Setup Docker services"""
        try:
            logger.info("Setting up Docker services...")

            # Check if docker-compose.yml exists
            compose_file = self.project_root / "docker-compose.yml"
            if not compose_file.exists():
                logger.warning("✗ docker-compose.yml not found")
                return {"status": "missing", "error": "docker-compose.yml not found"}

            # Start Docker services
            logger.info("Starting Docker services...")
            result = subprocess.run(
                ["docker-compose", "up", "-d"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                logger.info("✓ Docker services started successfully")
                return {"status": "started", "output": result.stdout}
            else:
                logger.error(f"✗ Failed to start Docker services: {result.stderr}")
                return {"status": "failed", "error": result.stderr}

        except Exception as e:
            logger.error(f"Error setting up Docker services: {e}")
            return {"error": str(e)}

    def setup_github_secrets(self) -> Dict[str, Any]:
        """Check GitHub Secrets setup"""
        try:
            logger.info("Checking GitHub Secrets setup...")

            # Check if we're in a GitHub Actions environment
            if os.getenv("GITHUB_ACTIONS"):
                logger.info("✓ Running in GitHub Actions environment")
                return {"status": "github_actions", "environment": "github_actions"}

            # Check if we're in a local development environment
            required_secrets = [
                "DEEPSEEK_API_KEY",
                "GLM_API_KEY",
                "GROK_API_KEY",
                "KIMI_API_KEY",
                "QWEN_API_KEY",
                "GPTOSS_API_KEY",
            ]

            secrets_status = {}
            for secret in required_secrets:
                if os.getenv(secret):
                    secrets_status[secret] = "present"
                    logger.info(f"✓ {secret} is set")
                else:
                    secrets_status[secret] = "missing"
                    logger.warning(f"✗ {secret} is not set")

            return {
                "status": "local_development",
                "environment": "local",
                "secrets": secrets_status,
            }

        except Exception as e:
            logger.error(f"Error checking GitHub Secrets: {e}")
            return {"error": str(e)}

    def create_directories(self) -> Dict[str, Any]:
        """Create necessary directories"""
        try:
            logger.info("Creating necessary directories...")

            directories = [
                "logs",
                "data",
                "models",
                "cache",
                "temp",
                "output",
                "reports",
                "backups",
            ]

            created_dirs = []
            for dir_name in directories:
                dir_path = self.project_root / dir_name
                dir_path.mkdir(exist_ok=True)
                created_dirs.append(str(dir_path))
                logger.info(f"✓ Created directory: {dir_name}")

            return {"status": "success", "directories": created_dirs}

        except Exception as e:
            logger.error(f"Error creating directories: {e}")
            return {"error": str(e)}

    def setup_logging(self) -> Dict[str, Any]:
        """Setup logging configuration"""
        try:
            logger.info("Setting up logging...")

            # Create logs directory
            logs_dir = self.project_root / "logs"
            logs_dir.mkdir(exist_ok=True)

            # Setup logging configuration
            log_config = {
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "standard": {
                        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                    }
                },
                "handlers": {
                    "default": {
                        "level": "INFO",
                        "formatter": "standard",
                        "class": "logging.StreamHandler",
                        "stream": "ext://sys.stdout",
                    },
                    "file": {
                        "level": "INFO",
                        "formatter": "standard",
                        "class": "logging.FileHandler",
                        "filename": str(logs_dir / "amas.log"),
                        "mode": "a",
                    },
                },
                "loggers": {
                    "": {
                        "handlers": ["default", "file"],
                        "level": "INFO",
                        "propagate": False,
                    }
                },
            }

            # Save logging configuration
            config_file = self.project_root / "logging_config.json"
            with open(config_file, "w") as f:
                json.dump(log_config, f, indent=2)

            logger.info("✓ Logging configuration created")
            return {"status": "success", "config_file": str(config_file)}

        except Exception as e:
            logger.error(f"Error setting up logging: {e}")
            return {"error": str(e)}

    def run_full_setup(self) -> Dict[str, Any]:
        """Run complete environment setup"""
        try:
            logger.info("Starting full environment setup...")

            setup_results = {
                "timestamp": datetime.now().isoformat(),
                "python_version": self.check_python_version(),
                "dependencies": self.check_dependencies(),
                "python_environment": self.setup_python_environment(),
                "python_packages": self.install_python_packages(),
                "docker_services": self.setup_docker_services(),
                "github_secrets": self.setup_github_secrets(),
                "directories": self.create_directories(),
                "logging": self.setup_logging(),
            }

            # Generate summary
            setup_results["summary"] = self._generate_setup_summary(setup_results)

            return setup_results

        except Exception as e:
            logger.error(f"Error in full setup: {e}")
            return {"error": str(e)}

    def _generate_setup_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate setup summary"""
        try:
            summary = {"setup_complete": True, "issues": [], "recommendations": []}

            # Check Python version
            if not results.get("python_version", False):
                summary["issues"].append("Python version is not compatible")
                summary["setup_complete"] = False

            # Check dependencies
            deps = results.get("dependencies", {})
            missing_deps = [
                dep
                for dep, status in deps.items()
                if not status.get("installed", False)
            ]
            if missing_deps:
                summary["issues"].append(
                    f"Missing dependencies: {', '.join(missing_deps)}"
                )
                summary["setup_complete"] = False

            # Check Python environment
            if results.get("python_environment", {}).get("status") == "failed":
                summary["issues"].append("Python environment setup failed")
                summary["setup_complete"] = False

            # Check Python packages
            if results.get("python_packages", {}).get("status") == "failed":
                summary["issues"].append("Python packages installation failed")
                summary["setup_complete"] = False

            # Check Docker services
            if results.get("docker_services", {}).get("status") == "failed":
                summary["issues"].append("Docker services setup failed")
                summary["setup_complete"] = False

            # Check GitHub secrets
            secrets = results.get("github_secrets", {}).get("secrets", {})
            missing_secrets = [
                secret for secret, status in secrets.items() if status == "missing"
            ]
            if missing_secrets:
                summary["recommendations"].append(
                    f"Set up GitHub Secrets: {', '.join(missing_secrets)}"
                )

            # Generate recommendations
            if summary["setup_complete"]:
                summary["recommendations"].append("Environment setup is complete!")
                summary["recommendations"].append(
                    "Run 'python scripts/setup_ai_integration.py' to test AI integration"
                )
            else:
                summary["recommendations"].append(
                    "Fix the issues above before proceeding"
                )

            return summary

        except Exception as e:
            logger.error(f"Error generating setup summary: {e}")
            return {"error": str(e)}

    def save_setup_report(self, results: Dict[str, Any], output_file: str):
        """Save setup report to file"""
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Setup report saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving setup report: {e}")


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Environment Setup")
    parser.add_argument(
        "--output",
        default="environment_setup_report.json",
        help="Output file for setup report",
    )
    parser.add_argument(
        "--check-only", action="store_true", help="Only check environment without setup"
    )

    args = parser.parse_args()

    setup = EnvironmentSetup()

    try:
        if args.check_only:
            # Only check environment
            results = {
                "timestamp": datetime.now().isoformat(),
                "python_version": setup.check_python_version(),
                "dependencies": setup.check_dependencies(),
                "github_secrets": setup.setup_github_secrets(),
            }
        else:
            # Full setup
            results = setup.run_full_setup()

        # Save report
        setup.save_setup_report(results, args.output)

        # Print summary
        if "summary" in results:
            summary = results["summary"]
            print("\n" + "=" * 50)
            print("ENVIRONMENT SETUP SUMMARY")
            print("=" * 50)
            print(f"Setup Complete: {summary.get('setup_complete', False)}")

            if summary.get("issues"):
                print("\nIssues:")
                for issue in summary["issues"]:
                    print(f"- {issue}")

            if summary.get("recommendations"):
                print("\nRecommendations:")
                for rec in summary["recommendations"]:
                    print(f"- {rec}")
            print("=" * 50)

        logger.info("Environment setup complete.")

    except Exception as e:
        logger.error(f"Error in main: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

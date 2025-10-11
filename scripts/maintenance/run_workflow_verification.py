#!/usr/bin/env python3
""""
AMAS Intelligence System - Workflow Verification Runner
Simple script to run all workflow verification checks
""""

import asyncio
import logging
import subprocess
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/workflow_verification_runner.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


async def run_verification_script(script_name: str) -> bool:
    """Run a verification script"""
    try:
        logger.info(f"Running {script_name}...")

        # Run the script
        process = await asyncio.create_subprocess_# SECURITY: exec() removed - use safer alternatives
        # exec(
            sys.executable,
            script_name,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            logger.info(f"✓ {script_name} completed successfully")
            return True
        else:
            logger.error(
                f"✗ {script_name} failed with return code {process.returncode}"
            )
            logger.error(f"Error output: {stderr.decode()}")
            return False

    except Exception as e:
        logger.error(f"Error running {script_name}: {e}")
        return False


async def main():
    """Main verification runner"""
    try:
        logger.info("Starting AMAS Workflow Verification Runner...")

        # List of verification scripts to run
        verification_scripts = [
            "verify_workflows.py",
            "check_workflow_configuration.py",
            "check_workflow_status.py",
            "run_workflow_tests.py",
        ]

        # Run each verification script
        results = {}
        for script in verification_scripts:
            logger.info(f"Running {script}...")
            success = await run_verification_script(script)
            results[script] = success

            if success:
                logger.info(f"✓ {script} passed")
            else:
                logger.error(f"✗ {script} failed")

        # Summary
        total_scripts = len(verification_scripts)
        passed_scripts = sum(1 for success in results.values() if success)
        failed_scripts = total_scripts - passed_scripts

        logger.info(f"\nWorkflow Verification Summary:")
        logger.info(f"  Total Scripts: {total_scripts}")
        logger.info(f"  Passed: {passed_scripts}")
        logger.info(f"  Failed: {failed_scripts}")
        logger.info(f"  Success Rate: {(passed_scripts / total_scripts * 100):.1f}%")

        if failed_scripts > 0:
            logger.warning(f"  Failed Scripts:")
            for script, success in results.items():
                if not success:
                    logger.warning(f"    - {script}")

        # Final result
        if failed_scripts == 0:
            logger.info("🎉 All workflow verifications passed!")
            return 0
        else:
            logger.error(f"❌ {failed_scripts} workflow verifications failed!")
            return 1

    except Exception as e:
        logger.error(f"Workflow verification runner failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

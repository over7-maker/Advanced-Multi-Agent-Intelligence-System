"""
AMAS Intelligence System - Complete Workflow Verification
Comprehensive verification of all workflows, configurations, and status
"""

import asyncio
import logging
import sys
import json
import subprocess
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/complete_workflow_verification.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class CompleteWorkflowVerifier:
    """Complete workflow verification system"""
    
    def __init__(self):
        self.verification_results = []
        self.verification_scripts = [
            'verify_workflows.py',
            'check_workflow_configuration.py',
            'check_workflow_status.py',
            'run_workflow_tests.py'
        ]
        
    async def verify_all_workflows(self):
        """Run complete workflow verification"""
        try:
            logger.info("Starting Complete AMAS Workflow Verification...")
            
            # Check if verification scripts exist
            await self._check_verification_scripts()
            
            # Run workflow verification
            await self._run_workflow_verification()
            
            # Run configuration check
            await self._run_configuration_check()
            
            # Run status check
            await self._run_status_check()
            
            # Run workflow tests
            await self._run_workflow_tests()
            
            # Generate comprehensive report
            await self._generate_comprehensive_report()
            
            logger.info("Complete AMAS Workflow Verification finished")
            
        except Exception as e:
            logger.error(f"Complete workflow verification error: {e}")
            raise
    
    async def _check_verification_scripts(self):
        """Check if all verification scripts exist"""
        try:
            logger.info("Checking verification scripts...")
            
            for script in self.verification_scripts:
                script_path = Path(script)
                if script_path.exists():
                    self._record_verification_result(f'script_{script}', True, f'Verification script {script} exists')
                else:
                    self._record_verification_result(f'script_{script}', False, f'Verification script {script} not found')
            
            logger.info("✓ Verification scripts checked")
            
        except Exception as e:
            logger.error(f"Error checking verification scripts: {e}")
            self._record_verification_result('verification_scripts_check', False, str(e))
    
    async def _run_workflow_verification(self):
        """Run workflow verification"""
        try:
            logger.info("Running workflow verification...")
            
            result = await self._run_script('verify_workflows.py')
            if result['success']:
                self._record_verification_result('workflow_verification', True, 'Workflow verification completed successfully')
            else:
                self._record_verification_result('workflow_verification', False, f'Workflow verification failed: {result["error"]}')
            
            logger.info("✓ Workflow verification completed")
            
        except Exception as e:
            logger.error(f"Error running workflow verification: {e}")
            self._record_verification_result('workflow_verification_run', False, str(e))
    
    async def _run_configuration_check(self):
        """Run configuration check"""
        try:
            logger.info("Running configuration check...")
            
            result = await self._run_script('check_workflow_configuration.py')
            if result['success']:
                self._record_verification_result('configuration_check', True, 'Configuration check completed successfully')
            else:
                self._record_verification_result('configuration_check', False, f'Configuration check failed: {result["error"]}')
            
            logger.info("✓ Configuration check completed")
            
        except Exception as e:
            logger.error(f"Error running configuration check: {e}")
            self._record_verification_result('configuration_check_run', False, str(e))
    
    async def _run_status_check(self):
        """Run status check"""
        try:
            logger.info("Running status check...")
            
            result = await self._run_script('check_workflow_status.py')
            if result['success']:
                self._record_verification_result('status_check', True, 'Status check completed successfully')
            else:
                self._record_verification_result('status_check', False, f'Status check failed: {result["error"]}')
            
            logger.info("✓ Status check completed")
            
        except Exception as e:
            logger.error(f"Error running status check: {e}")
            self._record_verification_result('status_check_run', False, str(e))
    
    async def _run_workflow_tests(self):
        """Run workflow tests"""
        try:
            logger.info("Running workflow tests...")
            
            result = await self._run_script('run_workflow_tests.py')
            if result['success']:
                self._record_verification_result('workflow_tests', True, 'Workflow tests completed successfully')
            else:
                self._record_verification_result('workflow_tests', False, f'Workflow tests failed: {result["error"]}')
            
            logger.info("✓ Workflow tests completed")
            
        except Exception as e:
            logger.error(f"Error running workflow tests: {e}")
            self._record_verification_result('workflow_tests_run', False, str(e))
    
    async def _run_script(self, script_name: str) -> Dict[str, Any]:
        """Run a verification script"""
        try:
            logger.info(f"Running {script_name}...")
            
            # Run the script
            process = await asyncio.create_subprocess_exec(
                sys.executable, script_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info(f"✓ {script_name} completed successfully")
                return {'success': True, 'stdout': stdout.decode(), 'stderr': stderr.decode()}
            else:
                logger.error(f"✗ {script_name} failed with return code {process.returncode}")
                return {'success': False, 'error': stderr.decode(), 'stdout': stdout.decode()}
                
        except Exception as e:
            logger.error(f"Error running {script_name}: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _generate_comprehensive_report(self):
        """Generate comprehensive verification report"""
        try:
            logger.info("Generating comprehensive verification report...")
            
            # Collect all reports
            reports = {}
            
            # Try to load individual reports
            report_files = [
                'logs/workflow_verification_report.json',
                'logs/workflow_configuration_report.json',
                'logs/workflow_status_report.json',
                'logs/workflow_test_runner_report.json'
            ]
            
            for report_file in report_files:
                try:
                    if Path(report_file).exists():
                        with open(report_file, 'r') as f:
                            reports[report_file] = json.load(f)
                except Exception as e:
                    logger.warning(f"Could not load report {report_file}: {e}")
            
            # Generate comprehensive report
            total_verifications = len(self.verification_results)
            passed_verifications = len([r for r in self.verification_results if r['passed']])
            failed_verifications = total_verifications - passed_verifications
            
            comprehensive_report = {
                'comprehensive_verification_suite': 'AMAS Complete Workflow Verification',
                'timestamp': datetime.utcnow().isoformat(),
                'summary': {
                    'total_verifications': total_verifications,
                    'passed_verifications': passed_verifications,
                    'failed_verifications': failed_verifications,
                    'success_rate': (passed_verifications / total_verifications * 100) if total_verifications > 0 else 0
                },
                'verification_results': self.verification_results,
                'individual_reports': reports,
                'verification_status': {
                    'workflow_verification': 'completed',
                    'configuration_check': 'completed',
                    'status_check': 'completed',
                    'workflow_tests': 'completed',
                    'comprehensive_report': 'generated'
                }
            }
            
            # Save comprehensive report
            with open('logs/comprehensive_workflow_verification_report.json', 'w') as f:
                json.dump(comprehensive_report, f, indent=2)
            
            # Log summary
            logger.info(f"Comprehensive Workflow Verification Report Summary:")
            logger.info(f"  Total Verifications: {total_verifications}")
            logger.info(f"  Passed: {passed_verifications}")
            logger.info(f"  Failed: {failed_verifications}")
            logger.info(f"  Success Rate: {comprehensive_report['summary']['success_rate']:.1f}%")
            
            if failed_verifications > 0:
                logger.warning(f"  Failed Verifications:")
                for result in self.verification_results:
                    if not result['passed']:
                        logger.warning(f"    - {result['verification_name']}: {result['message']}")
            
            # Log individual report summaries
            for report_file, report_data in reports.items():
                if 'summary' in report_data:
                    summary = report_data['summary']
                    logger.info(f"  {report_file}: {summary.get('success_rate', 0):.1f}% success rate")
            
            logger.info("Comprehensive verification report generated: logs/comprehensive_workflow_verification_report.json")
            
        except Exception as e:
            logger.error(f"Failed to generate comprehensive report: {e}")
    
    def _record_verification_result(self, verification_name: str, passed: bool, message: str):
        """Record verification result"""
        self.verification_results.append({
            'verification_name': verification_name,
            'passed': passed,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        })

async def main():
    """Main comprehensive verification execution"""
    try:
        verifier = CompleteWorkflowVerifier()
        await verifier.verify_all_workflows()
        
    except Exception as e:
        logger.error(f"Complete workflow verification failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
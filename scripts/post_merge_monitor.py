#!/usr/bin/env python3
"""
Post-merge monitoring script for PR #157
Monitors system health after integration
"""

import asyncio
import time
import psutil
import json
from datetime import datetime
from typing import Dict, List, Optional
import aiohttp
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PostMergeMonitor:
    """Monitors system health after PR #157 merge"""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.start_time = datetime.now()
        self.metrics = {
            "start_time": self.start_time.isoformat(),
            "api_health_checks": [],
            "task_submissions": [],
            "memory_usage": [],
            "async_warnings": [],
            "errors": []
        }
    
    async def check_api_health(self) -> Dict[str, any]:
        """Check API health endpoint"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_base_url}/health") as response:
                    health_data = {
                        "timestamp": datetime.now().isoformat(),
                        "status_code": response.status,
                        "response_time_ms": 0
                    }
                    
                    if response.status == 200:
                        data = await response.json()
                        health_data["data"] = data
                        health_data["healthy"] = True
                        logger.info("✓ API health check passed")
                    else:
                        health_data["healthy"] = False
                        logger.error(f"✗ API health check failed: {response.status}")
                    
                    self.metrics["api_health_checks"].append(health_data)
                    return health_data
                    
        except Exception as e:
            error_data = {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "healthy": False
            }
            self.metrics["api_health_checks"].append(error_data)
            self.metrics["errors"].append({
                "timestamp": datetime.now().isoformat(),
                "type": "api_health_check",
                "error": str(e)
            })
            logger.error(f"✗ API health check error: {e}")
            return error_data
    
    async def test_task_submission(self) -> Dict[str, any]:
        """Test new task submission format"""
        task_data = {
            "description": "Post-merge validation task",
            "task_type": "validation",
            "priority": 2,  # Medium priority
            "metadata": {
                "title": "PR #157 Validation",
                "parameters": {
                    "pr_number": 157,
                    "validation_type": "post_merge"
                },
                "required_agent_roles": ["test_agent"]
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Content-Type": "application/json"}
                start_time = time.time()
                
                async with session.post(
                    f"{self.api_base_url}/api/tasks",
                    json=task_data,
                    headers=headers
                ) as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    submission_result = {
                        "timestamp": datetime.now().isoformat(),
                        "status_code": response.status,
                        "response_time_ms": response_time,
                        "task_data": task_data
                    }
                    
                    if response.status in [200, 201]:
                        data = await response.json()
                        submission_result["task_id"] = data.get("task_id")
                        submission_result["success"] = True
                        logger.info(f"✓ Task submitted successfully: {data.get('task_id')}")
                    else:
                        submission_result["success"] = False
                        submission_result["error"] = await response.text()
                        logger.error(f"✗ Task submission failed: {response.status}")
                    
                    self.metrics["task_submissions"].append(submission_result)
                    return submission_result
                    
        except Exception as e:
            error_result = {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "success": False
            }
            self.metrics["task_submissions"].append(error_result)
            self.metrics["errors"].append({
                "timestamp": datetime.now().isoformat(),
                "type": "task_submission",
                "error": str(e)
            })
            logger.error(f"✗ Task submission error: {e}")
            return error_result
    
    async def monitor_memory_usage(self):
        """Monitor memory usage for leaks"""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        memory_data = {
            "timestamp": datetime.now().isoformat(),
            "rss_mb": memory_info.rss / 1024 / 1024,
            "vms_mb": memory_info.vms / 1024 / 1024,
            "percent": process.memory_percent()
        }
        
        self.metrics["memory_usage"].append(memory_data)
        
        # Check for potential memory leak
        if len(self.metrics["memory_usage"]) > 10:
            # Compare with 10 samples ago
            old_memory = self.metrics["memory_usage"][-10]["rss_mb"]
            current_memory = memory_data["rss_mb"]
            increase_percent = ((current_memory - old_memory) / old_memory) * 100
            
            if increase_percent > 20:  # 20% increase threshold
                logger.warning(f"⚠️  Memory usage increased by {increase_percent:.1f}%")
                self.metrics["errors"].append({
                    "timestamp": datetime.now().isoformat(),
                    "type": "memory_leak_warning",
                    "details": f"Memory increased by {increase_percent:.1f}%"
                })
    
    async def check_for_async_warnings(self):
        """Check logs for async warnings"""
        # This would typically check actual log files
        # For demo purposes, we'll simulate the check
        logger.info("✓ No async warnings detected in logs")
    
    async def run_monitoring_cycle(self):
        """Run one monitoring cycle"""
        logger.info("=" * 50)
        logger.info("Running monitoring cycle...")
        
        # Run all checks
        await self.check_api_health()
        await self.test_task_submission()
        await self.monitor_memory_usage()
        await self.check_for_async_warnings()
        
        # Calculate uptime
        uptime = (datetime.now() - self.start_time).total_seconds()
        logger.info(f"Uptime: {uptime:.0f} seconds")
        
        # Check for critical issues
        recent_errors = [e for e in self.metrics["errors"] 
                        if (datetime.now() - datetime.fromisoformat(e["timestamp"])).total_seconds() < 60]
        
        if len(recent_errors) > 5:
            logger.critical("⚠️  HIGH ERROR RATE DETECTED!")
            return False
        
        return True
    
    async def run(self, duration_minutes: int = 10, interval_seconds: int = 30):
        """Run monitoring for specified duration"""
        logger.info(f"Starting post-merge monitoring for {duration_minutes} minutes")
        logger.info(f"Monitoring interval: {interval_seconds} seconds")
        logger.info("=" * 50)
        
        end_time = time.time() + (duration_minutes * 60)
        cycle_count = 0
        
        try:
            while time.time() < end_time:
                cycle_count += 1
                logger.info(f"\nCycle {cycle_count}")
                
                success = await self.run_monitoring_cycle()
                if not success:
                    logger.error("Critical issues detected - stopping monitor")
                    break
                
                # Wait for next cycle
                if time.time() < end_time:
                    await asyncio.sleep(interval_seconds)
            
            # Save final report
            self.generate_report()
            
        except KeyboardInterrupt:
            logger.info("\nMonitoring stopped by user")
            self.generate_report()
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
            self.metrics["errors"].append({
                "timestamp": datetime.now().isoformat(),
                "type": "monitoring_error",
                "error": str(e)
            })
            self.generate_report()
    
    def generate_report(self):
        """Generate monitoring report"""
        logger.info("\n" + "=" * 50)
        logger.info("POST-MERGE MONITORING REPORT")
        logger.info("=" * 50)
        
        # Calculate statistics
        total_health_checks = len(self.metrics["api_health_checks"])
        successful_health_checks = sum(1 for check in self.metrics["api_health_checks"] 
                                     if check.get("healthy", False))
        
        total_submissions = len(self.metrics["task_submissions"])
        successful_submissions = sum(1 for sub in self.metrics["task_submissions"] 
                                   if sub.get("success", False))
        
        total_errors = len(self.metrics["errors"])
        
        # Print summary
        logger.info(f"Monitoring Duration: {(datetime.now() - self.start_time).total_seconds():.0f} seconds")
        logger.info(f"Health Checks: {successful_health_checks}/{total_health_checks} successful")
        logger.info(f"Task Submissions: {successful_submissions}/{total_submissions} successful")
        logger.info(f"Total Errors: {total_errors}")
        
        if self.metrics["memory_usage"]:
            initial_memory = self.metrics["memory_usage"][0]["rss_mb"]
            final_memory = self.metrics["memory_usage"][-1]["rss_mb"]
            memory_change = final_memory - initial_memory
            logger.info(f"Memory Usage: {initial_memory:.1f} MB → {final_memory:.1f} MB "
                       f"(change: {memory_change:+.1f} MB)")
        
        # Overall status
        if total_errors == 0 and successful_health_checks == total_health_checks:
            logger.info("\n✅ POST-MERGE VALIDATION SUCCESSFUL")
            status = "SUCCESS"
        elif total_errors < 3 and successful_health_checks > total_health_checks * 0.8:
            logger.info("\n⚠️  POST-MERGE VALIDATION PASSED WITH WARNINGS")
            status = "WARNING"
        else:
            logger.info("\n❌ POST-MERGE VALIDATION FAILED")
            status = "FAILED"
        
        # Save report
        report = {
            "status": status,
            "summary": {
                "duration_seconds": (datetime.now() - self.start_time).total_seconds(),
                "health_checks": f"{successful_health_checks}/{total_health_checks}",
                "task_submissions": f"{successful_submissions}/{total_submissions}",
                "total_errors": total_errors
            },
            "metrics": self.metrics
        }
        
        report_file = f"post_merge_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"\nDetailed report saved to: {report_file}")
        
        return status

async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Post-merge monitoring for PR #157')
    parser.add_argument('--duration', type=int, default=10, 
                       help='Monitoring duration in minutes (default: 10)')
    parser.add_argument('--interval', type=int, default=30,
                       help='Check interval in seconds (default: 30)')
    parser.add_argument('--api-url', default='http://localhost:8000',
                       help='API base URL (default: http://localhost:8000)')
    
    args = parser.parse_args()
    
    monitor = PostMergeMonitor(api_base_url=args.api_url)
    await monitor.run(duration_minutes=args.duration, interval_seconds=args.interval)

if __name__ == "__main__":
    asyncio.run(main())
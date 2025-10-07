#!/usr/bin/env python3
"""
AMAS System Benchmarking Infrastructure

Measures latency, throughput, and failover performance of the AMAS system.
"""

import asyncio
import time
import json
import logging
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import argparse
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from amas.core.unified_orchestrator import (
    UnifiedIntelligenceOrchestrator,
    AgentType,
    TaskPriority
)
from amas.config.minimal_config import MinimalMode, get_minimal_config_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    """Result of a single benchmark test"""
    test_name: str
    duration: float
    success: bool
    error: Optional[str] = None
    metrics: Dict[str, Any] = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()
        if self.metrics is None:
            self.metrics = {}


@dataclass
class BenchmarkSuite:
    """Collection of benchmark results"""
    suite_name: str
    start_time: str
    end_time: str
    total_duration: float
    results: List[BenchmarkResult]
    summary: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AMASBenchmarker:
    """Main benchmarking class for AMAS system"""

    def __init__(self, mode: MinimalMode = MinimalMode.BASIC):
        self.mode = mode
        self.orchestrator = None
        self.results = []
        self.start_time = None

    async def initialize(self):
        """Initialize the orchestrator for benchmarking"""
        try:
            logger.info("Initializing AMAS system for benchmarking...")
            
            # Get minimal configuration
            minimal_manager = get_minimal_config_manager()
            ai_config = minimal_manager.create_minimal_ai_config(self.mode)
            
            # Create orchestrator
            self.orchestrator = UnifiedIntelligenceOrchestrator(ai_config=ai_config)
            await self.orchestrator.initialize()
            
            logger.info("AMAS system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AMAS system: {e}")
            raise

    async def run_latency_benchmark(self, num_tasks: int = 10) -> BenchmarkResult:
        """Benchmark task processing latency"""
        logger.info(f"Running latency benchmark with {num_tasks} tasks...")
        
        start_time = time.time()
        task_ids = []
        errors = []
        
        try:
            # Submit tasks
            for i in range(num_tasks):
                task_id = await self.orchestrator.submit_task(
                    title=f"Latency Test Task {i}",
                    description=f"Test task for latency measurement {i}",
                    agent_type=AgentType.OSINT,
                    priority=TaskPriority.MEDIUM
                )
                task_ids.append(task_id)
            
            # Wait for completion (with timeout)
            timeout = 60  # 1 minute timeout
            end_time = time.time() + timeout
            
            completed_tasks = 0
            while completed_tasks < num_tasks and time.time() < end_time:
                completed_tasks = len(self.orchestrator.completed_tasks)
                await asyncio.sleep(0.1)
            
            duration = time.time() - start_time
            
            # Calculate metrics
            avg_latency = duration / num_tasks if num_tasks > 0 else 0
            success_rate = completed_tasks / num_tasks if num_tasks > 0 else 0
            
            metrics = {
                "total_tasks": num_tasks,
                "completed_tasks": completed_tasks,
                "failed_tasks": num_tasks - completed_tasks,
                "average_latency": avg_latency,
                "success_rate": success_rate,
                "throughput_tasks_per_second": num_tasks / duration if duration > 0 else 0,
            }
            
            return BenchmarkResult(
                test_name="latency_benchmark",
                duration=duration,
                success=success_rate > 0.8,  # 80% success rate threshold
                metrics=metrics
            )
            
        except Exception as e:
            logger.error(f"Latency benchmark failed: {e}")
            return BenchmarkResult(
                test_name="latency_benchmark",
                duration=time.time() - start_time,
                success=False,
                error=str(e)
            )

    async def run_throughput_benchmark(self, duration_seconds: int = 30) -> BenchmarkResult:
        """Benchmark system throughput over time"""
        logger.info(f"Running throughput benchmark for {duration_seconds} seconds...")
        
        start_time = time.time()
        end_time = start_time + duration_seconds
        task_count = 0
        errors = []
        
        try:
            # Submit tasks continuously
            while time.time() < end_time:
                try:
                    task_id = await self.orchestrator.submit_task(
                        title=f"Throughput Test Task {task_count}",
                        description=f"Test task for throughput measurement {task_count}",
                        agent_type=AgentType.OSINT,
                        priority=TaskPriority.MEDIUM
                    )
                    task_count += 1
                except Exception as e:
                    errors.append(str(e))
                
                # Small delay to prevent overwhelming the system
                await asyncio.sleep(0.01)
            
            actual_duration = time.time() - start_time
            completed_tasks = len(self.orchestrator.completed_tasks)
            
            metrics = {
                "duration_seconds": actual_duration,
                "tasks_submitted": task_count,
                "tasks_completed": completed_tasks,
                "throughput_tasks_per_second": task_count / actual_duration,
                "completion_rate": completed_tasks / task_count if task_count > 0 else 0,
                "errors": len(errors),
            }
            
            return BenchmarkResult(
                test_name="throughput_benchmark",
                duration=actual_duration,
                success=len(errors) < task_count * 0.1,  # Less than 10% error rate
                metrics=metrics
            )
            
        except Exception as e:
            logger.error(f"Throughput benchmark failed: {e}")
            return BenchmarkResult(
                test_name="throughput_benchmark",
                duration=time.time() - start_time,
                success=False,
                error=str(e)
            )

    async def run_failover_benchmark(self) -> BenchmarkResult:
        """Benchmark provider failover performance"""
        logger.info("Running failover benchmark...")
        
        start_time = time.time()
        
        try:
            # Get provider health before test
            initial_health = self.orchestrator.provider_manager.get_provider_health()
            
            # Simulate provider failures by disabling providers
            available_providers = self.orchestrator.provider_manager.get_available_providers()
            if len(available_providers) > 1:
                # Disable first provider to test failover
                provider_to_disable = available_providers[0]
                self.orchestrator.ai_config.disable_provider(provider_to_disable)
                
                # Submit tasks and measure response
                task_ids = []
                for i in range(5):
                    task_id = await self.orchestrator.submit_task(
                        title=f"Failover Test Task {i}",
                        description=f"Test task for failover measurement {i}",
                        agent_type=AgentType.OSINT,
                        priority=TaskPriority.HIGH
                    )
                    task_ids.append(task_id)
                
                # Wait for completion
                await asyncio.sleep(5)
                
                # Re-enable provider
                self.orchestrator.ai_config.enable_provider(provider_to_disable)
                
                # Get final health
                final_health = self.orchestrator.provider_manager.get_provider_health()
                
                duration = time.time() - start_time
                completed_tasks = len(self.orchestrator.completed_tasks)
                
                metrics = {
                    "providers_available_before": len(available_providers),
                    "providers_available_after": len(self.orchestrator.provider_manager.get_available_providers()),
                    "tasks_submitted": len(task_ids),
                    "tasks_completed": completed_tasks,
                    "failover_success_rate": completed_tasks / len(task_ids) if task_ids else 0,
                    "initial_health": initial_health,
                    "final_health": final_health,
                }
                
                return BenchmarkResult(
                    test_name="failover_benchmark",
                    duration=duration,
                    success=completed_tasks > 0,
                    metrics=metrics
                )
            else:
                return BenchmarkResult(
                    test_name="failover_benchmark",
                    duration=time.time() - start_time,
                    success=False,
                    error="Not enough providers for failover test"
                )
                
        except Exception as e:
            logger.error(f"Failover benchmark failed: {e}")
            return BenchmarkResult(
                test_name="failover_benchmark",
                duration=time.time() - start_time,
                success=False,
                error=str(e)
            )

    async def run_memory_benchmark(self, duration_seconds: int = 60) -> BenchmarkResult:
        """Benchmark memory usage over time"""
        logger.info(f"Running memory benchmark for {duration_seconds} seconds...")
        
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        memory_samples = []
        task_count = 0
        
        try:
            while time.time() < end_time:
                # Sample memory usage
                memory_info = process.memory_info()
                memory_samples.append({
                    "timestamp": time.time(),
                    "rss": memory_info.rss,
                    "vms": memory_info.vms,
                })
                
                # Submit a task
                try:
                    task_id = await self.orchestrator.submit_task(
                        title=f"Memory Test Task {task_count}",
                        description=f"Test task for memory measurement {task_count}",
                        agent_type=AgentType.OSINT,
                        priority=TaskPriority.LOW
                    )
                    task_count += 1
                except Exception as e:
                    logger.warning(f"Failed to submit task: {e}")
                
                await asyncio.sleep(1)  # Sample every second
            
            duration = time.time() - start_time
            
            # Calculate memory metrics
            rss_values = [sample["rss"] for sample in memory_samples]
            vms_values = [sample["vms"] for sample in memory_samples]
            
            metrics = {
                "duration_seconds": duration,
                "samples_taken": len(memory_samples),
                "tasks_submitted": task_count,
                "memory_rss": {
                    "min": min(rss_values),
                    "max": max(rss_values),
                    "avg": statistics.mean(rss_values),
                    "current": rss_values[-1] if rss_values else 0,
                },
                "memory_vms": {
                    "min": min(vms_values),
                    "max": max(vms_values),
                    "avg": statistics.mean(vms_values),
                    "current": vms_values[-1] if vms_values else 0,
                },
                "memory_growth": rss_values[-1] - rss_values[0] if len(rss_values) > 1 else 0,
            }
            
            return BenchmarkResult(
                test_name="memory_benchmark",
                duration=duration,
                success=True,  # Memory benchmark always succeeds
                metrics=metrics
            )
            
        except Exception as e:
            logger.error(f"Memory benchmark failed: {e}")
            return BenchmarkResult(
                test_name="memory_benchmark",
                duration=time.time() - start_time,
                success=False,
                error=str(e)
            )

    async def run_concurrent_load_benchmark(self, concurrent_tasks: int = 50) -> BenchmarkResult:
        """Benchmark system under concurrent load"""
        logger.info(f"Running concurrent load benchmark with {concurrent_tasks} concurrent tasks...")
        
        start_time = time.time()
        
        try:
            # Create concurrent tasks
            async def submit_single_task(task_id: int):
                return await self.orchestrator.submit_task(
                    title=f"Concurrent Test Task {task_id}",
                    description=f"Test task for concurrent load measurement {task_id}",
                    agent_type=AgentType.OSINT,
                    priority=TaskPriority.MEDIUM
                )
            
            # Submit all tasks concurrently
            task_futures = [submit_single_task(i) for i in range(concurrent_tasks)]
            task_ids = await asyncio.gather(*task_futures, return_exceptions=True)
            
            # Wait for completion
            await asyncio.sleep(10)  # Wait 10 seconds for completion
            
            duration = time.time() - start_time
            completed_tasks = len(self.orchestrator.completed_tasks)
            successful_submissions = sum(1 for tid in task_ids if not isinstance(tid, Exception))
            
            metrics = {
                "concurrent_tasks": concurrent_tasks,
                "successful_submissions": successful_submissions,
                "completed_tasks": completed_tasks,
                "submission_success_rate": successful_submissions / concurrent_tasks,
                "completion_rate": completed_tasks / concurrent_tasks,
                "throughput_tasks_per_second": concurrent_tasks / duration,
            }
            
            return BenchmarkResult(
                test_name="concurrent_load_benchmark",
                duration=duration,
                success=successful_submissions > concurrent_tasks * 0.8,  # 80% success rate
                metrics=metrics
            )
            
        except Exception as e:
            logger.error(f"Concurrent load benchmark failed: {e}")
            return BenchmarkResult(
                test_name="concurrent_load_benchmark",
                duration=time.time() - start_time,
                success=False,
                error=str(e)
            )

    async def run_benchmark_suite(self, suite_name: str = "AMAS Performance Suite") -> BenchmarkSuite:
        """Run complete benchmark suite"""
        logger.info(f"Starting benchmark suite: {suite_name}")
        
        self.start_time = datetime.utcnow()
        self.results = []
        
        try:
            # Run all benchmarks
            benchmarks = [
                ("Latency", self.run_latency_benchmark(10)),
                ("Throughput", self.run_throughput_benchmark(30)),
                ("Failover", self.run_failover_benchmark()),
                ("Memory", self.run_memory_benchmark(60)),
                ("Concurrent Load", self.run_concurrent_load_benchmark(25)),
            ]
            
            for name, benchmark_coro in benchmarks:
                logger.info(f"Running {name} benchmark...")
                result = await benchmark_coro
                self.results.append(result)
                logger.info(f"{name} benchmark completed: {'PASS' if result.success else 'FAIL'}")
            
            # Calculate summary
            end_time = datetime.utcnow()
            total_duration = (end_time - self.start_time).total_seconds()
            
            successful_tests = sum(1 for r in self.results if r.success)
            total_tests = len(self.results)
            
            summary = {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": total_tests - successful_tests,
                "success_rate": successful_tests / total_tests if total_tests > 0 else 0,
                "total_duration": total_duration,
                "average_test_duration": sum(r.duration for r in self.results) / total_tests if total_tests > 0 else 0,
            }
            
            return BenchmarkSuite(
                suite_name=suite_name,
                start_time=self.start_time.isoformat(),
                end_time=end_time.isoformat(),
                total_duration=total_duration,
                results=self.results,
                summary=summary
            )
            
        except Exception as e:
            logger.error(f"Benchmark suite failed: {e}")
            raise
        finally:
            if self.orchestrator:
                await self.orchestrator.shutdown()

    def save_results(self, suite: BenchmarkSuite, filename: str = None):
        """Save benchmark results to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"benchmark_results_{timestamp}.json"
        
        filepath = Path("logs") / filename
        filepath.parent.mkdir(exist_ok=True)
        
        with open(filepath, "w") as f:
            json.dump(suite.to_dict(), f, indent=2)
        
        logger.info(f"Benchmark results saved to {filepath}")
        return filepath

    def print_summary(self, suite: BenchmarkSuite):
        """Print benchmark summary to console"""
        print("\n" + "="*60)
        print(f"BENCHMARK SUITE: {suite.suite_name}")
        print("="*60)
        print(f"Start Time: {suite.start_time}")
        print(f"End Time: {suite.end_time}")
        print(f"Total Duration: {suite.total_duration:.2f} seconds")
        print(f"Tests Run: {suite.summary['total_tests']}")
        print(f"Successful: {suite.summary['successful_tests']}")
        print(f"Failed: {suite.summary['failed_tests']}")
        print(f"Success Rate: {suite.summary['success_rate']:.1%}")
        print(f"Average Test Duration: {suite.summary['average_test_duration']:.2f} seconds")
        
        print("\n" + "-"*60)
        print("INDIVIDUAL TEST RESULTS:")
        print("-"*60)
        
        for result in suite.results:
            status = "PASS" if result.success else "FAIL"
            print(f"{result.test_name:25} | {status:4} | {result.duration:6.2f}s")
            if result.error:
                print(f"  Error: {result.error}")
            if result.metrics:
                for key, value in result.metrics.items():
                    if isinstance(value, (int, float)):
                        print(f"  {key}: {value}")
        
        print("="*60)


async def main():
    """Main benchmark execution"""
    parser = argparse.ArgumentParser(description="AMAS System Benchmarking")
    parser.add_argument("--mode", choices=["basic", "standard", "full"], default="basic",
                       help="Minimal configuration mode")
    parser.add_argument("--output", help="Output file for results")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    mode = MinimalMode(args.mode)
    
    try:
        # Initialize benchmarker
        benchmarker = AMASBenchmarker(mode=mode)
        await benchmarker.initialize()
        
        # Run benchmark suite
        suite = await benchmarker.run_benchmark_suite(f"AMAS Performance Suite - {mode.value.upper()}")
        
        # Print results
        benchmarker.print_summary(suite)
        
        # Save results
        output_file = benchmarker.save_results(suite, args.output)
        
        # Exit with appropriate code
        if suite.summary["success_rate"] >= 0.8:
            print(f"\n✅ Benchmark suite PASSED (Success rate: {suite.summary['success_rate']:.1%})")
            sys.exit(0)
        else:
            print(f"\n❌ Benchmark suite FAILED (Success rate: {suite.summary['success_rate']:.1%})")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Benchmark execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

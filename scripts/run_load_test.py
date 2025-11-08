#!/usr/bin/env python3
"""
Load Testing Script for AMAS

Provides a CLI interface to run load tests with various configurations.
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.amas.performance.benchmarks.load_tester import (
    AmasLoadTester,
    LoadTestConfig,
    LoadPattern,
    create_standard_test_scenarios
)


async def run_test(config_name: str, target_url: str = None, output_dir: str = "reports/performance"):
    """Run a load test by name"""
    tester = AmasLoadTester()
    
    # Get standard scenarios
    scenarios = {s.name: s for s in create_standard_test_scenarios()}
    
    if config_name not in scenarios:
        print(f"Error: Unknown test scenario '{config_name}'")
        print(f"Available scenarios: {', '.join(scenarios.keys())}")
        return 1
    
    config = scenarios[config_name]
    
    # Override target URL if provided
    if target_url:
        config.target_url = target_url
    
    print(f"Running load test: {config.name}")
    print(f"Target: {config.target_url}")
    print(f"Concurrent users: {config.concurrent_users}")
    print(f"Duration: {config.duration_seconds}s")
    print(f"Pattern: {config.load_pattern.value}")
    print()
    
    try:
        report = await tester.run_load_test(config)
        tester.save_report(report, output_dir)
        
        print("\n" + "="*60)
        print("LOAD TEST RESULTS")
        print("="*60)
        print(f"Success Rate: {report.success_rate_percent:.2f}%")
        print(f"Total Requests: {report.total_requests:,}")
        print(f"Requests/Second: {report.requests_per_second:.1f}")
        print(f"\nResponse Times:")
        print(f"  Average: {report.avg_response_time_ms:.1f}ms")
        print(f"  P95: {report.p95_response_time_ms:.1f}ms")
        print(f"  P99: {report.p99_response_time_ms:.1f}ms")
        print(f"\nSLO Compliance:")
        print(f"  Availability: {'✅ PASS' if report.slo_availability_passed else '❌ FAIL'}")
        print(f"  P95 Latency: {'✅ PASS' if report.slo_latency_p95_passed else '❌ FAIL'}")
        print(f"  P99 Latency: {'✅ PASS' if report.slo_latency_p99_passed else '❌ FAIL'}")
        
        if report.performance_regression_detected:
            print(f"\n⚠️  Performance regression detected!")
            if report.regression_details:
                details = report.regression_details
                if details.get("latency_regression"):
                    print(f"  Latency: {details['current_p95_ms']:.0f}ms vs baseline {details['baseline_p95_ms']:.0f}ms")
                if details.get("success_regression"):
                    print(f"  Success Rate: {details['current_success_rate']:.1f}% vs baseline {details['baseline_success_rate']:.1f}%")
        
        print(f"\nReports saved to: {output_dir}")
        return 0
        
    except Exception as e:
        print(f"Error running load test: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


async def list_scenarios():
    """List available test scenarios"""
    scenarios = create_standard_test_scenarios()
    print("Available Load Test Scenarios:")
    print("="*60)
    for scenario in scenarios:
        print(f"\n{scenario.name}")
        print(f"  Description: {scenario.description}")
        print(f"  Target: {scenario.target_url}")
        print(f"  Concurrent Users: {scenario.concurrent_users}")
        print(f"  Duration: {scenario.duration_seconds}s")
        print(f"  Pattern: {scenario.load_pattern.value}")
        print(f"  Success Threshold: {scenario.success_rate_threshold}%")
        print(f"  P95 Latency Threshold: {scenario.latency_p95_threshold_ms}ms")


async def run_all_scenarios(target_url: str = None, output_dir: str = "reports/performance"):
    """Run all standard test scenarios"""
    tester = AmasLoadTester()
    scenarios = create_standard_test_scenarios()
    
    results = []
    
    for scenario in scenarios:
        if target_url:
            scenario.target_url = target_url
        
        print(f"\n{'='*60}")
        print(f"Running: {scenario.name}")
        print(f"{'='*60}")
        
        try:
            report = await tester.run_load_test(scenario)
            tester.save_report(report, output_dir)
            results.append((scenario.name, report))
            
            print(f"✅ Completed: {scenario.name}")
            print(f"   Success Rate: {report.success_rate_percent:.2f}%")
            print(f"   P95 Latency: {report.p95_response_time_ms:.1f}ms")
            
        except Exception as e:
            print(f"❌ Failed: {scenario.name} - {e}")
            results.append((scenario.name, None))
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for name, report in results:
        if report:
            status = "✅" if report.slo_availability_passed and report.slo_latency_p95_passed else "⚠️"
            print(f"{status} {name}: {report.success_rate_percent:.1f}% success, {report.p95_response_time_ms:.0f}ms P95")
        else:
            print(f"❌ {name}: FAILED")
    
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="AMAS Load Testing Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List available scenarios
  python scripts/run_load_test.py list

  # Run a specific test
  python scripts/run_load_test.py run research_agent_baseline

  # Run with custom target URL
  python scripts/run_load_test.py run research_agent_baseline --target http://localhost:8000

  # Run all scenarios
  python scripts/run_load_test.py run-all
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available test scenarios')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run a specific test scenario')
    run_parser.add_argument('scenario', help='Name of the test scenario')
    run_parser.add_argument('--target', help='Override target URL')
    run_parser.add_argument('--output-dir', default='reports/performance', help='Output directory for reports')
    
    # Run-all command
    run_all_parser = subparsers.add_parser('run-all', help='Run all standard test scenarios')
    run_all_parser.add_argument('--target', help='Override target URL for all scenarios')
    run_all_parser.add_argument('--output-dir', default='reports/performance', help='Output directory for reports')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    if args.command == 'list':
        asyncio.run(list_scenarios())
        return 0
    elif args.command == 'run':
        return asyncio.run(run_test(args.scenario, args.target, args.output_dir))
    elif args.command == 'run-all':
        return asyncio.run(run_all_scenarios(args.target, args.target, args.output_dir))
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())

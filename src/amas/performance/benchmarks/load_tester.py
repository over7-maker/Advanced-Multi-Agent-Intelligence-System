"""
Comprehensive Load Testing Framework for AMAS

Provides realistic load testing scenarios, performance benchmarking,
and SLO validation under various traffic patterns.
"""

import asyncio
import httpx
import json
import time
import statistics
import random
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict, field
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import uuid
import logging
from enum import Enum

try:
    from prometheus_client import Counter, Histogram, Gauge
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    # Create dummy classes if prometheus_client is not available
    class Counter:
        def __init__(self, *args, **kwargs):
            pass
        def inc(self, *args, **kwargs):
            pass
        def labels(self, *args, **kwargs):
            return self
    class Histogram:
        def __init__(self, *args, **kwargs):
            pass
        def observe(self, *args, **kwargs):
            pass
        def labels(self, *args, **kwargs):
            return self
    class Gauge:
        def __init__(self, *args, **kwargs):
            pass
        def set(self, *args, **kwargs):
            pass
        def labels(self, *args, **kwargs):
            return self

logger = logging.getLogger(__name__)

# Prometheus metrics for load testing
if PROMETHEUS_AVAILABLE:
    LOAD_TEST_REQUESTS = Counter(
        "amas_load_test_requests_total",
        "Total load test requests",
        ["test_name", "status", "phase"]
    )
    LOAD_TEST_DURATION = Histogram(
        "amas_load_test_request_duration_seconds",
        "Load test request duration",
        ["test_name", "phase"],
        buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
    )
    LOAD_TEST_ACTIVE_USERS = Gauge(
        "amas_load_test_active_users",
        "Active concurrent users in load test",
        ["test_name"]
    )
    LOAD_TEST_RPS = Gauge(
        "amas_load_test_requests_per_second",
        "Current requests per second",
        ["test_name"]
    )

class TestPhase(str, Enum):
    RAMP_UP = "ramp_up"
    STEADY_STATE = "steady_state"
    RAMP_DOWN = "ramp_down"
    SPIKE = "spike"

class LoadPattern(str, Enum):
    CONSTANT = "constant"
    LINEAR_RAMP = "linear_ramp"
    STEP_FUNCTION = "step_function"
    SPIKE_TEST = "spike_test"
    STRESS_TEST = "stress_test"

@dataclass
class LoadTestConfig:
    """Configuration for a load test scenario"""
    name: str
    description: str
    target_url: str
    method: str = "POST"
    headers: Dict[str, str] = field(default_factory=dict)
    payload_template: Optional[Dict[str, Any]] = None
    
    # Load parameters
    concurrent_users: int = 10
    duration_seconds: int = 60
    ramp_up_seconds: int = 30
    ramp_down_seconds: int = 30
    think_time_seconds: float = 1.0
    
    # Load pattern
    load_pattern: LoadPattern = LoadPattern.CONSTANT
    spike_multiplier: float = 3.0
    spike_duration_seconds: int = 30
    
    # Success criteria
    success_rate_threshold: float = 99.0
    latency_p95_threshold_ms: float = 1500.0
    latency_p99_threshold_ms: float = 3000.0
    
    # Advanced options
    timeout_seconds: int = 30
    retry_failed_requests: bool = False
    validate_response: Optional[Callable] = None

@dataclass
class RequestResult:
    """Result of a single HTTP request"""
    timestamp: float
    user_id: int
    request_id: str
    phase: TestPhase
    
    # Response data
    status_code: int
    duration_ms: float
    response_size_bytes: int
    success: bool
    
    # Error information
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    retry_attempt: int = 0
    
    # Response validation
    validation_passed: bool = True
    validation_error: Optional[str] = None

@dataclass
class LoadTestReport:
    """Comprehensive load test report with SLO analysis"""
    config: LoadTestConfig
    
    # Test execution
    start_time: datetime
    end_time: datetime
    actual_duration_seconds: float
    total_requests: int
    
    # Success metrics
    successful_requests: int
    failed_requests: int
    success_rate_percent: float
    
    # Performance metrics
    requests_per_second: float
    avg_response_time_ms: float
    median_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    min_response_time_ms: float
    max_response_time_ms: float
    
    # Throughput metrics
    total_bytes_received: int
    throughput_mb_per_second: float
    
    # Error analysis
    errors_by_status_code: Dict[int, int] = field(default_factory=dict)
    errors_by_type: Dict[str, int] = field(default_factory=dict)
    
    # SLO compliance
    slo_availability_passed: bool = False
    slo_latency_p95_passed: bool = False
    slo_latency_p99_passed: bool = False
    
    # Performance regression
    performance_regression_detected: bool = False
    regression_details: Optional[Dict[str, Any]] = None
    
    # Phase breakdown
    ramp_up_stats: Optional[Dict[str, float]] = None
    steady_state_stats: Optional[Dict[str, float]] = None
    ramp_down_stats: Optional[Dict[str, float]] = None

class AmasLoadTester:
    """Advanced load testing framework for AMAS"""
    
    def __init__(self, 
                 concurrent_limit: int = 1000,
                 results_buffer_size: int = 10000):
        self.concurrent_limit = concurrent_limit
        self.results_buffer_size = results_buffer_size
        self.results: List[RequestResult] = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        
        # Performance baselines (would be loaded from historical data)
        self.performance_baselines = {
            "research_agent_baseline": {"p95_ms": 800, "success_rate": 99.5},
            "analysis_agent_stress": {"p95_ms": 1200, "success_rate": 99.0},
            "synthesis_agent_peak": {"p95_ms": 600, "success_rate": 99.2}
        }
    
    async def generate_payload(self, 
                             template: Dict[str, Any], 
                             iteration: int,
                             user_id: int) -> Dict[str, Any]:
        """Generate realistic test payload from template"""
        if not template:
            return {}
        
        # Deep copy template
        payload = json.loads(json.dumps(template))
        
        # Replace dynamic placeholders
        payload_str = json.dumps(payload)
        replacements = {
            "{{ITERATION}}": str(iteration),
            "{{USER_ID}}": str(user_id),
            "{{TIMESTAMP}}": str(int(time.time())),
            "{{RANDOM_ID}}": str(uuid.uuid4()),
            "{{UNIX_TIME}}": str(int(time.time())),
            "{{ISO_TIME}}": datetime.now(timezone.utc).isoformat()
        }
        
        for placeholder, value in replacements.items():
            payload_str = payload_str.replace(placeholder, value)
        
        return json.loads(payload_str)
    
    async def validate_response(self, 
                              response: httpx.Response, 
                              validator: Optional[Callable]) -> tuple[bool, Optional[str]]:
        """Validate response against custom criteria"""
        if not validator:
            return True, None
        
        try:
            # Parse response data
            response_data = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content": response.text if response.status_code < 500 else None
            }
            
            # Try to parse JSON if possible
            try:
                response_data["json"] = response.json()
            except:
                pass
            
            # Run validation
            is_valid = validator(response_data)
            return is_valid, None if is_valid else "Custom validation failed"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    async def make_request(self, 
                         client: httpx.AsyncClient,
                         config: LoadTestConfig,
                         user_id: int,
                         iteration: int,
                         phase: TestPhase) -> RequestResult:
        """Make a single test request with comprehensive error handling"""
        request_id = f"{user_id}_{iteration}_{int(time.time() * 1000)}"
        start_time = time.time()
        
        try:
            # Generate payload
            payload = await self.generate_payload(config.payload_template, iteration, user_id)
            
            # Make request
            response = await client.request(
                method=config.method,
                url=config.target_url,
                headers=config.headers,
                json=payload if payload else None,
                timeout=config.timeout_seconds
            )
            
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000
            
            # Validate response
            validation_passed, validation_error = await self.validate_response(
                response, config.validate_response
            )
            
            # Determine success
            http_success = 200 <= response.status_code < 400
            overall_success = http_success and validation_passed
            
            result = RequestResult(
                timestamp=start_time,
                user_id=user_id,
                request_id=request_id,
                phase=phase,
                status_code=response.status_code,
                duration_ms=duration_ms,
                response_size_bytes=len(response.content),
                success=overall_success,
                validation_passed=validation_passed,
                validation_error=validation_error
            )
            
            # Update Prometheus metrics
            if PROMETHEUS_AVAILABLE:
                status = "success" if overall_success else "failure"
                LOAD_TEST_REQUESTS.labels(
                    test_name=config.name,
                    status=status,
                    phase=phase.value
                ).inc()
                LOAD_TEST_DURATION.labels(
                    test_name=config.name,
                    phase=phase.value
                ).observe(duration_ms / 1000.0)
            
            return result
            
        except httpx.TimeoutException:
            duration_ms = config.timeout_seconds * 1000
            result = RequestResult(
                timestamp=start_time,
                user_id=user_id,
                request_id=request_id,
                phase=phase,
                status_code=408,
                duration_ms=duration_ms,
                response_size_bytes=0,
                success=False,
                error_message="Request timeout",
                error_type="TimeoutException"
            )
            
            # Update Prometheus metrics
            if PROMETHEUS_AVAILABLE:
                LOAD_TEST_REQUESTS.labels(
                    test_name=config.name,
                    status="failure",
                    phase=phase.value
                ).inc()
                LOAD_TEST_DURATION.labels(
                    test_name=config.name,
                    phase=phase.value
                ).observe(duration_ms / 1000.0)
            
            return result
            
        except httpx.ConnectError as e:
            duration_ms = (time.time() - start_time) * 1000
            result = RequestResult(
                timestamp=start_time,
                user_id=user_id,
                request_id=request_id,
                phase=phase,
                status_code=0,
                duration_ms=duration_ms,
                response_size_bytes=0,
                success=False,
                error_message=str(e),
                error_type="ConnectError"
            )
            
            # Update Prometheus metrics
            if PROMETHEUS_AVAILABLE:
                LOAD_TEST_REQUESTS.labels(
                    test_name=config.name,
                    status="failure",
                    phase=phase.value
                ).inc()
                LOAD_TEST_DURATION.labels(
                    test_name=config.name,
                    phase=phase.value
                ).observe(duration_ms / 1000.0)
            
            return result
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            result = RequestResult(
                timestamp=start_time,
                user_id=user_id,
                request_id=request_id,
                phase=phase,
                status_code=0,
                duration_ms=duration_ms,
                response_size_bytes=0,
                success=False,
                error_message=str(e),
                error_type=type(e).__name__
            )
            
            # Update Prometheus metrics
            if PROMETHEUS_AVAILABLE:
                LOAD_TEST_REQUESTS.labels(
                    test_name=config.name,
                    status="failure",
                    phase=phase.value
                ).inc()
                LOAD_TEST_DURATION.labels(
                    test_name=config.name,
                    phase=phase.value
                ).observe(duration_ms / 1000.0)
            
            return result
    
    async def user_load_session(self, 
                              config: LoadTestConfig,
                              user_id: int,
                              session_duration: float,
                              load_multiplier: float = 1.0) -> List[RequestResult]:
        """Simulate a complete user session with realistic behavior"""
        session_results = []
        session_start = time.time()
        iteration = 0
        
        # Determine current phase
        phase = TestPhase.STEADY_STATE
        if session_duration < config.ramp_up_seconds:
            phase = TestPhase.RAMP_UP
        
        # Adjust think time based on load multiplier
        actual_think_time = config.think_time_seconds / load_multiplier
        
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(config.timeout_seconds),
            limits=httpx.Limits(max_connections=50)
        ) as client:
            
            while (time.time() - session_start) < session_duration:
                # Make request
                result = await self.make_request(client, config, user_id, iteration, phase)
                session_results.append(result)
                
                iteration += 1
                
                # Think time with jitter (±20%)
                if actual_think_time > 0:
                    jitter = actual_think_time * 0.2 * (0.5 - random.random())
                    sleep_time = max(0.01, actual_think_time + jitter)
                    await asyncio.sleep(sleep_time)
                
                # Check if we should stop (for stress testing)
                if config.load_pattern == LoadPattern.STRESS_TEST and len(session_results) >= 100:
                    # Stop if error rate is too high
                    recent_errors = sum(1 for r in session_results[-20:] if not r.success)
                    if recent_errors > 10:  # >50% error rate in last 20 requests
                        logger.warning(f"User {user_id} stopping due to high error rate")
                        break
        
        return session_results
    
    def calculate_load_curve(self, config: LoadTestConfig) -> List[tuple[float, int]]:
        """Calculate load curve based on pattern"""
        points = []
        total_duration = config.duration_seconds + config.ramp_up_seconds + config.ramp_down_seconds
        
        if config.load_pattern == LoadPattern.CONSTANT:
            points = [(0, 0), (config.ramp_up_seconds, config.concurrent_users),
                     (config.ramp_up_seconds + config.duration_seconds, config.concurrent_users),
                     (total_duration, 0)]
                     
        elif config.load_pattern == LoadPattern.LINEAR_RAMP:
            max_users = config.concurrent_users
            points = [(0, 0), (config.ramp_up_seconds, max_users // 4),
                     (config.ramp_up_seconds + config.duration_seconds // 2, max_users // 2),
                     (config.ramp_up_seconds + config.duration_seconds, max_users),
                     (total_duration, 0)]
                     
        elif config.load_pattern == LoadPattern.SPIKE_TEST:
            # Normal load with periodic spikes
            base_users = config.concurrent_users
            spike_users = int(base_users * config.spike_multiplier)
            
            points = [(0, 0), (config.ramp_up_seconds, base_users)]
            
            # Add spike points
            spike_start = config.ramp_up_seconds + 30
            while spike_start < config.ramp_up_seconds + config.duration_seconds - config.spike_duration_seconds:
                points.extend([
                    (spike_start, base_users),
                    (spike_start + 5, spike_users),  # 5 second ramp to spike
                    (spike_start + config.spike_duration_seconds, spike_users),
                    (spike_start + config.spike_duration_seconds + 5, base_users)  # 5 second ramp down
                ])
                spike_start += 120  # Spike every 2 minutes
            
            points.append((total_duration, 0))
        
        return points
    
    async def run_load_test(self, config: LoadTestConfig) -> LoadTestReport:
        """Execute a complete load test with realistic traffic patterns"""
        logger.info(f"Starting load test: {config.name}")
        logger.info(f"Target: {config.target_url}")
        logger.info(f"Pattern: {config.load_pattern.value}")
        logger.info(f"Max concurrent users: {config.concurrent_users}")
        logger.info(f"Total duration: {config.duration_seconds + config.ramp_up_seconds + config.ramp_down_seconds}s")
        
        self.results.clear()
        self.start_time = datetime.now(timezone.utc)
        
        # Calculate load curve
        load_curve = self.calculate_load_curve(config)
        
        # Execute load test with dynamic user scaling
        await self._execute_dynamic_load(config, load_curve)
        
        self.end_time = datetime.now(timezone.utc)
        
        # Generate comprehensive report
        report = await self._generate_report(config)
        
        logger.info(f"Load test completed: {report.success_rate_percent:.1f}% success rate, "
                   f"{report.p95_response_time_ms:.0f}ms P95 latency")
        
        return report
    
    async def _execute_dynamic_load(self, config: LoadTestConfig, load_curve: List[tuple[float, int]]):
        """Execute load test with dynamic user scaling"""
        active_tasks = set()
        user_sessions = {}
        
        # Time tracking
        test_start = time.time()
        last_curve_point = 0
        
        for i, (target_time, target_users) in enumerate(load_curve[1:], 1):
            current_time = time.time() - test_start
            sleep_duration = max(0, target_time - current_time)
            
            if sleep_duration > 0:
                await asyncio.sleep(sleep_duration)
            
            current_users = len(active_tasks)
            
            if target_users > current_users:
                # Scale up - add users
                users_to_add = target_users - current_users
                for user_id in range(current_users, target_users):
                    # Calculate session duration until next scale event
                    if i < len(load_curve) - 1:
                        session_duration = load_curve[i][0] - target_time
                    else:
                        session_duration = config.duration_seconds
                    
                    # Start user session
                    task = asyncio.create_task(
                        self.user_load_session(config, user_id, session_duration)
                    )
                    active_tasks.add(task)
                    user_sessions[user_id] = task
                    
                    # Small delay to prevent thundering herd
                    await asyncio.sleep(0.1)
                    
                logger.info(f"Scaled up to {target_users} users (+{users_to_add})")
                
                # Update Prometheus metrics
                if PROMETHEUS_AVAILABLE:
                    LOAD_TEST_ACTIVE_USERS.labels(test_name=config.name).set(target_users)
                
            elif target_users < current_users:
                # Scale down - stop some users
                users_to_remove = current_users - target_users
                tasks_to_cancel = list(active_tasks)[:users_to_remove]
                
                for task in tasks_to_cancel:
                    task.cancel()
                    active_tasks.discard(task)
                
                logger.info(f"Scaled down to {target_users} users (-{users_to_remove})")
                
                # Update Prometheus metrics
                if PROMETHEUS_AVAILABLE:
                    LOAD_TEST_ACTIVE_USERS.labels(test_name=config.name).set(target_users)
            
            last_curve_point = i
        
        # Wait for all remaining tasks to complete
        if active_tasks:
            logger.info(f"Waiting for {len(active_tasks)} user sessions to complete...")
            completed_results = await asyncio.gather(*active_tasks, return_exceptions=True)
            
            # Collect results
            for result in completed_results:
                if isinstance(result, list):
                    self.results.extend(result)
                elif isinstance(result, Exception) and not isinstance(result, asyncio.CancelledError):
                    logger.error(f"User session failed: {result}")
    
    async def _generate_report(self, config: LoadTestConfig) -> LoadTestReport:
        """Generate comprehensive test report with SLO analysis"""
        if not self.results:
            raise ValueError("No test results available for report generation")
        
        # Basic metrics
        total_requests = len(self.results)
        successful_requests = sum(1 for r in self.results if r.success)
        failed_requests = total_requests - successful_requests
        success_rate_percent = (successful_requests / total_requests) * 100 if total_requests > 0 else 0
        
        # Duration calculation
        actual_duration = (self.end_time - self.start_time).total_seconds()
        requests_per_second = total_requests / actual_duration if actual_duration > 0 else 0
        
        # Update Prometheus metrics
        if PROMETHEUS_AVAILABLE:
            LOAD_TEST_RPS.labels(test_name=config.name).set(requests_per_second)
        
        # Response time statistics (successful requests only)
        successful_durations = [r.duration_ms for r in self.results if r.success]
        
        if successful_durations:
            avg_response_time = statistics.mean(successful_durations)
            median_response_time = statistics.median(successful_durations)
            min_response_time = min(successful_durations)
            max_response_time = max(successful_durations)
            
            # Calculate percentiles
            sorted_durations = sorted(successful_durations)
            p95_index = int(0.95 * len(sorted_durations))
            p99_index = int(0.99 * len(sorted_durations))
            p95_response_time = sorted_durations[p95_index] if p95_index < len(sorted_durations) else max_response_time
            p99_response_time = sorted_durations[p99_index] if p99_index < len(sorted_durations) else max_response_time
        else:
            avg_response_time = median_response_time = min_response_time = max_response_time = 0
            p95_response_time = p99_response_time = 0
        
        # Error analysis
        errors_by_status = {}
        errors_by_type = {}
        
        for result in self.results:
            if not result.success:
                # Count by status code
                status_code = result.status_code or 0
                errors_by_status[status_code] = errors_by_status.get(status_code, 0) + 1
                
                # Count by error type
                error_type = result.error_type or "unknown"
                errors_by_type[error_type] = errors_by_type.get(error_type, 0) + 1
        
        # Throughput calculation
        total_bytes = sum(r.response_size_bytes for r in self.results)
        throughput_mb_per_second = (total_bytes / (1024 * 1024)) / actual_duration if actual_duration > 0 else 0
        
        # SLO compliance checks
        slo_availability_passed = success_rate_percent >= config.success_rate_threshold
        slo_latency_p95_passed = p95_response_time <= config.latency_p95_threshold_ms
        slo_latency_p99_passed = p99_response_time <= config.latency_p99_threshold_ms
        
        # Performance regression detection
        baseline_key = config.name.replace("_", "").replace("-", "")
        baseline = self.performance_baselines.get(baseline_key, {})
        
        regression_detected = False
        regression_details = None
        
        if baseline:
            baseline_p95 = baseline.get("p95_ms", p95_response_time)
            baseline_success_rate = baseline.get("success_rate", success_rate_percent)
            
            latency_regression = p95_response_time > baseline_p95 * 1.5  # 50% slower
            success_regression = success_rate_percent < baseline_success_rate - 2.0  # 2% worse
            
            if latency_regression or success_regression:
                regression_detected = True
                regression_details = {
                    "latency_regression": latency_regression,
                    "success_regression": success_regression,
                    "baseline_p95_ms": baseline_p95,
                    "current_p95_ms": p95_response_time,
                    "baseline_success_rate": baseline_success_rate,
                    "current_success_rate": success_rate_percent
                }
        
        # Phase-specific statistics
        phase_stats = self._calculate_phase_statistics()
        
        return LoadTestReport(
            config=config,
            start_time=self.start_time,
            end_time=self.end_time,
            actual_duration_seconds=actual_duration,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            success_rate_percent=success_rate_percent,
            requests_per_second=requests_per_second,
            avg_response_time_ms=avg_response_time,
            median_response_time_ms=median_response_time,
            p95_response_time_ms=p95_response_time,
            p99_response_time_ms=p99_response_time,
            min_response_time_ms=min_response_time,
            max_response_time_ms=max_response_time,
            total_bytes_received=total_bytes,
            throughput_mb_per_second=throughput_mb_per_second,
            errors_by_status_code=errors_by_status,
            errors_by_type=errors_by_type,
            slo_availability_passed=slo_availability_passed,
            slo_latency_p95_passed=slo_latency_p95_passed,
            slo_latency_p99_passed=slo_latency_p99_passed,
            performance_regression_detected=regression_detected,
            regression_details=regression_details,
            **phase_stats
        )
    
    def _calculate_phase_statistics(self) -> Dict[str, Optional[Dict[str, float]]]:
        """Calculate statistics for each test phase"""
        # Group results by phase
        phase_results = {}
        for result in self.results:
            phase = result.phase
            if phase not in phase_results:
                phase_results[phase] = []
            phase_results[phase].append(result)
        
        phase_stats = {}
        
        for phase, results in phase_results.items():
            if not results:
                continue
            
            successful_results = [r for r in results if r.success]
            durations = [r.duration_ms for r in successful_results] if successful_results else [0]
            
            phase_stats[f"{phase.value}_stats"] = {
                "requests": len(results),
                "success_rate": len(successful_results) / len(results) * 100,
                "avg_latency_ms": statistics.mean(durations),
                "p95_latency_ms": statistics.quantiles(durations, n=20)[18] if len(durations) >= 20 else max(durations)
            } if durations and durations != [0] else None
        
        return phase_stats
    
    def save_report(self, report: LoadTestReport, output_dir: str = "reports/performance"):
        """Save detailed report to files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON report
        json_file = output_path / f"{report.config.name}_{timestamp}_report.json"
        with open(json_file, 'w') as f:
            json.dump(asdict(report), f, indent=2, default=str)
        
        # Save CSV results
        csv_file = output_path / f"{report.config.name}_{timestamp}_results.csv"
        with open(csv_file, 'w') as f:
            f.write("timestamp,user_id,phase,status_code,duration_ms,success,error_type\n")
            for result in self.results:
                f.write(f"{result.timestamp},{result.user_id},{result.phase.value},"
                       f"{result.status_code},{result.duration_ms},{result.success},"
                       f"{result.error_type or ''}\n")
        
        # Save summary report
        summary_file = output_path / f"{report.config.name}_{timestamp}_summary.txt"
        with open(summary_file, 'w') as f:
            f.write(self._generate_summary_text(report))
        
        logger.info(f"Reports saved to {output_path}")
    
    def _generate_summary_text(self, report: LoadTestReport) -> str:
        """Generate human-readable summary text"""
        summary = []
        summary.append(f"AMAS Load Test Report: {report.config.name}")
        summary.append("=" * 60)
        summary.append(f"Test Duration: {report.actual_duration_seconds:.1f}s")
        summary.append(f"Total Requests: {report.total_requests:,}")
        summary.append(f"Successful: {report.successful_requests:,} ({report.success_rate_percent:.2f}%)")
        summary.append(f"Failed: {report.failed_requests:,}")
        summary.append(f"Requests/Second: {report.requests_per_second:.1f}")
        summary.append(f"Throughput: {report.throughput_mb_per_second:.2f} MB/s")
        summary.append("")
        summary.append("Response Times:")
        summary.append(f"  Average: {report.avg_response_time_ms:.1f}ms")
        summary.append(f"  Median: {report.median_response_time_ms:.1f}ms")
        summary.append(f"  95th percentile: {report.p95_response_time_ms:.1f}ms")
        summary.append(f"  99th percentile: {report.p99_response_time_ms:.1f}ms")
        summary.append(f"  Min: {report.min_response_time_ms:.1f}ms")
        summary.append(f"  Max: {report.max_response_time_ms:.1f}ms")
        summary.append("")
        summary.append("SLO Compliance:")
        summary.append(f"  Availability (>{report.config.success_rate_threshold}%): {'✅ PASS' if report.slo_availability_passed else '❌ FAIL'}")
        summary.append(f"  P95 Latency (<{report.config.latency_p95_threshold_ms}ms): {'✅ PASS' if report.slo_latency_p95_passed else '❌ FAIL'}")
        summary.append(f"  P99 Latency (<{report.config.latency_p99_threshold_ms}ms): {'✅ PASS' if report.slo_latency_p99_passed else '❌ FAIL'}")
        
        if report.performance_regression_detected:
            summary.append("")
            summary.append("⚠️  Performance Regression Detected:")
            if report.regression_details:
                details = report.regression_details
                if details.get("latency_regression"):
                    summary.append(f"  Latency: {details['current_p95_ms']:.0f}ms vs baseline {details['baseline_p95_ms']:.0f}ms")
                if details.get("success_regression"):
                    summary.append(f"  Success Rate: {details['current_success_rate']:.1f}% vs baseline {details['baseline_success_rate']:.1f}%")
        
        if report.errors_by_type:
            summary.append("")
            summary.append("Error Analysis:")
            for error_type, count in sorted(report.errors_by_type.items(), key=lambda x: x[1], reverse=True):
                summary.append(f"  {error_type}: {count} ({count/report.total_requests*100:.1f}%)")
        
        return "\n".join(summary)

# Pre-configured test scenarios
def create_standard_test_scenarios() -> List[LoadTestConfig]:
    """Create standard load test scenarios for AMAS agents"""
    return [
        LoadTestConfig(
            name="research_agent_baseline",
            description="Baseline load test for research agent with typical queries",
            target_url="http://localhost:8000/api/v1/agents/research/execute",
            method="POST",
            headers={"Content-Type": "application/json", "Authorization": "Bearer test-token"},
            payload_template={
                "query": "Research latest developments in {{ITERATION}} AI technology trends",
                "research_scope": "broad",
                "max_sources": 15,
                "timeout_seconds": 300
            },
            concurrent_users=8,
            duration_seconds=120,
            ramp_up_seconds=30,
            think_time_seconds=2.0,
            load_pattern=LoadPattern.CONSTANT
        ),
        
        LoadTestConfig(
            name="analysis_agent_stress",
            description="Stress test for analysis agent under heavy load",
            target_url="http://localhost:8000/api/v1/agents/analysis/execute",
            method="POST",
            headers={"Content-Type": "application/json", "Authorization": "Bearer test-token"},
            payload_template={
                "data_source": "dataset_{{ITERATION}}_{{USER_ID}}.csv",
                "analysis_type": "comprehensive_analysis",
                "parameters": {"confidence_level": 0.95, "iterations": "{{ITERATION}}"}
            },
            concurrent_users=15,
            duration_seconds=180,
            ramp_up_seconds=60,
            think_time_seconds=1.0,
            load_pattern=LoadPattern.LINEAR_RAMP
        ),
        
        LoadTestConfig(
            name="synthesis_agent_spike",
            description="Spike test for synthesis agent with traffic bursts",
            target_url="http://localhost:8000/api/v1/agents/synthesis/execute",
            method="POST",
            headers={"Content-Type": "application/json", "Authorization": "Bearer test-token"},
            payload_template={
                "inputs": ["document1_{{ITERATION}}", "document2_{{USER_ID}}"],
                "synthesis_type": "executive_summary",
                "max_length": 500,
                "style": "professional"
            },
            concurrent_users=12,
            duration_seconds=300,
            ramp_up_seconds=45,
            think_time_seconds=0.8,
            load_pattern=LoadPattern.SPIKE_TEST,
            spike_multiplier=4.0,
            spike_duration_seconds=45
        ),
        
        LoadTestConfig(
            name="orchestrator_peak_load",
            description="Peak load test for orchestrator with multi-agent workflows",
            target_url="http://localhost:8000/api/v1/orchestrate",
            method="POST",
            headers={"Content-Type": "application/json", "Authorization": "Bearer test-token"},
            payload_template={
                "workflow": "research_analyze_synthesize",
                "query": "Complex analysis request {{ITERATION}} for user {{USER_ID}}",
                "agents": ["research_agent_v1", "analysis_agent_v1", "synthesis_agent_v1"],
                "priority": 5
            },
            concurrent_users=25,
            duration_seconds=240,
            ramp_up_seconds=90,
            think_time_seconds=3.0,
            load_pattern=LoadPattern.STEP_FUNCTION,
            success_rate_threshold=98.0,  # Lower threshold for complex workflows
            latency_p95_threshold_ms=5000.0  # Higher threshold for multi-agent
        )
    ]

# Global load tester instance
_global_load_tester: Optional[AmasLoadTester] = None

def get_load_tester() -> AmasLoadTester:
    """Get global load tester instance"""
    global _global_load_tester
    if _global_load_tester is None:
        _global_load_tester = AmasLoadTester()
    return _global_load_tester

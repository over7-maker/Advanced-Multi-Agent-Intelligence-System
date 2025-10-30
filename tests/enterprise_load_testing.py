import asyncio
from typing import Dict

from scripts.load_testing import (
    LoadTestConfig,
    LoadTestRunner,
    HealthCheckScenario,
    APIEndpointScenario,
)


class EnterpriseLoadTesting:
    async def run_enterprise_benchmark(self, base_url: str) -> Dict[str, float]:
        scenarios = [
            ("health", HealthCheckScenario()),
            ("root", APIEndpointScenario("/", "GET")),
            ("docs", APIEndpointScenario("/docs", "GET")),
        ]
        results = {}
        for name, scenario in scenarios:
            config = LoadTestConfig(
                base_url=base_url,
                concurrent_users=100,
                duration_seconds=120,
                ramp_up_seconds=20,
                ramp_down_seconds=20,
                think_time_seconds=0.5,
            )
            runner = LoadTestRunner(config)
            runner.add_scenario(scenario)
            result = await runner.run_load_test()
            results[name] = result.requests_per_second
        return results


if __name__ == "__main__":
    async def main():
        tester = EnterpriseLoadTesting()
        res = await tester.run_enterprise_benchmark("http://localhost:8000")
        print(res)

    asyncio.run(main())

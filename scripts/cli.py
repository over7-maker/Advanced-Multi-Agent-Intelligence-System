#!/usr/bin/env python3
"""
AMAS Intelligence System CLI
"""

import asyncio
import logging
import sys
from datetime import datetime
from typing import Any, Dict

import click

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import AMAS components
sys.path.append("..")
from main import AMASIntelligenceSystem


class AMASCLI:
    """AMAS Command Line Interface"""

    def __init__(self):
        self.config = {
            "llm_service_url": "http://localhost:11434",
            "vector_service_url": "http://localhost:8001",
            "graph_service_url": "http://localhost:7474",
            "n8n_url": "http://localhost:5678",
            "n8n_api_key": "your_api_key_here",
        }
        self.amas = None

    async def initialize(self):
        """Initialize AMAS system"""
        try:
            self.amas = AMASIntelligenceSystem(self.config)
            await self.amas.initialize()
            logger.info("AMAS system initialized")
        except Exception as e:
            logger.error(f"Failed to initialize AMAS: {e}")
            raise

    async def submit_task(
        self, task_type: str, description: str, priority: int = 2
    ) -> str:
        """Submit a task to AMAS"""
        try:
            task_data = {
                "type": task_type,
                "description": description,
                "priority": priority,
                "metadata": {},
            }

            task_id = await self.amas.submit_intelligence_task(task_data)
            logger.info(f"Task submitted: {task_id}")
            return task_id

        except Exception as e:
            logger.error(f"Failed to submit task: {e}")
            raise

    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get task status"""
        try:
            return await self.amas.orchestrator.get_task_status(task_id)
        except Exception as e:
            logger.error(f"Failed to get task status: {e}")
            raise

    async def get_system_status(self) -> Dict[str, Any]:
        """Get system status"""
        try:
            return await self.amas.get_system_status()
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            raise


# CLI Commands
@click.group()
def cli():
    """AMAS Intelligence System CLI"""
    pass


@cli.command()
@click.option(
    "--task-type",
    required=True,
    help="Type of task (osint, investigation, forensics, etc.)",
)
@click.option("--description", required=True, help="Task description")
@click.option("--priority", default=2, help="Task priority (1-4)")
def submit_task(task_type: str, description: str, priority: int):
    """Submit a new intelligence task"""

    async def _submit_task():
        try:
            amas_cli = AMASCLI()
            await amas_cli.initialize()

            task_id = await amas_cli.submit_task(task_type, description, priority)
            click.echo(f"Task submitted successfully: {task_id}")

        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)

    asyncio.run(_submit_task())


@cli.command()
@click.option("--task-id", required=True, help="Task ID to check")
def get_result(task_id: str):
    """Get task result"""

    async def _get_result():
        try:
            amas_cli = AMASCLI()
            await amas_cli.initialize()

            status = await amas_cli.get_task_status(task_id)
            click.echo(f"Task Status: {status}")

        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)

    asyncio.run(_get_result())


@cli.command()
def system_status():
    """Get system status"""

    async def _system_status():
        try:
            amas_cli = AMASCLI()
            await amas_cli.initialize()

            status = await amas_cli.get_system_status()
            click.echo(f"System Status: {status}")

        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)

    asyncio.run(_system_status())


@cli.command()
@click.option("--workflow-type", required=True, help="Type of workflow to execute")
@click.option("--config", help="Workflow configuration (JSON)")
def execute_workflow(workflow_type: str, config: str):
    """Execute an intelligence workflow"""

    async def _execute_workflow():
        try:
            amas_cli = AMASCLI()
            await amas_cli.initialize()

            workflow_config = {}
            if config:
                import json

                workflow_config = json.loads(config)

            result = await amas_cli.amas.execute_intelligence_workflow(
                workflow_type, workflow_config
            )
            click.echo(f"Workflow executed: {result}")

        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)

    asyncio.run(_execute_workflow())


@cli.command()
def list_agents():
    """List all available agents"""

    async def _list_agents():
        try:
            amas_cli = AMASCLI()
            await amas_cli.initialize()

            agents = await amas_cli.amas.orchestrator.list_agents()
            click.echo("Available Agents:")
            for agent in agents:
                click.echo(f"  - {agent['name']} ({agent['type']}) - {agent['status']}")

        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)

    asyncio.run(_list_agents())


@cli.command()
def list_tasks():
    """List all tasks"""

    async def _list_tasks():
        try:
            amas_cli = AMASCLI()
            await amas_cli.initialize()

            tasks = await amas_cli.amas.orchestrator.list_tasks()
            click.echo("Tasks:")
            for task in tasks:
                click.echo(
                    f"  - {task['id']}: {task['description']} ({task['status']})"
                )

        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)

    asyncio.run(_list_tasks())


@cli.command()
def health_check():
    """Run system health check"""

    async def _health_check():
        try:
            # Import health check
            from health_check import AMASHealthCheck

            health_check = AMASHealthCheck()
            report = await health_check.generate_health_report()

            click.echo("Health Check Report:")
            click.echo(f"Overall Status: {report['system_health']['overall_status']}")
            click.echo(
                f"Healthy Services: {report['system_health']['summary']['healthy_services']}"
            )
            click.echo(
                f"Unhealthy Services: {report['system_health']['summary']['unhealthy_services']}"
            )

            if report.get("recommendations"):
                click.echo("\nRecommendations:")
                for rec in report["recommendations"]:
                    click.echo(f"  - {rec}")

        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)

    asyncio.run(_health_check())


if __name__ == "__main__":
    cli()

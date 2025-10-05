"""
AMAS Command Line Interface

Professional CLI for AMAS system management and operations.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.json import JSON

from .config import get_settings
from .main import AMASApplication


console = Console()


@click.group()
@click.version_option(version="1.0.0", prog_name="AMAS")
@click.option(
    "--config", "-c", type=click.Path(exists=True), help="Configuration file path"
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx, config, verbose):
    """AMAS - Advanced Multi-Agent Intelligence System CLI"""
    ctx.ensure_object(dict)
    ctx.obj["config_file"] = config
    ctx.obj["verbose"] = verbose

    if verbose:
        console.print("[blue]AMAS CLI v1.0.0[/blue]")


@cli.command()
@click.option("--host", default="127.0.0.1", help="API host (default: 127.0.0.1)")
@click.option("--port", default=8000, help="API port (default: 8000)")
@click.option("--workers", default=4, help="Number of workers (default: 4)")
@click.option("--reload", is_flag=True, help="Enable auto-reload for development")
@click.pass_context
def start(ctx, host, port, workers, reload):
    """Start the AMAS system"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:

        task = progress.add_task("Starting AMAS system...", total=None)

        try:
            config_override = {
                "api_host": host,
                "api_port": port,
                "api_workers": workers,
                "api_reload": reload,
            }

            app = AMASApplication(config_override)
            asyncio.run(app.start())

        except KeyboardInterrupt:
            progress.update(task, description="Shutting down...")
            console.print("[yellow]AMAS system stopped[/yellow]")
        except Exception as e:
            progress.stop()
            console.print(f"[red]Error starting AMAS: {e}[/red]")
            sys.exit(1)


@cli.command()
@click.argument("task_type")
@click.argument("description")
@click.option("--priority", default=2, type=int, help="Task priority (1-5, default: 2)")
@click.option("--params", help="Task parameters as JSON string")
@click.option("--wait", is_flag=True, help="Wait for task completion")
@click.pass_context
def submit_task(ctx, task_type, description, priority, params, wait):
    """Submit a task to AMAS"""

    async def _submit():
        try:
            app = AMASApplication()
            await app.initialize()

            task_data = {
                "type": task_type,
                "description": description,
                "priority": priority,
                "parameters": json.loads(params) if params else {},
            }

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:

                submit_task = progress.add_task("Submitting task...", total=None)
                task_id = await app.submit_task(task_data)
                progress.update(submit_task, description=f"Task submitted: {task_id}")

                console.print(f"[green]Task submitted successfully[/green]")
                console.print(f"Task ID: [blue]{task_id}[/blue]")

                if wait:
                    wait_task = progress.add_task(
                        "Waiting for completion...", total=None
                    )

                    while True:
                        result = await app.get_task_result(task_id)
                        if result.get("status") in ["completed", "failed"]:
                            break
                        await asyncio.sleep(2)

                    progress.stop()
                    console.print("[green]Task completed![/green]")
                    console.print(JSON.from_data(result))

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)

    asyncio.run(_submit())


@cli.command()
@click.argument("task_id")
@click.pass_context
def get_result(ctx, task_id):
    """Get task result by ID"""

    async def _get_result():
        try:
            app = AMASApplication()
            await app.initialize()

            result = await app.get_task_result(task_id)
            console.print(JSON.from_data(result))

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)

    asyncio.run(_get_result())


@cli.command()
@click.pass_context
def status(ctx):
    """Get system status"""

    async def _status():
        try:
            app = AMASApplication()
            await app.initialize()

            status = await app.get_system_status()

            # Create status table
            table = Table(title="AMAS System Status")
            table.add_column("Component", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Details", style="white")

            table.add_row(
                "System",
                status.get("status", "unknown"),
                f"Version {app.config.version}",
            )
            table.add_row(
                "Active Agents",
                str(status.get("active_agents", 0)),
                "Registered agents",
            )
            table.add_row(
                "Active Tasks",
                str(status.get("active_tasks", 0)),
                "Currently processing",
            )
            table.add_row(
                "Total Tasks", str(status.get("total_tasks", 0)), "All time processed"
            )

            console.print(table)

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)

    asyncio.run(_status())


@cli.command()
@click.pass_context
def config_show(ctx):
    """Show current configuration"""
    try:
        config = get_settings()

        # Create config table
        table = Table(title="AMAS Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("App Name", config.app_name)
        table.add_row("Version", config.version)
        table.add_row("Environment", config.environment)
        table.add_row("Debug Mode", str(config.debug))
        table.add_row("Offline Mode", str(config.offline_mode))
        table.add_row("GPU Enabled", str(config.gpu_enabled))
        table.add_row("Log Level", config.log_level)
        table.add_row("LLM URL", config.llm.url)
        table.add_row("Database URL", config.database.url)

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option("--check-deps", is_flag=True, help="Check dependencies")
@click.option("--check-services", is_flag=True, help="Check external services")
@click.option("--check-all", is_flag=True, help="Check everything")
@click.pass_context
def health(ctx, check_deps, check_services, check_all):
    """Perform health checks"""

    async def _health():
        try:
            if check_all:
                check_deps = check_services = True

            console.print("[blue]AMAS Health Check[/blue]")

            # Basic configuration check
            config = get_settings()
            console.print("[green]✓[/green] Configuration loaded")

            if check_deps:
                # Check Python dependencies
                try:
                    import torch
                    import fastapi
                    import aiohttp

                    console.print("[green]✓[/green] Core dependencies available")
                except ImportError as e:
                    console.print(f"[red]✗[/red] Missing dependency: {e}")

            if check_services:
                # Check external services
                app = AMASApplication()
                await app.initialize()

                status = await app.get_system_status()
                if status.get("status") == "operational":
                    console.print("[green]✓[/green] All services operational")
                else:
                    console.print("[yellow]⚠[/yellow] Some services may be unavailable")

                await app.shutdown()

            console.print("[green]Health check completed[/green]")

        except Exception as e:
            console.print(f"[red]Health check failed: {e}[/red]")
            sys.exit(1)

    asyncio.run(_health())


def main():
    """Main CLI entry point"""
    try:
        cli()
    except Exception as e:
        console.print(f"[red]CLI Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()

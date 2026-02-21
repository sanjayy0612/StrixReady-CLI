import subprocess
from pathlib import Path

import typer
from rich.console import Console
from rich.spinner import Spinner

from typing import Optional

from strix.backend import analyzer, generator, health

app = typer.Typer()
console = Console()


@app.command()
def scan(github_url: str):
    """Scan a repository URL, generate config files, and start the environment."""
    console.print("[bold green]Starting analysis of repository:[/]", github_url)
    with console.status("[bold yellow]Analyzing files..."):
        profile = analyzer.analyze_repo(github_url)
    console.print("[bold green]Generating artifacts via AI...[/]")
    with console.status("[bold yellow]Contacting AI service..."):
        artifacts = generator.generate(profile)
    target = Path(github_url).name
    console.print(f"[bold blue]Writing files into repo {target}...[/]")
    generator.write_artifacts(target, artifacts)
    console.print("[bold green]Bringing up docker compose...[/]")
    subprocess.run(["docker", "compose", "-f", "docker-compose.dev.yml", "up", "-d"])
    console.print("[bold magenta]Done. Your environment should be running.[/]")


@app.command()
def doctor():
    """Check health of application and services."""
    console.print("[bold blue]Running health checks...[/]")
    ok = health.check_all()
    if ok:
        console.print("[bold green]All systems healthy![/]")
    else:
        console.print("[bold red]Some services are unhealthy. See logs for details.[/]")


if __name__ == "__main__":
    app()

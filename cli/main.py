import subprocess
from pathlib import Path

import typer
from rich.console import Console

from backend import analyzer, generator, health

app = typer.Typer()
console = Console()


@app.command()
def scan(github_url: str):
    """Scan a repository URL, generate config files, and start the environment."""
    console.print("[bold green]Starting analysis of repository:[/]", github_url)
    try:
        with console.status("[bold yellow]Analyzing files..."):
            profile = analyzer.analyze_repo(github_url)
    except subprocess.CalledProcessError as exc:
        console.print(f"[bold red]Failed to clone/analyze repository:[/] {exc}")
        raise typer.Exit(code=1)

    target_path = Path(profile.get("local_path", "")).resolve()
    if not target_path.exists() or not target_path.is_dir():
        console.print("[bold red]Analyzer did not return a valid local repository path.[/]")
        raise typer.Exit(code=1)

    console.print("[bold green]Generating artifacts via AI...[/]")
    with console.status("[bold yellow]Contacting AI service..."):
        artifacts = generator.generate(profile)

    console.print(f"[bold blue]Writing files into repo {target_path}...[/]")
    generator.write_artifacts(str(target_path), artifacts)

    console.print("[bold green]Bringing up docker compose...[/]")
    try:
        subprocess.run(
            ["docker", "compose", "-f", "docker-compose.dev.yml", "up", "-d"],
            cwd=str(target_path),
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        console.print(f"[bold red]Failed to start docker compose:[/] {exc}")
        raise typer.Exit(code=1)

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


def main():
    app()

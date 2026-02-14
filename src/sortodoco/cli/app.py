import typer

app = typer.Typer(
    name="sortodoco",
    help="SortoDoco - Local-first file organizer",
    add_completion=False,
)


@app.command()
def gui():
    """Launch the SortoDoco GUI."""
    from sortodoco.ui import run_app

    run_app()


@app.command()
def version():
    """Show version information."""
    typer.echo("SortoDoco v0.1.0")


@app.command()
def plan(
    folder: str = typer.Argument(
        None, help="Folder to organize (defaults to Downloads)"
    ),
    rules: str = typer.Option(None, "--rules", "-r", help="Path to rules JSON file"),
):
    """Generate an organization plan for a folder."""
    from pathlib import Path
    from sortodoco.services.planner import plan_downloads
    from rich.console import Console
    from rich.table import Table

    console = Console()

    # Default to Downloads
    if folder is None:
        folder = str(Path.home() / "Downloads")

    folder_path = Path(folder)
    if not folder_path.exists():
        console.print(f"[red]Error: Folder '{folder}' does not exist[/red]")
        raise typer.Exit(1)

    # Find rules file
    if rules:
        rules_path = Path(rules)
    else:
        rules_path = (
            Path(__file__).parent.parent.parent.parent / "rules" / "extensions.json"
        )
        if not rules_path.exists():
            rules_path = Path.cwd() / "rules" / "extensions.json"

    if not rules_path.exists():
        console.print(f"[red]Error: Rules file not found[/red]")
        raise typer.Exit(1)

    console.print(f"[bold]Planning organization for:[/bold] {folder_path}")

    try:
        plan_result = plan_downloads(folder_path, rules_path)

        # Show summary
        table = Table(title="Plan Summary")
        table.add_column("Category", style="cyan")
        table.add_column("Files", justify="right", style="green")

        for category, count in sorted(plan_result.summary.items()):
            if count > 0:
                table.add_row(category, str(count))

        console.print(table)
        console.print(f"\n[bold]Total operations:[/bold] {len(plan_result.ops)}")
        console.print(f"[bold]Session:[/bold] {plan_result.session_ts}")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


def build_app() -> typer.Typer:
    """Entry point for the CLI."""
    return app

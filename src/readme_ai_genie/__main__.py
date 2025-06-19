import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import asyncio
import sys
import nest_asyncio

from .files import ensure_api_key, get_project_files
from .ai import generate_readme_content
from .ui import review_and_finalize
from .styles import show_styles

# Apply nest_asyncio globally to smooth out nested loops (PyCharm, notebooks, etc.)
nest_asyncio.apply()

console = Console()

# Safe async runner that prefers asyncio.run but falls back if a loop is already running
def safe_async_run(coro):
    try:
        asyncio.run(coro)
    except RuntimeError as e:
        if "asyncio.run() cannot be called from a running event loop" in str(e):
            loop = asyncio.get_event_loop()
            loop.run_until_complete(coro)
        else:
            raise


def show_legendary_help():
    """Displays our beautiful, custom help screen."""
    console.print(Panel("[dim]A tool by Shivadeepak  [/dim]", border_style="dim"))
    console.print(
        Panel("[magenta bold]✨ Welcome to the AI-Powered README Genie! ✨[/magenta bold]", border_style="magenta"))

    table = Table(box=None, show_header=False, pad_edge=False)
    table.add_column("Command", style="cyan", no_wrap=True, width=35)
    table.add_column("Description", style="white")

    table.add_row("\n[bold]Usage:[/bold]")
    table.add_row("  readme-ai-genie-py <COMMAND> [OPTIONS]")

    table.add_row("\n[bold]Commands:[/bold]")
    table.add_row("  generate", "The main command to scan a project and generate a README.")
    table.add_row("  styles", "Lists all available AI personalities.")

    table.add_row("\n[bold]Options for `generate`:[/bold]")
    table.add_row("  --style <name>", "Set the AI personality (e.g., radiant, zen).")
    table.add_row("  -o, --output <path>", "Specify the output file path.")
    table.add_row("  -y, --yes", "Auto-approve all suggestions, skipping the review.")
    table.add_row("  --plain", "Generate a plain README without extra styling.")
    table.add_row("  --debug", "Show full error details for debugging.")

    table.add_row("\n[bold]General Options:[/bold]")
    table.add_row("  --version", "Show the tool's version.")
    table.add_row("  -h, --help", "Show this legendary help message.")

    console.print(table)

@click.group(context_settings=dict(help_option_names=[]))
@click.version_option(package_name="readme-ai-genie-py", prog_name="readme-ai-genie-py")
@click.help_option('-h', '--help')
def cli():
    """
    A CLI tool to generate beautiful READMEs using AI, built by Shivadeepak.
    """
    if ('--help' in sys.argv or '-h' in sys.argv) and len(sys.argv) == 2:
        show_legendary_help()
        sys.exit(0)

@cli.command()
@click.option('--style', default='default', help="Set the AI personality.")
@click.option('--output', '-o', default='README.md', help='Specify output file path.')
@click.option('--yes', '-y', is_flag=True, help='Auto-approve all AI suggestions.')
@click.option('--plain', is_flag=True, help='Disable styling and emoji tone.')
@click.option('--debug', is_flag=True, help="Show the full exception traceback.")
def generate(style, output, yes, plain, debug):
    """Scans the project and generates a new README.md file."""

    async def run_generation_flow():
        console.print(Panel("[dim]A tool by Shivadeepak   [/dim]", border_style="dim"))
        ensure_api_key()

        console.print(
            Panel("[magenta bold]✨ Welcome to the AI-Powered README Genie! ✨[/magenta bold]", border_style="magenta"))

        effective_style = 'default' if plain else style
        console.print(f"[cyan]Using '{effective_style}' personality...[/cyan]\n")

        try:
            console.print("[cyan]🕵️  Scanning project files...[/cyan]")
            files, total_files = get_project_files()
            if not files:
                console.print("[red]🚫 No files found to analyze. Exiting.[/red]")
                return

            console.print(f"[cyan]🔍 Scanned {total_files} files, analyzing the most relevant {len(files)}.[/cyan]")
            if total_files > 200:
                console.print(
                    f"[yellow]⚠️ Huge project detected! Creating a smart manifest...[/yellow]")

            with console.status("[bold cyan]🔮 Summoning the AI...[/bold cyan]", spinner="dots"):
                ai_draft = await generate_readme_content(files, effective_style, plain=plain)

            if not ai_draft:
                console.print("[red]🤖 AI failed to generate content.[/red]")
                return

            console.print("[green]✅ AI draft ready![/green]")
            final_content = review_and_finalize(ai_draft, auto_approve=yes)

            if final_content:
                with open(output, "w", encoding="utf-8") as f:
                    f.write(final_content)
                console.print(Panel(f"[magenta bold]\n🎉 Success! Your new README is at {output}[/magenta bold]", border_style="green"))

        except Exception as e:
            console.print(Panel(f"[red bold]\n🔥 An error occurred: {e}[/red bold]", border_style="red"))
            if debug:
                console.print_exception(show_locals=True)

    # Launch async flow safely
    safe_async_run(run_generation_flow())

@cli.command()
def styles():
    """List all available AI personalities."""
    console.print(Panel("[dim]A tool by Shivadeepak   [/dim]", border_style="dim"))
    show_styles()

if __name__ == '__main__':
    cli()

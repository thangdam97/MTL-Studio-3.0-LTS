"""
Display utilities using Rich library.
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box

# Global console instance
console = Console()


def print_header(title: str, subtitle: str = "", style: str = "blue") -> None:
    """Print a styled header panel."""
    content = f"[bold]{title}[/bold]"
    if subtitle:
        content += f"\n{subtitle}"

    console.print(Panel(
        content,
        border_style=style,
        padding=(0, 2),
    ))


def print_section(title: str, style: str = "cyan") -> None:
    """Print a section divider."""
    console.print(f"\n[{style}]{'=' * 60}[/{style}]")
    console.print(f"[{style} bold]{title}[/{style} bold]")
    console.print(f"[{style}]{'=' * 60}[/{style}]")


def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"[green][bold]✓[/bold] {message}[/green]")


def print_error(message: str) -> None:
    """Print an error message."""
    console.print(f"[red][bold]✗[/bold] {message}[/red]")


def print_warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"[yellow][bold]⚠[/bold] {message}[/yellow]")


def print_info(message: str) -> None:
    """Print an info message."""
    console.print(f"[cyan]ℹ {message}[/cyan]")


def create_status_table(data: dict, title: str = "Status") -> Table:
    """Create a status table from a dictionary."""
    table = Table(title=title, box=box.ROUNDED)
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="white")

    for key, value in data.items():
        table.add_row(str(key), str(value))

    return table


def create_key_value_display(data: dict) -> str:
    """Create a formatted key-value display string."""
    max_key_len = max(len(str(k)) for k in data.keys()) if data else 0
    lines = []
    for key, value in data.items():
        lines.append(f"  {str(key):<{max_key_len}} : {value}")
    return "\n".join(lines)

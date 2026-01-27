"""
Confirmation dialog components.
"""

from typing import Dict, Any, Optional
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from .styles import custom_style

console = Console()


def confirm_context_caching(
    model: str,
    instruction_size: int,
    ttl: int,
    auto_confirm: bool = False
) -> bool:
    """
    Show context caching confirmation dialog.

    Args:
        model: Model name being used
        instruction_size: Size of system instruction in bytes
        ttl: Cache TTL in minutes
        auto_confirm: If True, show info and auto-confirm

    Returns:
        True if user confirms, False otherwise
    """
    size_kb = instruction_size // 1024 if instruction_size > 1024 else instruction_size
    size_unit = "KB" if instruction_size > 1024 else "bytes"

    panel_content = (
        f"[green]✓[/green] Cache enabled for [bold cyan]{model}[/bold cyan]\n"
        f"[green]✓[/green] System instruction: [bold]{size_kb}{size_unit}[/bold] (will be cached)\n"
        f"[green]✓[/green] TTL: [bold]{ttl} minutes[/bold]\n"
        f"[green]✓[/green] Expected savings: [bold]~87% TPM reduction[/bold]"
    )

    console.print()
    console.print(Panel(
        panel_content,
        title="[bold green]Context Caching[/bold green]",
        border_style="green",
        padding=(1, 2),
    ))

    if auto_confirm:
        console.print("\n[dim]Press Enter to continue...[/dim]")
        input()
        return True

    return questionary.confirm(
        "Proceed with context caching?",
        default=True,
        style=custom_style,
    ).ask()


def confirm_continuity_pack(
    previous_volume: str,
    pack_data: Dict[str, Any],
) -> bool:
    """
    Show continuity pack detection and ask for inheritance.

    Args:
        previous_volume: Name/title of previous volume
        pack_data: Dictionary containing character names, glossary, series title

    Returns:
        True if user wants to inherit, False otherwise
    """
    # Build info table
    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    table.add_column("Item", style="cyan")
    table.add_column("Count", style="white")

    roster = pack_data.get('roster', pack_data.get('character_names', {}))
    glossary = pack_data.get('glossary', {})
    series_title = pack_data.get('series_title', pack_data.get('series_title_en', 'N/A'))

    table.add_row("Character names", f"{len(roster)} entries")
    table.add_row("Glossary terms", f"{len(glossary)} entries")
    table.add_row("Series title", str(series_title)[:40])

    console.print()
    console.print(Panel(
        f"[bold yellow]Sequel Detected[/bold yellow]\n\n"
        f"[bold]Previous volume found:[/bold]\n"
        f"  [cyan]{previous_volume}[/cyan]\n\n"
        f"[bold]Continuity Pack contains:[/bold]",
        border_style="yellow",
        padding=(1, 2),
    ))
    console.print(table)
    console.print()

    return questionary.select(
        "Inherit from previous volume?",
        choices=[
            questionary.Choice("Yes - Maintain consistency (Recommended)", value=True),
            questionary.Choice("No - Generate fresh metadata", value=False),
        ],
        default=True,
        style=custom_style,
    ).ask()


def confirm_series_inheritance(
    previous_volume_id: str,
    inherited_data: Dict[str, Any],
    auto_confirm: bool = False
) -> Dict[str, bool]:
    """
    Show series inheritance confirmation with detailed breakdown.

    Args:
        previous_volume_id: ID of the volume being inherited from
        inherited_data: Dictionary containing inherited metadata
        auto_confirm: If True, show info and auto-confirm all

    Returns:
        Dictionary with inheritance decisions for each category
    """
    # Build details table
    table = Table(box=box.ROUNDED, title="Inherited Data", title_style="bold cyan")
    table.add_column("Setting", style="cyan", width=20)
    table.add_column("Value", style="white", width=35)

    series_title = inherited_data.get('series_title_en', 'N/A')
    author = inherited_data.get('author_en', 'N/A')
    character_names = inherited_data.get('character_names', {})
    glossary = inherited_data.get('glossary', {})

    table.add_row("Series Title", str(series_title)[:35])
    table.add_row("Author (EN)", str(author)[:35])
    table.add_row("Character Names", f"{len(character_names)} entries")
    table.add_row("Glossary Terms", f"{len(glossary)} entries")

    console.print()
    console.print(Panel(
        f"[bold]Inheriting from:[/bold] [cyan]{previous_volume_id}[/cyan]",
        title="[bold green]Series Inheritance[/bold green]",
        border_style="green",
        padding=(1, 2),
    ))
    console.print(table)
    console.print()

    if auto_confirm:
        console.print("[dim]Auto-inheriting all metadata...[/dim]")
        return {
            'inherit_names': True,
            'inherit_glossary': True,
            'inherit_series_info': True,
        }

    # Ask for specific inheritance options
    choices = questionary.checkbox(
        "Select what to inherit:",
        choices=[
            questionary.Choice("Character names", value="names", checked=True),
            questionary.Choice("Glossary terms", value="glossary", checked=True),
            questionary.Choice("Series info (title, author)", value="series", checked=True),
        ],
        style=custom_style,
    ).ask()

    if choices is None:
        # User cancelled
        return {
            'inherit_names': False,
            'inherit_glossary': False,
            'inherit_series_info': False,
        }

    return {
        'inherit_names': 'names' in choices,
        'inherit_glossary': 'glossary' in choices,
        'inherit_series_info': 'series' in choices,
    }


def confirm_action(
    title: str,
    message: str,
    default: bool = True,
    style: str = "cyan"
) -> bool:
    """
    Generic action confirmation dialog.

    Args:
        title: Dialog title
        message: Confirmation message
        default: Default selection
        style: Panel border style

    Returns:
        True if confirmed, False otherwise
    """
    console.print()
    console.print(Panel(
        message,
        title=f"[bold]{title}[/bold]",
        border_style=style,
        padding=(1, 2),
    ))

    return questionary.confirm(
        "Proceed?",
        default=default,
        style=custom_style,
    ).ask()


def confirm_overwrite(filename: str) -> bool:
    """
    Confirm file overwrite.

    Args:
        filename: Name of file to be overwritten

    Returns:
        True if user confirms overwrite
    """
    return questionary.confirm(
        f"File '{filename}' already exists. Overwrite?",
        default=False,
        style=custom_style,
    ).ask()

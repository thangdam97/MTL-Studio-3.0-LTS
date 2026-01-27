"""
Status display menu components.
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
import json
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from ..components.styles import custom_style

console = Console()


def show_status_panel(work_dir: Path, volume_id: str) -> None:
    """
    Display detailed status for a volume.

    Args:
        work_dir: Path to WORK directory
        volume_id: Volume identifier
    """
    manifest_path = work_dir / volume_id / "manifest.json"
    if not manifest_path.exists():
        console.print(f"[red]Volume not found: {volume_id}[/red]")
        return

    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    # Header
    console.print()
    console.print(Panel(
        f"[bold]Pipeline Status[/bold]\n"
        f"Volume: [cyan]{volume_id}[/cyan]",
        border_style="blue",
        padding=(1, 2),
    ))

    # Metadata section
    metadata = manifest.get('metadata', {})
    metadata_en = manifest.get('metadata_en', {})

    meta_table = Table(title="Metadata", box=box.ROUNDED)
    meta_table.add_column("Field", style="cyan", width=15)
    meta_table.add_column("Japanese", style="white", width=25)
    meta_table.add_column("English", style="green", width=25)

    meta_table.add_row(
        "Title",
        str(metadata.get('title', 'N/A'))[:25],
        str(metadata_en.get('title_en', 'N/A'))[:25],
    )
    meta_table.add_row(
        "Author",
        str(metadata.get('author', 'N/A'))[:25],
        str(metadata_en.get('author_en', 'N/A'))[:25],
    )
    meta_table.add_row(
        "Volume",
        str(metadata.get('volume', 'N/A')),
        str(metadata_en.get('volume', 'N/A')),
    )

    console.print()
    console.print(meta_table)

    # Pipeline state section
    pipeline_state = manifest.get('pipeline_state', {})

    phase_table = Table(title="Pipeline Phases", box=box.ROUNDED)
    phase_table.add_column("Phase", style="cyan", width=25)
    phase_table.add_column("Status", style="white", width=15)
    phase_table.add_column("Details", style="dim", width=25)

    phases = [
        ('Phase 1: Librarian', 'librarian'),
        ('Phase 1.5: Metadata', 'metadata_processor'),
        ('Phase 2: Translator', 'translator'),
        ('Phase 3: Critics', 'critics'),
        ('Phase 4: Builder', 'builder'),
    ]

    for phase_name, phase_key in phases:
        phase_info = pipeline_state.get(phase_key, {})
        status = phase_info.get('status', 'not started')

        status_icon = {
            'completed': '[green]✓ completed[/green]',
            'in_progress': '[yellow]... in progress[/yellow]',
            'pending': '[dim]○ pending[/dim]',
            'manual review': '[cyan]⟳ manual[/cyan]',
            'not started': '[dim]- not started[/dim]',
        }.get(status, f'[dim]{status}[/dim]')

        details = phase_info.get('timestamp', '')[:19] if phase_info.get('timestamp') else ''

        phase_table.add_row(phase_name, status_icon, details)

    console.print()
    console.print(phase_table)

    # Chapter status section
    chapters = manifest.get('chapters', [])

    if chapters:
        chapter_table = Table(title=f"Chapters ({len(chapters)} total)", box=box.ROUNDED)
        chapter_table.add_column("#", style="dim", width=4)
        chapter_table.add_column("Filename", style="cyan", width=20)
        chapter_table.add_column("Title", style="white", width=25)
        chapter_table.add_column("Status", style="white", width=12)

        completed = 0
        for i, ch in enumerate(chapters[:15], 1):  # Show first 15
            status = ch.get('translation_status', 'pending')
            if status == 'completed':
                completed += 1

            status_icon = {
                'completed': '[green]✓[/green]',
                'in_progress': '[yellow]...[/yellow]',
                'pending': '[dim]○[/dim]',
                'failed': '[red]✗[/red]',
                'skipped': '[dim]~[/dim]',
            }.get(status, '[dim]?[/dim]')

            chapter_table.add_row(
                str(i),
                ch.get('filename', 'N/A')[:20],
                str(ch.get('title', ''))[:25] or '[dim]No title[/dim]',
                status_icon,
            )

        if len(chapters) > 15:
            chapter_table.add_row("...", f"+{len(chapters) - 15} more", "", "")

        console.print()
        console.print(chapter_table)
        console.print(f"\n  [bold]Progress:[/bold] {completed}/{len(chapters)} chapters translated")

    # Assets section
    assets = manifest.get('assets', {})
    if assets:
        console.print(f"\n  [bold]Assets:[/bold]")
        console.print(f"    Cover: {assets.get('cover', 'N/A')}")
        console.print(f"    Kuchi-e: {len(assets.get('kuchie', []))} images")
        console.print(f"    Illustrations: {len(assets.get('illustrations', []))} images")

    console.print()


def list_volumes_panel(work_dir: Path) -> Optional[str]:
    """
    Display list of all volumes with interactive selection.

    Args:
        work_dir: Path to WORK directory

    Returns:
        Selected volume ID or None
    """
    console.print()
    console.print(Panel(
        "[bold]Volumes[/bold]\n"
        "[dim]All volumes in WORK directory[/dim]",
        border_style="cyan",
        padding=(1, 2),
    ))

    volumes = _get_all_volumes(work_dir)

    if not volumes:
        console.print("\n[yellow]No volumes found in WORK directory[/yellow]")
        console.print(f"[dim]Start a new translation to create a volume.[/dim]\n")
        return None

    # Display volumes table
    vol_table = Table(box=box.ROUNDED)
    vol_table.add_column("#", style="dim", width=4)
    vol_table.add_column("Volume ID", style="cyan", width=30)
    vol_table.add_column("Title", style="white", width=30)
    vol_table.add_column("Status", style="white", width=15)
    vol_table.add_column("Chapters", style="dim", width=10)

    for i, vol in enumerate(volumes, 1):
        status = vol.get('status', 'unknown')
        status_icon = {
            'completed': '[green]✓ done[/green]',
            'in_progress': '[yellow]... working[/yellow]',
            'pending': '[dim]○ pending[/dim]',
        }.get(status, f'[dim]{status}[/dim]')

        vol_table.add_row(
            str(i),
            vol['id'][:30],
            str(vol.get('title', 'N/A'))[:30],
            status_icon,
            str(vol.get('chapters', 0)),
        )

    console.print()
    console.print(vol_table)
    console.print()

    # Offer to select a volume
    vol_choices = [
        questionary.Choice(f"{v['id']} - {v.get('title', 'N/A')[:30]}", value=v['id'])
        for v in volumes
    ]
    vol_choices.append(questionary.Separator())
    vol_choices.append(questionary.Choice("Back to Main Menu", value=None))

    selected = questionary.select(
        "Select a volume to view details:",
        choices=vol_choices,
        style=custom_style,
    ).ask()

    return selected


def show_translation_log(work_dir: Path, volume_id: str) -> None:
    """
    Display translation log for a volume.

    Args:
        work_dir: Path to WORK directory
        volume_id: Volume identifier
    """
    log_path = work_dir / volume_id / "translation_log.json"
    if not log_path.exists():
        console.print(f"[yellow]No translation log found for {volume_id}[/yellow]")
        return

    with open(log_path, 'r', encoding='utf-8') as f:
        log_data = json.load(f)

    console.print()
    console.print(Panel(
        "[bold]Translation Log[/bold]",
        border_style="cyan",
        padding=(1, 2),
    ))

    # Summary
    summary = log_data.get('summary', {})
    if summary:
        console.print(f"\n[bold]Summary:[/bold]")
        console.print(f"  Total chapters: {summary.get('total_chapters', 'N/A')}")
        console.print(f"  Completed: {summary.get('completed', 'N/A')}")
        console.print(f"  Failed: {summary.get('failed', 'N/A')}")
        console.print(f"  Total tokens: {summary.get('total_tokens', 'N/A'):,}")

    # Recent entries
    entries = log_data.get('entries', [])
    if entries:
        console.print(f"\n[bold]Recent Activity:[/bold]")
        for entry in entries[-10:]:  # Last 10 entries
            timestamp = entry.get('timestamp', '')[:19]
            chapter = entry.get('chapter', 'N/A')
            status = entry.get('status', 'N/A')
            tokens = entry.get('tokens', 0)

            status_icon = '[green]✓[/green]' if status == 'completed' else '[red]✗[/red]'
            console.print(f"  {status_icon} {timestamp} | {chapter} | {tokens:,} tokens")

    console.print()


def _get_all_volumes(work_dir: Path) -> List[Dict[str, Any]]:
    """Get list of all volumes with basic info."""
    volumes = []

    if not work_dir.exists():
        return volumes

    for vol_dir in work_dir.iterdir():
        if not vol_dir.is_dir():
            continue

        manifest_path = vol_dir / "manifest.json"
        if not manifest_path.exists():
            continue

        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)

            # Get status
            pipeline_state = manifest.get('pipeline_state', {})
            translator_status = pipeline_state.get('translator', {}).get('status', 'pending')

            # Count completed chapters
            chapters = manifest.get('chapters', [])
            completed = sum(1 for ch in chapters if ch.get('translation_status') == 'completed')

            volumes.append({
                'id': vol_dir.name,
                'title': manifest.get('metadata_en', {}).get('title_en') or
                        manifest.get('metadata', {}).get('title', 'Unknown'),
                'status': translator_status,
                'chapters': len(chapters),
                'completed': completed,
            })
        except Exception:
            # Skip volumes with invalid manifests
            continue

    return sorted(volumes, key=lambda x: x['id'], reverse=True)

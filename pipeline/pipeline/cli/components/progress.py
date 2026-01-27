"""
Progress display components using Rich.
"""

from typing import Optional, List, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich import box
import time

console = Console()


class TranslationProgress:
    """Progress display for translation phase."""

    def __init__(
        self,
        volume_title: str,
        total_chapters: int,
        model: str,
        cached: bool = False,
    ):
        """
        Initialize translation progress display.

        Args:
            volume_title: Title of the volume being translated
            total_chapters: Total number of chapters
            model: Gemini model being used
            cached: Whether context caching is active
        """
        self.volume_title = volume_title
        self.total_chapters = total_chapters
        self.model = model
        self.cached = cached

        self.current_chapter = 0
        self.current_chapter_name = ""
        self.recent_chapters: List[Dict[str, Any]] = []
        self.stats = {
            'input_tokens': 0,
            'output_tokens': 0,
            'cache_hits': 0,
            'cache_saves': 0,
        }

        self._progress: Optional[Progress] = None
        self._task_id = None
        self._live: Optional[Live] = None

    def _create_progress_bar(self) -> Progress:
        """Create the progress bar component."""
        return Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=40),
            TaskProgressColumn(),
            TextColumn("[cyan]{task.fields[chapter]}"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
        )

    def _create_layout(self) -> Panel:
        """Create the full progress display layout."""
        # Header info
        cache_status = "[green]✓ Yes[/green]" if self.cached else "[red]✗ No[/red]"
        header = (
            f"[bold]Phase 2: Translation[/bold]\n"
            f"Model: [cyan]{self.model}[/cyan]  |  Cached: {cache_status}"
        )

        # Stats table
        stats_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
        stats_table.add_column("Stat", style="dim")
        stats_table.add_column("Value", style="white")

        stats_table.add_row("Input tokens", f"{self.stats['input_tokens']:,}")
        stats_table.add_row("Output tokens", f"{self.stats['output_tokens']:,}")
        stats_table.add_row("Cache hits", str(self.stats['cache_hits']))
        stats_table.add_row("Cache saves", f"{self.stats['cache_saves']:,} tokens")

        # Recent chapters
        recent_text = ""
        for ch in self.recent_chapters[-3:]:
            status = "[green]✓[/green]" if ch.get('status') == 'completed' else "[yellow]...[/yellow]"
            name = ch.get('name', 'Unknown')[:30]
            tokens = ch.get('tokens', 0)
            duration = ch.get('duration', 0)
            recent_text += f"  {status} {name} - {tokens:,} tokens - {duration:.1f}s\n"

        if not recent_text:
            recent_text = "  [dim]No chapters completed yet[/dim]"

        # Build full content
        content = f"{header}\n\n"

        # Progress section (will be filled by progress bar)
        if self._progress:
            content += "[dim]Progress bar active[/dim]\n\n"

        content += "[bold]Stats:[/bold]\n"
        content += f"  Input tokens:  {self.stats['input_tokens']:,}\n"
        content += f"  Output tokens: {self.stats['output_tokens']:,}\n"
        content += f"  Cache hits:    {self.stats['cache_hits']}\n"
        content += f"  Cache saves:   {self.stats['cache_saves']:,} tokens\n\n"

        content += "[bold]Recent:[/bold]\n"
        content += recent_text

        return Panel(
            content,
            title=f"[bold cyan]Translating: {self.volume_title}[/bold cyan]",
            border_style="blue",
            padding=(1, 2),
        )

    def start(self) -> None:
        """Start the progress display."""
        self._progress = self._create_progress_bar()
        self._task_id = self._progress.add_task(
            "Translating...",
            total=self.total_chapters,
            chapter="Starting...",
        )
        self._progress.start()

    def stop(self) -> None:
        """Stop the progress display."""
        if self._progress:
            self._progress.stop()
            self._progress = None

    def update(
        self,
        chapter_name: str,
        completed: bool = False,
        tokens: int = 0,
        duration: float = 0,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cache_hit: bool = False,
    ) -> None:
        """
        Update progress with new chapter info.

        Args:
            chapter_name: Name of current/completed chapter
            completed: Whether the chapter is completed
            tokens: Total tokens for this chapter
            duration: Time taken for this chapter
            input_tokens: Input tokens used
            output_tokens: Output tokens generated
            cache_hit: Whether this request hit the cache
        """
        self.current_chapter_name = chapter_name

        if completed:
            self.current_chapter += 1
            self.recent_chapters.append({
                'name': chapter_name,
                'status': 'completed',
                'tokens': tokens,
                'duration': duration,
            })

            # Update stats
            self.stats['input_tokens'] += input_tokens
            self.stats['output_tokens'] += output_tokens
            if cache_hit:
                self.stats['cache_hits'] += 1
                self.stats['cache_saves'] += input_tokens

        if self._progress and self._task_id is not None:
            self._progress.update(
                self._task_id,
                completed=self.current_chapter,
                chapter=chapter_name[:30],
            )

    def print_summary(self) -> None:
        """Print final translation summary."""
        console.print()

        summary = Table(title="Translation Summary", box=box.ROUNDED)
        summary.add_column("Metric", style="cyan")
        summary.add_column("Value", style="white")

        summary.add_row("Chapters translated", f"{self.current_chapter}/{self.total_chapters}")
        summary.add_row("Total input tokens", f"{self.stats['input_tokens']:,}")
        summary.add_row("Total output tokens", f"{self.stats['output_tokens']:,}")
        summary.add_row("Cache hits", str(self.stats['cache_hits']))
        summary.add_row("Tokens saved by cache", f"{self.stats['cache_saves']:,}")

        if self.stats['input_tokens'] > 0:
            cache_ratio = (self.stats['cache_saves'] / self.stats['input_tokens']) * 100
            summary.add_row("Cache efficiency", f"{cache_ratio:.1f}%")

        console.print(summary)


def show_simple_progress(message: str, total: int = 100) -> Progress:
    """
    Create a simple progress bar for general use.

    Args:
        message: Progress message
        total: Total steps

    Returns:
        Progress instance (call .start() to begin)
    """
    return Progress(
        SpinnerColumn(),
        TextColumn(f"[bold blue]{message}"),
        BarColumn(),
        TaskProgressColumn(),
    )


def show_phase_progress(phase_name: str, step: int, total_steps: int) -> None:
    """
    Show progress for a pipeline phase.

    Args:
        phase_name: Name of the current phase
        step: Current step number
        total_steps: Total number of steps
    """
    progress_bar = "━" * int((step / total_steps) * 40)
    remaining = "─" * (40 - len(progress_bar))
    percentage = int((step / total_steps) * 100)

    console.print(
        f"  [cyan]{phase_name}[/cyan]\n"
        f"  [{progress_bar}[bold]{remaining}[/bold]] {percentage}% [{step}/{total_steps}]"
    )

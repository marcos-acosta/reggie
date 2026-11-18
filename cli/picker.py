from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from .lineup import Entry, Lineup


def pick_screen(console: Console, lineup: Lineup, current_id: str | None = None) -> Entry:
    table = Table(box=None, show_header=False, padding=(0, 1))
    for entry in lineup.entries:
        marker = " [dim](current)[/]" if entry.id == current_id else ""
        table.add_row(f"[cyan]{entry.number}[/]", f"{entry.name}{marker}")
    console.print(table)

    current = next((entry for entry in lineup.entries if entry.id == current_id), lineup.entries[0])
    choices = [key for entry in lineup.entries for key in (str(entry.number), entry.name)]
    choice = Prompt.ask("Screen", console=console, choices=choices, default=str(current.number), show_choices=False)
    return lineup.find(choice)

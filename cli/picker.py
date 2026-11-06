from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table


def pick_screen(console: Console, names: list[str], current: str | None = None) -> str:
    table = Table(box=None, show_header=False, padding=(0, 1))
    for number, name in enumerate(names, 1):
        marker = " [dim](current)[/]" if name == current else ""
        table.add_row(f"[cyan]{number}[/]", f"{name}{marker}")
    console.print(table)

    numbers = [str(n) for n in range(1, len(names) + 1)]
    default = str(names.index(current) + 1) if current in names else "1"
    choice = Prompt.ask("Screen", console=console, choices=numbers + names, default=default, show_choices=False)
    return names[int(choice) - 1] if choice in numbers else choice

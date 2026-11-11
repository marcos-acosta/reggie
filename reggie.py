import argparse

from rich.console import Console

from cli.control import send_command
from cli.picker import pick_screen
from cli.session import Session, available_screens
from display import default_kind, open_display

parser = argparse.ArgumentParser(description="Preview screens on the matrix or simulator.")
parser.add_argument("screen", nargs="?", help="Screen to show; omit to pick from a list")
parser.add_argument("--sim", action="store_true", help="Use the on-screen simulator")
parser.add_argument("--no-watch", dest="watch", action="store_false", help="Only reload when pressing r")
power = parser.add_mutually_exclusive_group()
power.add_argument("--on", dest="power", action="store_const", const="on", help="Resume the running session")
power.add_argument("--off", dest="power", action="store_const", const="off", help="Blank the running session")


def set_power(console: Console, command: str, kind: str) -> None:
    if reply := send_command(command):
        console.print(f"[dim]Session: {reply}[/]")
    elif command == "off":
        open_display(kind).clear()
        console.print("[dim]No running session; cleared the display[/]")
    else:
        console.print("[yellow]No running session to turn on; start one with reggie.py <screen>[/]")


def main() -> None:
    args = parser.parse_args()
    console = Console()
    kind = "sim" if args.sim else default_kind()

    if args.power:
        set_power(console, args.power, kind)
        return

    screens = available_screens()

    if args.screen and args.screen not in screens:
        parser.error(f"Unknown screen {args.screen!r}; available: {', '.join(screens)}")
    screen = args.screen or pick_screen(console, screens)

    console.print(f"[dim]Opening {kind} display…[/]")
    Session(open_display(kind), console, screen, watch=args.watch).run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass

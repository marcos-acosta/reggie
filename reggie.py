import argparse

from rich.console import Console

from cli.picker import pick_screen
from cli.session import Session, available_screens
from display import default_kind, open_display

parser = argparse.ArgumentParser(description="Preview screens on the matrix or simulator.")
parser.add_argument("screen", nargs="?", help="Screen to show; omit to pick from a list")
parser.add_argument("--sim", action="store_true", help="Use the on-screen simulator")
parser.add_argument("--no-watch", dest="watch", action="store_false", help="Only reload when pressing r")


def main() -> None:
    args = parser.parse_args()
    console = Console()
    screens = available_screens()

    if args.screen and args.screen not in screens:
        parser.error(f"Unknown screen {args.screen!r}; available: {', '.join(screens)}")
    screen = args.screen or pick_screen(console, screens)

    kind = "sim" if args.sim else default_kind()
    console.print(f"[dim]Opening {kind} display…[/]")
    Session(open_display(kind), console, screen, watch=args.watch).run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass

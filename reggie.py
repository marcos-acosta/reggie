import argparse

from rich.console import Console

from cli.picker import pick_screen
from cli.session import Session, available_screens
from display import default_kind, open_display

parser = argparse.ArgumentParser(description="Preview screens on the matrix or simulator.")
parser.add_argument("screen", nargs="?", help="Screen to show; omit to pick from a list")
parser.add_argument("--sim", action="store_true", help="Use the on-screen simulator")
parser.add_argument("--no-watch", dest="watch", action="store_false", help="Only reload when pressing r")
power = parser.add_mutually_exclusive_group()
power.add_argument("--on", dest="power", action="store_const", const="on", help="Turn the display on and exit")
power.add_argument("--off", dest="power", action="store_const", const="off", help="Turn the display off and exit")


def main() -> None:
    args = parser.parse_args()
    console = Console()
    kind = "sim" if args.sim else default_kind()

    if args.power:
        display = open_display(kind)
        getattr(display, args.power)()
        console.print(f"[dim]{kind} display turned {args.power}[/]")
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

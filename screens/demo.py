from screens import screen
from ui import Box, Column, Row, Spacer, Text


@screen()
def demo() -> Column:
    return Column(
        Box(Text("rgb64", color="orange"), padding=(1, 2), background="#202050"),
        Row(
            Text("L", color="red", font="5x7"),
            Spacer(),
            Text("R", color="lime", font="5x7"),
            gap=1,
        ),
        Text("5x7: Hello!", color="yellow", font="5x7"),
        Text("tom-thumb 12:45", color="magenta"),
        Spacer(),
        Row(
            Box(width=10, height=8, background="red"),
            Box(width=10, height=8, background="lime", margin=(0, 2)),
            Box(width=10, height=8, background="blue"),
            align="center",
        ),
        Box(
            Text("hi!", color="cyan"),
            padding=1,
            margin=(0, 4),
            background="#103010",
        ),
        gap=1,
    )

from screens import screen
from ui import FONT_NAMES, Column, Text

SAMPLES = ("ABCDEFGHIJKL", "abcdefghijkl", "0123456789!?")


@screen()
def fonts() -> Column:
    return Column(
        *(
            Column(Text(font, color="orange", font=font), *(Text(s, font=font) for s in SAMPLES))
            for font in FONT_NAMES
        ),
        gap=1,
    )

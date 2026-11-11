from screens import screen
from ui import Box, Node


@screen("off")
def off() -> Node:
    return Box()

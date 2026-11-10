import sys

from PIL import Image, ImageSequence

from display import open_display


def main():
    display = open_display()
    display.on()
    img = Image.open(sys.argv[1])

    if getattr(img, "is_animated", False):
        frames = [
            (f.copy(), f.info.get("duration", 100)) for f in ImageSequence.Iterator(img)
        ]
        while True:
            for frame, ms in frames:
                display.show(frame)
                display.sleep(ms / 1000)
    else:
        display.show(img)
        display.hold()


if __name__ == "__main__":
    main()

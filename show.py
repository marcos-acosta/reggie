import sys
import time

from PIL import Image, ImageSequence

from matrix import Matrix


def main():
    matrix = Matrix()
    img = Image.open(sys.argv[1])

    if getattr(img, "is_animated", False):
        frames = [
            (f.copy(), f.info.get("duration", 100)) for f in ImageSequence.Iterator(img)
        ]
        while True:
            for frame, ms in frames:
                matrix.show(frame)
                time.sleep(ms / 1000)
    else:
        matrix.show(img)


if __name__ == "__main__":
    main()

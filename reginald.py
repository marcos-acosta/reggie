import argparse
from matrix import Matrix
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument("action", help="The action to perform")
parser.add_argument("-s", "--src", help="The source image to show")
parser.add_argument("-l", "--level", help="The brightness level", type=int)


def main():
    args = parser.parse_args()
    matrix = Matrix()
    if args.action == "off":
        matrix.off()
    elif args.action == "on":
        matrix.on()
    elif args.action == "brightness" and args.level is not None:
        matrix.brightness(args.level)
    elif args.action == "show" and len(args.src):
        img = Image.open(args.src)
        matrix.show(img)


if __name__ == "__main__":
    main()

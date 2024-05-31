import os
import sys
import time

import numpy as np
from PIL import Image


# constants used for coloring console outputs
ANSIRED = '\033[91m'
STANDARD = '\033[0m'
ANSIGREEN = '\033[92m'

def green() -> str:
    return ANSIGREEN + "█" + STANDARD

def red() -> str:
    return ANSIRED + "█" + STANDARD

def find_picture(rgb, imageList) -> Image:
    best = (None, 765)
    for ((x, y, z), image) in imageList:
        # Searches for the Image witth the lowest offset of RGB values
        offset = abs(rgb[0] - x) + abs(rgb[1] - y) + abs(rgb[2] - z)
        if offset < best[1]:
            best = (image, offset)
    return best[0]

def create_image_list(folder) -> list[tuple[tuple, Image.Image]]:
    image_list = []
    # Only accept certain Image file formats
    filetypes = ("png", "jpg", "jpeg", "webp")
    # Iterate through given Directory
    for filename in os.listdir(folder):
        if filename.endswith(filetypes):
            filepath = os.path.join(folder, filename)
            img = Image.open(filepath).convert('RGB')
            avg_color = tuple(np.array(img).mean(axis=(0, 1)))
            # Creates a List that contains all Images and their RGB Values in a Tupel
            image_list.append((avg_color, img))
    print("time for creating list", time.time() - start, "seconds")
    print("Length of Imagelist:", len(image_list))
    return image_list


def create_image(amount: int, image: Image, width: float, height: float):
    img = Image.new('RGB', image.size)
    imageList = create_image_list(sys.argv[3])
    lastImage: tuple[Image.Image, tuple[int, int, int]] = (None, (0, 0, 0))
    first: bool = True
    # Vertical loop
    for i in range(0, amount):
        jRange = None
        # Creating a "Zick-Zack" for the horizontal loop
        if i % 2 == 1:
            jRange = range(0, amount)
        else:
            jRange = range(amount, 0, -1)
        statusString: str = ""
        # Horizontal loop
        for j in jRange:
            # Calculating the current pixel
            left = int(j * width)
            upper = int(i * height)
            right = int((j + 1) * width)
            lower = int((i + 1) * height)
            box = (left, upper, right, lower)
            # Geting the current pixel from the overall image
            pixel = image.crop(box)
            pixelColor = tuple(np.array(pixel).mean(axis=(0, 1)))
            # Calculating the RGB offset from the last used Image
            off_x = abs(lastImage[1][0] - pixelColor[0])
            off_y = abs(lastImage[1][1] - pixelColor[1])
            off_z = abs(lastImage[1][2] - pixelColor[2])
            off = off_x + off_y + off_z
            # Check if the current Pixels RGB values are significantly different to the last
            if off > 10 or first:
                # Find best Image for this Pixel
                first = False
                pixelImage: Image = find_picture(pixelColor, imageList)
                lastImage = (pixelImage, pixelColor)
                pixelImage = pixelImage.resize((box[2] - box[0], box[3] - box[1]))
                img.paste(pixelImage, box)
                statusString = statusString + red()
            else:
                # Use last image 
                resizedLast = lastImage[0].resize((box[2] - box[0], box[3] - box[1]))
                img.paste(resizedLast, box)
                statusString = statusString + green()
        print(statusString)
    img.show()



def main():
    # Check if input was correct
    if len(sys.argv) < 4:
        print(ANSIRED + "ERROR: Missing Parameters:", 4 - len(sys.argv), STANDARD)
        return
    if not os.path.isfile(sys.argv[1]):
        print(ANSIRED + "ERROR: " + sys.argv[1] + "is not a file!" + STANDARD)
        return
    if not os.path.isdir(sys.argv[3]):
        print(ANSIRED + "ERROR: " + sys.argv[3] + "is not a directory!" + STANDARD)
        return
    im = Image.open(sys.argv[1]).convert('RGB')
    amount = int(sys.argv[2])
    width, height = im.size
    pixelWidth = width / amount
    pixelHeight = height / amount
    # Rescale the Image, if the Pixels get to small. Scaling keeps the aspec ratio
    resized: bool = False
    if pixelWidth < 10:
        resized = True
        im = im.resize((int(10 * amount), int(10 * amount * height/width)))
        print("Not wide enough - Resized")
    if pixelHeight < 10:
        resized = True
        im = im.resize((int(10 * amount * width/height), int(10 * amount)))
        print("Not high enough - Resized")
    if resized:
        width, height = im.size
        pixelWidth = width / amount
        pixelHeight = height / amount
    print("Creating an Image with", str(amount) + "x" + str(amount) + "(" + str(amount*amount)
          + ")" ' "Pixels":')
    create_image(amount, im, pixelWidth, pixelHeight)
    time_needed = time.time() - start
    print(ANSIGREEN + "Process finished after", time_needed, "seconds" + STANDARD)


start = time.time()
main()

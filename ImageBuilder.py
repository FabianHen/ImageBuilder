import os
import sys
import time

import numpy as np
from PIL import Image


def find_picture(rgb, imageList) -> Image:
    best = (None, 765)
    for ((x, y, z), image) in imageList:
        offset = abs(rgb[0] - x) + abs(rgb[1] - y) + abs(rgb[2] - z)
        if offset < best[1]:
            best = (image, offset)
    return best[0]


def create_image_list(folder) -> list[tuple[tuple, Image]]:
    image_list = []

    filetypes = ("png", "jpg", "jpeg", "webp")
    for filename in os.listdir(folder):
        if filename.endswith(filetypes):
            filepath = os.path.join(folder, filename)
            img = Image.open(filepath).convert('RGB')
            avg_color = tuple(np.array(img).mean(axis=(0, 1)))
            image_list.append((avg_color, img))
    print("time for creating list", time.time() - start, "seconds")
    print(len(image_list))
    return image_list


def create_image(amount: int, image: Image, width: float, height: float):
    img = Image.new('RGB', image.size)
    imageList = create_image_list(sys.argv[3])
    lastImage: (Image, (int, int, int)) = (None, (0, 0, 0))
    lastOffset = 765
    for i in range(0, amount):
        jRange = None
        if i % 2 == 1:
            jRange = range(0, amount)
        else:
            jRange = range(amount, 0, -1)
        string = ""
        for j in jRange:
            left = int(j * width)
            upper = int(i * height)
            right = int((j + 1) * width)
            lower = int((i + 1) * height)
            box = (left, upper, right, lower)
            pixel = image.crop(box)
            pixelColor = tuple(np.array(pixel).mean(axis=(0, 1)))
            off_x = abs(lastImage[1][0] - pixelColor[0])
            off_y = abs(lastImage[1][1] - pixelColor[1])
            off_z = abs(lastImage[1][2] - pixelColor[2])
            off = off_x + off_y + off_z
            if abs(lastOffset - off) > 10:
                pixelImage: Image = find_picture(pixelColor, imageList)
                lastOffset = off
                lastImage = (pixelImage, pixelColor)
                pixelImage = pixelImage.resize((box[2] - box[0], box[3] - box[1]))
                img.paste(pixelImage, box)
                string = string + str(0)
            else:
                resizedLast = lastImage[0].resize((box[2] - box[0], box[3] - box[1]))
                img.paste(resizedLast, box)
                string = string + str(1)
        print(string)
    img.show()



def main():
    ansiRed = '\033[91m'
    standard = '\033[0m'
    green = '\033[92m'
    if len(sys.argv) < 4:
        print(ansiRed + "ERROR: Missing Parameters:", 4 - len(sys.argv), standard)
        return
    if not os.path.isfile(sys.argv[1]):
        print(ansiRed + "ERROR: " + sys.argv[1] + "is not a file!" + standard)
        return
    if not os.path.isdir(sys.argv[3]):
        print(ansiRed + "ERROR: " + sys.argv[3] + "is not a directory!" + standard)
        return
    im = Image.open(sys.argv[1]).convert('RGB')
    amount = int(sys.argv[2])
    width, height = im.size
    pixelWidth = width / amount
    pixelHeight = height / amount
    if pixelWidth <= 10 or pixelHeight <= 10:
        im.resize((int(10 * pixelWidth), int(10 * pixelHeight)))
        width, height = im.size
        pixelWidth = width / amount
        pixelHeight = height / amount
    print("Creating an Image with", str(amount) + "x" + str(amount) + "(" + str(amount*amount)
          + ")" ' "Pixels":')
    create_image(amount, im, pixelWidth, pixelHeight)
    time_needed = time.time() - start
    print(green+"Process finished after", time_needed, "seconds" + standard)


start = time.time()
main()

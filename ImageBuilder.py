import os
import sys

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
    for filename in os.listdir(folder):
        if filename.endswith("png") or filename.endswith("jpg"):
            filepath = os.path.join(folder, filename)
            img = Image.open(filepath).convert('RGB')
            avg_color = tuple(np.array(img).mean(axis=(0, 1)))
            image_list.append((avg_color, img))
    return image_list


def main():
    amount = int(sys.argv[2])
    im = Image.open(sys.argv[1])
    im = im.convert('RGB')
    width, height = im.size
    pixelWidth = width / amount
    pixelHeight = height / amount
    if pixelWidth <= 10 or pixelHeight <= 10:
        im.resize((5 * width, 5 * height))
        width, height = im.size
        pixelWidth = width / amount
        pixelHeight = height / amount
    img = Image.new('RGB', im.size)
    imageList = create_image_list(sys.argv[3])
    for i in range(0, amount):
        for j in range(0, amount):
            left = int(j * pixelWidth)
            upper = int(i * pixelHeight)
            right = int((j + 1) * pixelWidth)
            lower = int((i + 1) * pixelHeight)
            box = (left, upper, right, lower)
            pixel = im.crop(box)
            pixelColor = tuple(np.array(pixel).mean(axis=(0, 1)))
            pixelImage = find_picture(pixelColor, imageList).resize((box[2] - box[0], box[3] - box[1]))
            img.paste(pixelImage, box)
    img.show()


main()

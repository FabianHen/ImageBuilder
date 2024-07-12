import os
import sys
import time
import math

import numpy as np
from PIL import Image


# constants used for coloring console outputs
ANSIRED = '\033[91m'
STANDARD = '\033[0m'
ANSIGREEN = '\033[92m'
# Threshhold constant that determines when he same Image is used for surrounding pixels
THRESHOLD = 10
# 2 Dimensional Array with values that are either 0 or 1, to track if a pixel was already filled
check_array: list[list[int]]
# 2 Dimensional Array with RGB values in a tuple, to avoid calculating the values of a pixel twice
value_array: list[list[int]]
# The image that is given by the user
input_image: Image.Image
# The image that is created
output_image: Image.Image
# A list that contains all Images from the given folder together with their average RGB values like this: [(R,G,B), Image]
image_list: list[tuple[tuple[int, int, int], Image.Image]]
# The width and heigh of each pixel
width: int
height: int
# The amount of pixels on each side
amount: int


def find_same_color(x: int, y: int, rgb: tuple[int, int, int], image=Image.Image):
    global input_image, output_image, value_array, check_array, image_list
    output_image.paste(image, (x * width, y * height))
    check_array[y][x] = 1
    # Check pixel left to the current pixel
    if x != 0 and check_array[y][x-1] == 0:
        color_left = get_pixel_color(y, x-1)
        offset = calculate_offset(color_left, rgb)
        if offset < THRESHOLD:
            find_same_color(x-1, y, rgb, image)
    # Check pixel underneath the current pixel
    if y != amount-1 and check_array[y + 1][x] == 0:
        color_bottom = get_pixel_color(y + 1, x)
        offset = calculate_offset(color_bottom, rgb)
        if offset < THRESHOLD:
            find_same_color(x, y + 1, rgb, image)
    # Check pixel right to the curren pixel
    if x != amount-1 and check_array[y][x+1] == 0:
        color_right = get_pixel_color(y, x+1)
        offset = calculate_offset(color_right, rgb)
        if offset < THRESHOLD:
            find_same_color(x+1, y, rgb, image)


def calculate_offset(rgb1: tuple[int, int, int], rgb2: tuple[int, int, int]) -> int:
    off_r = abs(rgb1[0] - rgb2[0])
    off_g = abs(rgb1[1] - rgb2[1])
    off_b = abs(rgb1[2] - rgb2[2])
    return off_r + off_g + off_b


def get_pixel_color(x: int, y: int) -> tuple[int, int, int]:
    global width, height, value_array
    if value_array[y][x] is None:
        left = int(x * width)
        upper = int(y * height)
        right = int((x + 1) * width)
        lower = int((y + 1) * height)
        box = (left, upper, right, lower)
        # Geting the current pixel from the overall image
        pixel = input_image.crop(box)
        value_array[y][x] = tuple(np.array(pixel).mean(axis=(0, 1)))
    return value_array[y][x]


def find_picture(rgb) -> Image:
    best = (None, 765)
    for ((x, y, z), image) in image_list:
        # Searches for the Image witth the lowest offset of RGB values
        offset = abs(rgb[0] - x) + abs(rgb[1] - y) + abs(rgb[2] - z)
        if offset < best[1]:
            best = (image, offset)
    return best[0]


def fill(x: int, y: int):
    global width, height

    pixelColor = get_pixel_color(x, y)
    pixelImage: Image = find_picture(pixelColor)
    pixelImage = pixelImage.resize((width, height))
    find_same_color(x, y, pixelColor, pixelImage)


def create_image(amount: int):
    global output_image, check_array
    # Vertical loop
    for y in range(0, amount):
        # Horizontal loop
        for x in range(0, amount):
            if (check_array[y][x] == 0):
                fill(x, y)
    directory = os.path.dirname(sys.argv[1])
    filename = os.path.basename(sys.argv[1])
    name, extension = os.path.splitext(filename)
    new_filename = f"{name}_result{extension}"
    output_image_path = os.path.join(directory, new_filename)
    output_image.save(output_image_path)

    time_needed = time.time() - start
    print(ANSIGREEN + "Process finished after",
          time_needed, "seconds" + STANDARD)
    output_image.show()


def create_image_list(folder) -> None:
    global image_list
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
    print("Using", len(image_list), "Images to create new image")


def check_input() -> bool:
    # Check amount of parameters
    if len(sys.argv) < 4:
        print(ANSIRED, "ERROR:", 4 - len(sys.argv),
              "Missing Parameters!", STANDARD)
        return False
    # Check if the given image is valid
    if not os.path.isfile(sys.argv[1]):
        print(ANSIRED, "ERROR:", sys.argv[1], "is not a file!", STANDARD)
        return False
    # Check if the given amount is valid
    if not sys.argv[2].isdigit():
        print(ANSIRED, sys.argv[2], "is not a number!", STANDARD)
        return False
    # Check if the given directory is valid
    if not os.path.isdir(sys.argv[3]):
        print(ANSIRED, "ERROR:", sys.argv[3], " is not a directory!", STANDARD)
        return False
    return True


def main():
    global input_image, output_image, value_array, check_array, image_list, width, height, amount
    if not check_input():
        return
    im = Image.open(sys.argv[1]).convert('RGB')
    amount = int(sys.argv[2])
    check_array = [[0 for i in range(amount)] for j in range(amount)]
    value_array = [[None for i in range(amount)] for j in range(amount)]
    image_width, image_height = im.size
    print("original:", im.size)
    width = image_width / amount
    height = image_height / amount
    im = im.resize((amount * width, amount * height))
    print("after:", im.size)
    # Rescale the Image, if the Pixels get to small. Scaling keeps the aspec ratio
    resized: bool = False
    if width < 10:
        resized = True
        im = im.resize(
            (int(10 * amount), int(10 * amount * image_height/image_width)))
    if height < 10:
        resized = True
        im = im.resize(
            (int(10 * amount * image_width/image_height), int(10 * amount)))
    if resized:
        image_width, image_height = im.size
        width = image_width / amount
        height = image_height / amount
    width = math.ceil(image_width / amount)
    height = math.ceil(image_height / amount)
    im = im.resize((amount * width, amount * height))
    # Setting global variables
    input_image = im
    output_image = Image.new('RGB', input_image.size)
    create_image_list(sys.argv[3])
    print("Creating an Image with", str(amount) + "x" + str(amount) + "(" + str(amount*amount)
          + ")" ' "Pixels":')
    print(width, height)
    create_image(amount)


start = time.time()
main()

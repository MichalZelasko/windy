from PIL import Image

from os import listdir, remove, mkdir
from os.path import isfile, join
from shutil import move

import numpy as np

def list_files(raw_pictures_path = "../../resources/raw_pictures"):
    file_list = [join(raw_pictures_path, f) for f in listdir(raw_pictures_path) if isfile(join(raw_pictures_path, f))]
    return sorted(file_list, reverse = True)

def convert_size(image_size_x, image_size_y, x_a = 80, x_b = -100, y_a = 0, y_b = 1500):
    if x_a is None:
        x_a = int(0.10 * image_size_x)
    if x_b is None:
        x_b = int(0.85 * image_size_x)
    if y_a is None:
        y_a = int(0.00 * image_size_y)
    if y_b is None:
        y_b = int(0.77 * image_size_y)
    return x_a, x_b, y_a, y_b

def convert_image(filepath, x_a = 80, x_b = -100, y_a = 0, y_b = 1500):
    image = Image.open(filepath)
    try:
        picture = np.array(image.getdata()).reshape(image.size[1], image.size[0], 4)
    except:
        picture = np.array(image.getdata()).reshape(image.size[1], image.size[0], 3)
    x_a, x_b, y_a, y_b = convert_size(image.size[1], image.size[0], x_a, x_b, y_a, y_b)
    return picture[x_a:x_b,y_a:y_b]

def save_image(image, filepath, newpath):
    filename = filepath.split("/")[-1].split("\\")[-1]
    try:
        PIL_image = Image.fromarray(image.astype('uint8'), 'RGBA')
    except:
        PIL_image = Image.fromarray(image.astype('uint8'), 'RGB')
    try:
        PIL_image.save(newpath + "/" + filename)
    except:
        mkdir(newpath)
        PIL_image.save(newpath + "/" + filename)

def convert_images(filepaths, newpath):
    for filepath in filepaths:
        image = convert_image(filepath)
        save_image(image, filepath, newpath)

def convert_raw_images(do_convert = True, rescource = "../../resources/raw_pictures_3", path = "../../resources/pictures_2", x_a = 80, x_b = -100, y_a = 0, y_b = 1500):
    if do_convert:
        print("Convertion")
        filepaths = list_files(raw_pictures_path = rescource)
        convert_images(filepaths, path, x_a = 80, x_b = -100, y_a = 0, y_b = 1500)
    else:
        print("Convertion stage omitted!")

def clean_directory(directory = "../../output/extrapolation"):
    filepaths = list_files(raw_pictures_path = directory)
    for file in filepaths:
        remove(file)

def move_files(name, path):
    source = name
    destination = path + "/" + name
    try:
        move(source, destination)
    except:
        mkdir(path)
        move(source, destination)

if __name__ == "__main__":
    convert_raw_images()


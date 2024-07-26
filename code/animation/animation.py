import matplotlib.pyplot as plt
from celluloid import Camera

from PIL import Image

import numpy as np

from os import listdir
from os.path import isfile, join

class Animation:

    def __init__(self, directory_path):
        self.directory_path = directory_path
        self.list_files()

    def list_files(self): 
        self.file_list = [join(self.directory_path, f) for f in listdir(self.directory_path) if isfile(join(self.directory_path, f))]

    def get_picture(self, filepath):
        image = Image.open(filepath)
        return np.array(image.getdata()).reshape(image.size[1], image.size[0], 4)
    
    def animate(self, filename):
        camera = Camera(plt.figure())
        for filepath in self.file_list:
            picture = self.get_picture(filepath)
            plt.imshow(picture)
            camera.snap()
        anim = camera.animate(blit=True)
        anim.save(filename)
        plt.show()
"""
This script generates an animation of a stream of frames. Useful to see the evolution of a typhoon
"""

import matplotlib.pyplot as plt
from matplotlib import animation
from utils import read_image, get_h5_filenames


# GET PICTURE FRAMES
class DisplayImage(object):
    def __init__(self, directory=None, data=None):
        if directory:
            self.files = get_h5_filenames(directory)
            self.mode = "directory"
            self.interval = 1
        elif data:
            self.files = data
            self.mode = "data"
            self.interval = 100
        else:
            self.mode = None
            raise Exception("Missing argument. Use either argument directory or data")
        self.im = None

    def get_image(self, index):
        if self.mode == "directory":
            return read_image(self.files[index])
        if self.mode == "data":
            return self.files[index]

    def init(self):
        """ Resets initial image value
        :return:
        """
        image = self.get_image(0)
        self.im.set_data(image)

    def animate(self, i):
        """ Updages the image frame
        :param i: Index of the frame
        """
        image = self.get_image(i)
        self.im.set_data(image)

    def run(self):
        """ Runs the animation
        """
        fig = plt.figure()
        self.im = plt.imshow(self.get_image(0), cmap="gist_yarg")
        print(len(self.files)-1)
        _ = animation.FuncAnimation(fig, self.animate, init_func=self.init, interval=self.interval,
                                    frames=len(self.files) - 1, repeat=True)
        plt.show()



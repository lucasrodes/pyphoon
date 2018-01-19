"""
This script generates an animation of a stream of frames. Useful to see the evolution of a typhoon
"""

import matplotlib.pyplot as plt
matplotlib.use
from matplotlib import animation
import moviepy.editor as mpy
import numpy as np


# GET PICTURE FRAMES
class DisplaySequence(object):
    def __init__(self, typhoon_sequence=None, raw_data=None, interval=100,
                 start_frame=0, end_frame=-1):
        if typhoon_sequence:
            self.data = typhoon_sequence.data['X']
        elif raw_data:
            self.data = raw_data
        else:
            raise Exception("Missing argument. Use either argument "
                            "<typhoon_sequence> or <raw_data>")
        self.data = self.data[start_frame:end_frame]
        self.name = typhoon_sequence.name
        self.interval = interval
        self.im = None
        self.start_frame = start_frame

    """
    def __init__(self, folder_path=None, h5file_path=None, data=None,
                 id=None, interval=100):
        if folder_path:
            _files = get_h5_filenames(folder_path)
            self.files = [read_image(file) for file in _files]
            self.id = folder_path.split('/')[-2]
        elif h5file_path:
            data = read_h5file(h5file_path)
            self.files = data['X']
            self.id = h5file_path.split('/')[-1].split('.h5')[0]
        elif data:
            self.files = data
            self.id = "untitled_"+str(dt.now().time())
        else:
            raise Exception("Missing argument. Use either argument "
                            "<directory>, <h5file_path> or <data>")
        self.interval = interval
        # Force overwrite if input argument is used
        if id:
            self.id = id
        self.im = None
    """

    def get_frame(self, index):
        """ Gets the image frame at position index
        :param index: Frame index within the typhoon sequence
        :return: Array containing the image
        """
        return self.data[index]

    def get_frame_gif(self, index):
        """ Gets the image frame at position index
        :param index: Frame index within the typhoon sequence
        :return: Array containing the image
        """
        frame = self.data[index]
        frames = np.array([frame, frame, frame])
        return frames

    def init(self):
        """ Resets initial image value
        :return:
        """
        image = self.get_frame(0)
        self.im.set_data(image)

    def animate(self, i):
        """ Updages the image frame
        :param i: Index of the frame
        """
        image = self.get_frame(i)
        plt.xlabel(self.start_frame+i)
        self.im.set_data(image)

    def run(self):
        """ Runs the animation
        """
        fig = plt.figure()
        plt.title(self.name)
        self.im = plt.imshow(self.get_frame(0), cmap="Greys")
        _ = animation.FuncAnimation(fig, self.animate, init_func=self.init,
                                    interval=self.interval, frames=len(
                self.data) - 1, repeat=True)
        plt.show()

    def generate_gif(self):
        """ Generates and stores a gif animation from the input typhoon sequence
        """
        clip = mpy.VideoClip(self.get_frame_gif, duration=15.0)
        clip.write_gif(self.name+'.gif', fps=15)

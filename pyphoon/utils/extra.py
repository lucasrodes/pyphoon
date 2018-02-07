import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation, rc
from IPython.display import HTML
from pyphoon.utils.utils import DisplaySequence
from pyphoon.utils.io import load_TyphoonSequence


class klas(object):
    def __init__(self):
        path_to_file = '../sampledata/197906.h5'
        self.sequence = load_TyphoonSequence(path_to_file)

        # First set up the figure, the axis, and the plot element we want to
        # animate
        self.fig, ax = plt.subplots()

        self.im = plt.imshow(self.sequence.images[0], cmap="Greys")

    # initialization function: plot the background of each frame
    def init(self):
        self.im.set_data(self.sequence.images[0])
        return self.im

    # animation function. This is called sequentially
    def animate(self, i):
        self.im.set_data(self.sequence.images[i])
        return (self.im,)

    def run(self):
        # call the animator. blit=True means only re-draw the parts that have changed.
        anim = animation.FuncAnimation(self.fig, self.animate,
                                       init_func=self.init,
                                       frames=73, interval=200)

        HTML(anim.to_html5_video())

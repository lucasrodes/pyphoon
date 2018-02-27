"""
This module provides tools to visualise Digital Typhoon related data.
This can be extremely helpful when you want to visualize a particular typhoon
sequence or generate a GIF from it.

Overall, this package is the perfect bridge between your stored data and your
thoughts. Just bring data to life with it and start exploring!

Getting Started
^^^^^

Let us visualize the sequence ``201626``, stored at "../data/201626.h5". We
load it, as usual, using
:func:`~pyphoon.utils.io.typhoonlist.load_typhoonlist_h5`.

>>> from pyphoon.io.typhoonlist import load_typhoonlist_h5
>>> from pyphoon.visualize import DisplaySequence
>>> # Load sequence from HDF file
>>> path = "data/201626.h5"
>>> typhoon_sequence = load_typhoonlist_h5(path_to_file=path)
>>> DisplaySequence(
    typhoon_sequence=typhoon_sequence,
    interval=100,
).run()

Methods and classes
^^^^^
"""

import matplotlib.pyplot as plt
from matplotlib import animation


class DisplaySequence(object):
    """ Used to animate a batch of images.

    :var typhoon_sequence: :class:`~pyphoon.utils.io.typhoonlist.TyphoonList`
        instance. Contains the data to bec displayed.
    :var interval: Interval between frames while visualizing the animation.
    :var start_frame: First frame of the sequence to visualize.
    :var end_frame: Last frame of the sequence to visualize.
    :var show_title: Set to false if no title should be shown in the figure.
    """
    def __init__(self, typhoon_sequence=None, interval=100, start_frame=0,
                 end_frame=None, show_title=True, alt_title=None):

        # Load images
        self.images = typhoon_sequence.get_data('images')
        self.ids = typhoon_sequence.get_id('images')

        # Load name
        self.name = typhoon_sequence.name

        # Define display window
        self.start_frame = start_frame
        if end_frame is None:
            self.images = self.images[start_frame:]
        else:
            self.images = self.images[start_frame:end_frame]

        # Frame interval
        self.interval = interval

        # Plot properties
        self.alt_title = alt_title
        self.show_title = show_title
        self.fig = plt.figure()
        self.ax = plt.gca()
        plt.axis('off')
        self.im = self.ax.imshow(self.images[0], cmap="Greys")

        """
        # Other stuff idk
        match_best_image = [
            flag == 1 for flag in typhoon_sequence.data['Y'][:, -2]
        ]
        self.flag_fix = typhoon_sequence.data['Y'][match_best_image, -1]
        """

    def _init(self):
        """ Resets initial image value
        """
        self.im.set_data(self.images[0])

    def _animate(self, i):
        """ Updates the image frame.

        :param i: Index of the frame
        :type i: int
        """
        if self.show_title:
            if self.alt_title is not None:
                self.ax.set_title(self.alt_title)
            else:
                self.ax.set_title(
                    str(self.ids[i]) + " | " +
                    str(self.start_frame + i) #+ " | "
                    # + str(int(self.flag_fix[i]))
                )
        self.im.set_data(self.images[i])

    def run(self, save=False, filename="untitled"):
        """ Runs the animation
        """
        anim = animation.FuncAnimation(self.fig,
                                       func=self._animate,
                                       init_func=self._init,
                                       interval=self.interval,
                                       frames=len(self.images),
                                       repeat=True
        )

        if save:
            anim.save(filename+'.gif', dpi=80, writer='imagemagick')

        plt.show()

    def run_html(self):
        """ Runs the animation
        """
        anim = animation.FuncAnimation(self.fig,
                                       func=self._animate,
                                       init_func=self._init,
                                       interval=self.interval,
                                       frames=len(self.images),
                                       repeat=True)
        return anim.to_html5_video()
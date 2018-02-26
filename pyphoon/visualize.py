"""
This module provides tools to visualise Digital Typhoon related data.
This can be extremely helpful when you want to visualize a particular typhoon
sequence or generate a GIF from it.

Overall, this package is the perfect bridge between your stored data and your
thoughts. Just bring data to life with it and start exploring!
"""

import matplotlib.pyplot as plt
from matplotlib import animation


############################
#        VISUALISE         #
############################

class DisplaySequence(object):
    """ Used to animate a batch of images.

    :var typhoon_sequence: :class:`~pyphoon.utils.io.TyphoonList` instance.
    :var raw_data: List of frames.
    :var name: Name of the sequence.
    :var interval: Interval between frames while visualizing the animation.
    :var start_frame: First frame of the sequence to visualize.
    :var end_frame: Last frame of the sequence to visualize.
    :var axis: Set to True if axis are to be displayed.
    :var show_title: Set to false if no title should be shown in the figure.

    |

    :Example:

        There are two options to visualize a sequence of frames. Either using a
        :class:`~pyphoon.utils.io.TyphoonList` instance

        >>> from pyphoon.io.typhoonlist import read_typhoonlist_h5
        >>> from pyphoon.visualize import DisplaySequence
        >>> # Load sequence from HDF file
        >>> path = "data/201626.h5"
        >>> typhoon_sequence = read_typhoonlist_h5(path_to_file=path)
        >>> DisplaySequence(
            typhoon_sequence=typhoon_sequence,
            interval=100,
            start_frame=0,
            end_frame=-1
        ).run()

        or directly feeding a raw list of frames.

        >>> from pyphoon.io.h5 import read_h5file
        >>> from pyphoon.io.typhoonlist import read_typhoonlist_h5
        >>> from pyphoon.visualize import DisplaySequence
        >>> # Load sequence from HDF file
        >>> path = "data/201626.h5"
        >>> typhoon_sequence = read_typhoonlist_h5(path_to_file=path)
        >>> data = typhoon_sequence.images
        >>> DisplaySequence(
            raw_data=data,
            name="201626",
            interval=100,
            start_frame=0,
            end_frame=-1
        ).run()
    """
    def __init__(self, typhoon_sequence=None, raw_data=None, name="untitled",
                 interval=100, start_frame=0, end_frame=None, axis=False,
                 show_title=True, alt_title=None):

        if typhoon_sequence is not None:
            self.data = typhoon_sequence.data['X']
            self.data_id = typhoon_sequence.data['X_ids']
            match_best_image = [
                flag == 1 for flag in typhoon_sequence.data['Y'][:, -2]
            ]
            self.flag_fix = typhoon_sequence.data['Y'][match_best_image, -1]
            self.name = typhoon_sequence.name
        elif raw_data is not None:
            self.data = raw_data
            self.data_id = ["no_id" for i in self.data]
            self.flag_fix = ["no_flag" for i in self.data]
            self.name = name
        else:
            raise Exception("Missing argument. Use either argument "
                            "<typhoon_sequence> or <raw_data>")
        if end_frame is None:
            self.data = self.data[start_frame:]
        else:
            self.data = self.data[start_frame:end_frame]
        self.start_frame = start_frame
        self.interval = interval

        self.axis = axis
        self.alt_title = alt_title
        self.show_title = show_title
        self.fig = plt.figure()
        self.ax = plt.gca()
        if not self.axis:
            plt.axis('off')
        self.im = self.ax.imshow(self.data[0], cmap="Greys")

    def _init(self):
        """ Resets initial image value
        """
        self.im.set_data(self.data[0])

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
                    str(self.data_id[i]) + " | " +
                    str(self.start_frame+i) + " | " +
                    str(int(self.flag_fix[i]))
                )
        self.im.set_data(self.data[i])

    def run(self, save=False, filename="untitled"):
        """ Runs the animation
        """
        anim = animation.FuncAnimation(self.fig,
                                       func=self._animate,
                                       init_func=self._init,
                                       interval=self.interval,
                                       frames=len(self.data),
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
                                       frames=len(self.data),
                                       repeat=True)
        return anim.to_html5_video()
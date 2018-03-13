"""

"""

import matplotlib.pyplot as plt
from matplotlib import animation


class DisplaySequence(object):
    """ Used to animate a batch of images.

    :param images: List with image arrays. Each element of the list must be an
        array of 2 dimensions.
    :type images: list
    :param images_ids: List of the ids of the elements in the list *images*.
    :type images_ids: list
    :param name: Name
    :type name: str
    :param interval: Interval between frames while visualizing the animation.
    :type interval: int
    :param start_frame: First image frame of the list to visualize.
    :type start_frame: int
    :param end_frame: Last image frame of the list to visualize.
    :type end_frame: int
    :param show_title: Set to false if no title should be shown in the figure.
    :type show_title: bool
    """
    def __init__(self, images, images_ids, name, interval=100, start_frame=0,
                 end_frame=None, show_title=True, alt_title=None):

        # TODO: check len(images) == len(images_ids)

        # Load images
        self.images = images
        self.ids = images_ids

        # Load name
        self.name = name

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
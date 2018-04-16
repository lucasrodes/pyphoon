"""
"""

import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib import gridspec
import numpy.ma as ma
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np


class DisplaySequence(object):
    """ Animates a sequence of images. Mainly to be used to display a typhoon
    sequence temporal evolution.

    :param images: List with image arrays. Each element of the list must be an
        array of 2 dimensions.
    :type images: list
    :param images_ids: List of the ids of the elements in the list *images*.
    :type images_ids: list
    :param interval: Interval between frames while visualizing the animation.
    :type interval: int
    :param start_frame: First image frame of the list to visualize.
    :type start_frame: int
    :param end_frame: Last image frame of the list to visualize.
    :type end_frame: int
    :param show_title: Set to false if no title should be shown in the figure.
    :type show_title: bool
    """
    def __init__(self, images, images_ids, interval=100, start_frame=0,
                 end_frame=None, show_title=True, alt_title=None):

        # TODO: check len(images) == len(images_ids)

        # Load images
        self.images = images
        self.ids = images_ids

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
        self.image_plt = self.ax.imshow(self.images[0], cmap="Greys")
        plt.axis('off')

    def _init(self):
        """ Resets initial image value
        """
        self._animate(0)

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
        self.image_plt.set_data(self.images[i])

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


class DisplayPredictedLabeledSequence(DisplaySequence):
    """ Animates a sequence of images and provides a visualisation of the
    network prediction. To be used to display a typhoon sequence temporal
    evolution. Currently, only working for binary predictions (0, 1).

    :param images: List with image arrays. Each element of the list must
        be an array of 2 dimensions.
    :type images: list
    :param images_ids: List of the ids of the elements in the list *images*.
    :type images_ids: list
    :type predictions: Network predictions for samples in **images**.
        Note that this list should only contain '0' and '1'.
    :param predictions: list
    :param ground_truth: Ground truth labels for samples in **images**.
        Note that this list should only contain '0' and '1'.
    :type ground_truth: list
    :param interval: Interval between frames while visualizing the
        animation.
    :type interval: int
    :param start_frame: First image frame of the list to visualize.
    :type start_frame: int
    :param end_frame: Last image frame of the list to visualize.
    :type end_frame: int
    :param show_title: Set to false if no title should be shown in the
        figure.
    :type show_title: bool
    """

    def __init__(self, images, images_ids, predictions, ground_truth,
                 interval=100, start_frame=0, end_frame=None,
                 show_title=True, alt_title=None):

        super().__init__(images, images_ids, interval=interval,
                         start_frame=start_frame, end_frame=end_frame,
                         show_title=show_title, alt_title=alt_title)

        # Data
        self.predictions = predictions
        self.ground_truth = ground_truth

        # Plot
        self.fig = plt.figure()
        gs = gridspec.GridSpec(1, 2, width_ratios=[3, 2])
        # Image plot
        self.ax1 = self.fig.add_subplot(gs[0])
        self.image_plt = self.ax1.imshow(self.images[0], cmap="Greys")

        # Label plot
        self.ax2 = self.fig.add_subplot(gs[1])
        colors = self._get_colors(self.predictions[0], self.ground_truth[0])
        self.ax2.barh(
            [0, 1],
            [1 - self.predictions[0], self.predictions[0]],
            color=colors,
            height=.5
        )
        self.ax2.set_yticks([0, 1])
        self.ax2.set_yticklabels(['TC', 'x-TC'])
        self.ax2.set_xlim(0, 1)
        plt.axis('off')

    @staticmethod
    def _get_colors(prediction, ground_truth):
        neutral = [.7, .7, .7]
        incorrect = [.7, 0, 0]
        correct = [0, .8, 0]
        colors = [neutral, neutral]

        prediction = int(round(prediction))
        if prediction == ground_truth:
            colors[prediction] = correct
        else:
            colors[prediction] = incorrect

        return colors

    def _animate(self, i):
        """ Updates the image frame.

        :param i: Index of the frame
        :type i: int
        """

        self.image_plt.set_data(self.images[i])
        plt.axis('off')
        self.ax2.clear()
        colors = self._get_colors(self.predictions[i], self.ground_truth[i])
        self.ax2.barh(
            [0, 1],
            [1 - self.predictions[i], self.predictions[i]],
            color=colors,
            height=.5
        )

        self.ax2.set_yticks([0, 1])
        self.ax2.set_yticklabels(['TC', 'x-TC'])
        self.ax2.set_xlim(0, 1)

        # Set title
        if self.show_title:
            if self.alt_title is not None:
                self.fig.suptitle(self.alt_title)
            else:
                self.fig.suptitle(
                    str(self.ids[i]) + " | " +
                    str(self.start_frame + i)
                )
                self.ax1.set_title("Satellite image")
                self.ax2.set_title("Network output")


def nice_imshow(ax, X, colorbar=False, vmin=None, vmax=None, cmap=None,
                barsize=None):
    """ Wrapper around plt.imshow. Code from `here`_.

    ..  _here:
        code from: https://github.com/julienr/ipynb_playground/blob/master/keras/convmnist/keras_cnn_mnist.ipynb

    :param ax: Plot axis.
    :type ax: matplotlib.axes.Axes instance
    :param X: 2D image array.
    :type X: numpy.array
    :param colorbar:
    :param vmin: Minimum value in the bar.
    :type vmin: float
    :param vmax: Maximum value in the bar.
    :type vmax: float
    :param cmap: If None, default to rc image.cmap value. cmap is ignored if
        X is 3-D, directly specifying RGB(A) values.
    :param barsize: Tick label font size in points or as a string (e.g., ‘large’).
    :type barsize: float or str
    """
    # if cmap is None:
    #    cmap = cm.jet
    if vmin is None:
        vmin = X.min()
    if vmax is None:
        vmax = X.max()
    divider = make_axes_locatable(ax)
    im = ax.imshow(X, vmin=vmin, vmax=vmax, interpolation='nearest',
                   cmap=cmap)
    if colorbar:
        cax = divider.append_axes("right", size="5%", pad=0.1)
        cbar = plt.colorbar(im, cax=cax)
        if barsize:
            cbar.ax.tick_params(labelsize=barsize)


def make_mosaic(imgs, nrows, ncols, border=1):
    """ Given a set of images with all the same shape, makes a
    mosaic with nrows and ncols

    :param imgs: Array of shape (N, W, H), where N: #images, W: width and H:
        height.
    :type imgs: numpy.array
    :param nrows: Number of rows in the plot grid.
    :type nrows: int
    :param ncols: Number of columns in the plot grid.
    :type ncols: int
    :param border: padding between images.
    :type border: int or float.
    :return:
    """
    nimgs = imgs.shape[0]
    imshape = imgs.shape[1:]

    mosaic = ma.masked_all((nrows * imshape[0] + (nrows - 1) * border,
                            ncols * imshape[1] + (ncols - 1) * border),
                           dtype=np.float32)

    paddedh = imshape[0] + border
    paddedw = imshape[1] + border
    for i in range(nimgs):
        row = int(np.floor(i / ncols))
        col = i % ncols

        mosaic[row * paddedh:row * paddedh + imshape[0],
        col * paddedw:col * paddedw + imshape[1]] = imgs[i]
    return mosaic

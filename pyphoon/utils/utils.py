"""

"""
from os import listdir
from os.path import isfile, join
from datetime import datetime as dt
import matplotlib.pyplot as plt
from matplotlib import animation
# import moviepy.editor as mpy


def get_ids_images(sequence_folder):
    """ Gets ids for each image within a folder.

    :param sequence_folder: Array containing the data from Best Track
    :type sequence_folder:
    :return: List with the ids of all images.
    :rtype: list

    .. seealso:: :func:`get_id_image`
    """
    ids = [get_id_image(f) for f in listdir(sequence_folder) if isfile(
        join(sequence_folder, f)) and f.endswith('.h5')]
    return sorted(ids)


def get_id_image(path_to_file):
    """ Gets id of an image. The id is constructed using the date of the
    typhoon. Note that typhoons from different sequences might have the
    same ID since they were recorded at the same time. Therefore,
    we recommend always using the typhoon ID together with the sequence
    identifier, as this way we ensure the uniqueness.

    To build the image id, the name of the original HDF file is used,
    which have the following structure:

    *YYYYMMDDHH-typhoon_id-satellite_model.h5*

    In particular we only preserve the beginning of the filename, namelu
    *YYYYMMDDHH*

    :param path_to_file: Path to the HDF image file.
    :type path_to_file: str
    :return: Image id
    :rtype: int
    """
    return int(path_to_file.split('-')[0])


def get_ids_best(best_data):
    """ Gets ids for each sample in the best track data. It uses the date of
    the data to generate the id.

    :param best_data: Array containing the data from Best Track.
    :type best_data: numpy.array
    :return: List with the ids of all samples from input Best Track data.
    :rtype: list
    """
    ids = [int(dt(int(d[0]), int(d[1]), int(d[2]), int(d[3])).strftime(
        "%Y%m%d%H")) for d in best_data]
    return ids


def h5file_2_name(path_h5file):
    """ Given a path to an HDF file, obtains the file name (without format
    extension).

    :param path_h5file: Path to an HDF file.
    :type path_h5file: str
    :return: Name of file
    :rtype: str

    |

    :Example:

        >>> from pyphoon.utils.utils import h5file_2_name
        >>> h5file_2_name("path/to/filename.h5")
        'filename'
    """
    return path_h5file.split('/')[-1].split('.h5')[0]


def folder_2_name(path_folder):
    """ Given a path to an HDF file, obtains the file name (without format
    extension).

    :param path_folder: Path to a folder.
    :type path_folder: str
    :return: Name of file
    :rtype: str

    |

    :Example:

        >>> from pyphoon.utils.utils import folder_2_name
        >>> folder_2_name("path/to/folder")
        'folder'
    """
    name = path_folder.split('/')[-1]
    if name == '':
        name = path_folder.split('/')[-2]
    return name


class DisplaySequence(object):
    """ Used to animate a batch of images.

    :cvar typhoon_sequence: :class:`~pyphoon.utils.io.TyphoonSequence` instance.
    :cvar raw_data: List of frames.
    :cvar name: Name of the sequence.
    :cvar interval: Interval between frames while visualizing the animation.
    :cvar start_frame: First frame of the sequence to visualize.
    :cvar end_frame: Last frame of the sequence to visualize.

    |

    :Example:

        There are two options to visualize a sequence of frames. Either using a
        :class:`~pyphoon.utils.io.TyphoonSequence` instance

        >>> from pyphoon.utils.io import load_TyphoonSequence
        >>> # Load sequence from HDF file
        >>> path = "data/201626.h5"
        >>> typhoon_sequence = load_TyphoonSequence(path_to_file=path)
        >>> DisplaySequence(
            typhoon_sequence=typhoon_sequence,
            interval=100,
            start_frame=0,
            end_frame=-1
        ).run()

        or directly feeding a raw list of frames.

        >>> from pyphoon.utils.io import read_h5file, load_TyphoonSequence
        >>> # Load sequence from HDF file
        >>> path = "data/201626.h5"
        >>> typhoon_sequence = load_TyphoonSequence(path_to_file=path)
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
                 interval=100, start_frame=0, end_frame=None):
        if typhoon_sequence:
            self.data = typhoon_sequence.data['X']
            self.name = typhoon_sequence.name
        elif raw_data:
            self.data = raw_data
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

        self.fig = plt.figure()
        self.ax = plt.gca()
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
        self.ax.set_title(self.name + " | " + str(self.start_frame+i))
        self.im.set_data(self.data[i])

    def run(self):
        """ Runs the animation
        """
        _ = animation.FuncAnimation(self.fig,
                                    func=self._animate,
                                    init_func=self._init,
                                    interval=self.interval,
                                    frames=len(self.data) - 1,
                                    repeat=True)
        plt.show()

    def run_html(self):
        """ Runs the animation
        """
        anim = animation.FuncAnimation(self.fig,
                                       func=self._animate,
                                       init_func=self._init,
                                       interval=self.interval,
                                       frames=len(self.data) - 1,
                                       repeat=True)
        return anim.to_html5_video()


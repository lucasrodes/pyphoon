"""

"""
from datetime import datetime as dt
import matplotlib.pyplot as plt
from matplotlib import animation
from pyphoon.io.h5 import get_h5_filenames
# import moviepy.editor as mpy


############################
#        IMAGE IDs         #
############################

def get_image_ids(sequence_folder):
    """ Gets ids for each image within a folder.

    :param sequence_folder: Folder name containing images stored as single H5
        files.
    :type sequence_folder: str
    :return: List with the ids of all images.
    :rtype: list

    .. seealso:: :func:`get_image_id`
    """
    files = get_h5_filenames(sequence_folder)
    ids = [get_image_id(file) for file in files]
    # ids = [get_image_id(f) for f in listdir(sequence_folder) if isfile(
    #    join(sequence_folder, f)) and f.endswith('.h5')]
    return sorted(ids)


def get_image_id(filename):
    """ Gets id of an image. The id is constructed using the date of the
    typhoon. Note that typhoons from different sequences might have the
    same ID since they were recorded at the same time. Therefore, the final
    id is constructed using both the date and the typhoon ID together.

    To build the image id, the name of the original HDF file is used,
    which have the following structure:

    *YYYYMMDDHH-<typhoon id>-<satellite model>.h5*

    We can then parse it to the id, namely
    *<typhoon id>_YYYYMMDDHH*

    :param filename: Name of the HDF image file.
    :type filename: str
    :return: Image frame id
    :rtype: int
    """
    return filename.split('-')[1] + "_" + filename.split('-')[0]


############################
#         BEST IDs         #
############################

def get_best_ids(best_data, seq_name):
    """ Gets ids for each sample in the best track data. It uses the date of
    the data to generate the id.

    :param best_data: Array containing the data from Best Track.
    :type best_data: numpy.array
    :param seq_name: Name of the typhoon sequence
    :type seq_name: str
    :return: List with the ids of all samples from input Best Track data.
    :rtype: list
    """
    ids = [
        seq_name + "_" + dt(int(d[0]), int(d[1]), int(d[2]),
                            int(d[3])).strftime("%Y%m%d%H") for d in best_data
    ]
    return ids


############################
#          DATES           #
############################

def get_date_from_id(identifier):
    """ Gets the date of the frame at position idx

    :param identifier: Identifier of an image or best track frame
    :type identifier: str
    :return: Date of the frame
    :rtype: datetime.datetime
    """
    # Ignore typhoon id section
    identifier = identifier.split('_')[1]

    year = int(identifier[:4])
    month = int(identifier[4:6])
    day = int(identifier[6:8])
    hour = int(identifier[8:])
    date = dt(year, month, day, hour)
    return date


############################
#       IMAGE DATES        #
############################

def get_image_dates(sequence_folder):
    """ Gets the dates from all image H5 files stored in *sequence_folder*.

    :param sequence_folder: Folder name containing images stored as single H5
        files.
    :type sequence_folder: str
    :return: List with the dates of all images.
    :rtype: list

    .. seealso:: :func:`get_image_date`
    """
    files = get_h5_filenames(sequence_folder)
    dates = [get_image_date(file) for file in files]
    return dates


def get_image_date(filename):
    """ Gets the date from

    :param filename: Name of the HDF image file.
    :type filename: str
    :return: Date the image with a given *filename* was taken.
    :rtype: datetime.datetime
    """
    identifier = filename.split('-')[0]
    year = int(identifier[:4])
    month = int(identifier[4:6])
    day = int(identifier[6:8])
    hour = int(identifier[8:])
    date = dt(year, month, day, hour)
    return date


############################
#        BEST DATES        #
############################

def get_best_dates(best_data):
    """ Gets the dates of samples in a best data array

    :param best_data: Array containing the data from Best Track.
    :type best_data: numpy.array
    :return: List of datetime.datetime elements.
    :rtype: list
    """
    dates = [dt(int(d[0]), int(d[1]), int(d[2]), int(d[3])) for d in best_data]
    return dates


############################
#          OTHERS          #
############################

def h5file_2_name(path_h5file):
    """ Given a path to an HDF file, obtains the file name (without format
    extension).

    :param path_h5file: Path to an HDF file.
    :type path_h5file: str
    :return: Name of file
    :rtype: str

    |

    :Example:

        >>> from pyphoon.utils import h5file_2_name
        >>> h5file_2_name("path/to/filename.h5")
        'filename'
    """
    return path_h5file.split('/')[-1].split('.h5')[0]


def folder_2_name(path_folder):
    """ Given a path to a folder, obtains the file name (without format
    extension).

    :param path_folder: Path to a folder.
    :type path_folder: str
    :return: Name of file
    :rtype: str

    |

    :Example:

        >>> from pyphoon.utils import folder_2_name
        >>> folder_2_name("path/to/folder")
        'folder'
    """
    name = path_folder.split('/')[-1]
    if name == '':
        name = path_folder.split('/')[-2]
    return name


############################
#        VISUALISE         #
############################

class DisplaySequence(object):
    """ Used to animate a batch of images.

    :cvar typhoon_sequence: :class:`~pyphoon.utils.io.TyphoonList` instance.
    :cvar raw_data: List of frames.
    :cvar name: Name of the sequence.
    :cvar interval: Interval between frames while visualizing the animation.
    :cvar start_frame: First frame of the sequence to visualize.
    :cvar end_frame: Last frame of the sequence to visualize.
    :cvar axis: Set to True if axis are to be displayed.
    :cvar show_title: Set to false if no title should be shown in the figure.

    |

    :Example:

        There are two options to visualize a sequence of frames. Either using a
        :class:`~pyphoon.utils.io.TyphoonList` instance

        >>> from pyphoon.io import read_typhoonlist_h5
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
        >>> from pyphoon.io import read_typhoonlist_h5
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


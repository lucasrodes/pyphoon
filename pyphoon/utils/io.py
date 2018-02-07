"""
This module provides a handful of tools to read (and also write) several
data formats (e.g. HDF and TSV files). Therefore, this has become an
essential tool to interact with the Digital Typhoon data.

+-------------------------------------------+---------------------------------------------------------------------------------------------------+
| method/class name                         | Description                                                                                       |
+===========================================+===================================================================================================+
| :func:`create_TyphoonSequence`            | Creation of a :class:`TyphoonSequence` instance using best track and satellite image data sources |
+-------------------------------------------+---------------------------------------------------------------------------------------------------+
| :func:`load_TyphoonSequence`              | Load previously stored (as H5) typhoon sequence data as a :class:`TyphoonSequence` instance       |
+-------------------------------------------+---------------------------------------------------------------------------------------------------+
| :class:`TyphoonSequence`                  | Class encapsulating images and best track data of a certain typhoon sequence                      |
+-------------------------------------------+---------------------------------------------------------------------------------------------------+
| :func:`get_h5_filenames`                  | Class encapsulating images and best track data of a certain typhoon sequence                      |
+-------------------------------------------+---------------------------------------------------------------------------------------------------+
| :func:`read_h5file`                       | Reads an HDF file and returns its content as dictionary.                                          |
+-------------------------------------------+---------------------------------------------------------------------------------------------------+
| :func:`write_h5file`                      | Constructs and stores an H5 file containing certain given data.                                   |
+-------------------------------------------+---------------------------------------------------------------------------------------------------+
| :func:`read_tsvs`                         | Reads all TSV files from a given directory and merges them into a single list                     |
+-------------------------------------------+---------------------------------------------------------------------------------------------------+
| :func:`read_tsv`                          | Reads the content from a single TSV file and merges it into a single list                         |
+-------------------------------------------+---------------------------------------------------------------------------------------------------+
| :func:`check_constant_distance_in_tsv`    | Checks if data samples in a TSV file are always at a certain constant time distance               |
+-------------------------------------------+---------------------------------------------------------------------------------------------------+
| :func:`read_images`                       | Reads all HDF files containing images within a given folder.                                      |
+-------------------------------------------+---------------------------------------------------------------------------------------------------+
| :func:`read_image`                        | Reads an HDF file containing an image                                                             |
+-------------------------------------------+---------------------------------------------------------------------------------------------------+

"""
from pyphoon.utils import get_ids_best, get_ids_images, h5file_2_name, \
    folder_2_name
from pyphoon.io.h5 import write_h5file
from datetime import datetime as dt


#######################################
#  TyphoonSequence RELATED FUNCTIONS  #
#######################################

def create_TyphoonSequence(path_images, path_best=None):
    """ Groups the images and best track data from a certain typhoon and
    generates a `TyphoonSequence` instance. As input it requires an HDF
    file containing the images from a certain typhoon sequence an,
    optionally, a TSV file with best track data of the same typhoon
    sequence. If the HDF and TSV files refer to different sequences the
    data will be wrongly saved.

    This function is very relevant when mergin the two main data
    components of this dataset: Images (folder with h5 files) and Best
    Track (TSV file).

    :param path_images: Path to the typhoon sequence H5 file (images data).
    :type path_images: str
    :param path_best: Path to the typhoon sequence TSV file (best track data).
        given sequence.
    :type path_best: str
    :return: Object containing images and bes track data of a typhoon sequence.
    :rtype: TyphoonSequence

    .. seealso:: :class:`TyphoonSequence`
    """
    # Get the images from the HDF file and their corresponding IDs.
    data = {
        'X': read_images(path_images),
        'X_ids': get_ids_images(path_images),
    }
    # Get the best track data from the TSV file and their corresponding IDs.
    if path_best:
        Y = read_tsv(path_best)
        data['Y'] = Y
        data['Y_ids'] = get_ids_best(Y)

    # Get name of the
    name = folder_2_name(path_images)
    return TyphoonSequence(data, name=name)


def load_TyphoonSequence(path_to_file, path_images=None, overwrite_ids=False):
    """ Loads a typhoon sequence stored as an HDF file as an instance of
    TyphoonSequence. The loaded data is assumed to have, at least,
    one field corresponding to the images (X) and another to the
    corresponding best track metadata (Y). Additionally, it may have ids.

    :param path_to_file: Path to the HDF file to load.
    :type path_to_file: str
    :param path_images: Path to the original image folder. This path is
        relevant if the IDs of the images are to be set. Otherwise t
    :type path_images: str, optional
    :param overwrite_ids: Set to True if the loaded typhoon sequence does
        have IDs already but you want to overwrite them.
    :type overwrite_ids: bool
    :return: Object containing images and bes track data of a typhoon sequence.
    :rtype: TyphoonSequence instance

    .. seealso:: :class:`TyphoonSequence`
    """
    # Read HDF file
    data = read_h5file(path_to_file)
    # Get ids
    if 'X_ids' not in data and path_images:
        data['X_ids'] = get_ids_images(path_images)
    if 'Y_ids' not in data:
        data['Y_ids'] = get_ids_best(data['Y'])
    if overwrite_ids:
        data['X_ids'] = get_ids_images(path_images)
        data['Y_ids'] = get_ids_best(data['Y'])
    else:
        data['X_ids'] = sorted(data['X_ids'])

    name = h5file_2_name(path_to_file)
    return TyphoonSequence(data, name=name)


class TyphoonSequence(object):
    """ Object encapsulating the images and best track data of a certain
    typhoon sequence.

    :cvar data: Dictionary-shape data. The details on the shape of the
        dictionary are according to the output format of :func:`read_h5file`.
    :cvar name: Name of the sequence (str).

    |

    :Example: Creating a TyphoonSequence object and storing it as an HDF
        file is very easy. You just need to create an instance of
        TyphoonSequence and pass the paths of the image files and best
        track data fro ma certain typhoon sequence. This way, both data are
        merged and can be stored as a single HDF file.

        Accessing only one single file rather than several files per
        each sequence significantly reduces execution time.

        >>> from pyphoon.utils.io import create_TyphoonSequence
        >>> path_images='../original_data/image/201626/'
        >>> path_best='../original_data/jma/201626.tsv'
        >>> typhoon_sequence = create_TyphoonSequence(path_images=path_images, path_best=path_best)
        >>> typhoon_sequence.save_as_h5("data/201626.h5")

        Loading a sequence as a TyphoonSequence object can be
        done in multiple ways. The easiest way is to retrieve the data
        from an HDF file generated using `create_TyphoonSequence`.

        >>> from pyphoon.utils.io import load_TyphoonSequence
        >>> # Load sequence from HDF file
        >>> path = "data/201626.h5"
        >>> typhoon_sequence = load_TyphoonSequence(path_to_file=path)

        We can also load a typhoon sequence straight from a dictionary with
        format: {X: ..., Y: ...}. The details on the shape of the dictionary
        are according to the output format of :func:`read_h5file`.

        >>> from pyphoon.io import TyphoonList
        >>> from pyphoon.io.h5 read_h5file
        >>> # Load sequence from a dictionary (format {X: ..., Y:...})
        >>> data = read_h5file(path_to_file="data/201626.h5")
        >>> typhoon_sequence_2 = TyphoonSequence(data=data, name="X")

        Once a sequence is loaded, you may want to plot a specific frame.
         it is
        very simple. Only
        need to set a start and end frames and an interval (time between
        frames) value.

        >>> import matplotlib.pyplot as plt
        >>> plt.imshow(typhoon_sequence_2.image[10])
        >>> plt.show())

    .. seealso:: :class:`~pyphoon.utils.DisplaySequence`

    """
    def __init__(self, data, name):
        self.data = data
        self.name = name

    def save_as_h5(self, path_to_file, compression=None):
        """ Stores the data as an HDF file.

        :param path_to_file: Path to the directory where typhoon sequence data
            will be stored.
        :type path_to_file: str
        :param compression: Set to a compression format. Find more details at
            the `h5py documentation`_
        :type compression: str, default None

        .. _h5py documentation:
            http://docs.h5py.org/en/latest/high/dataset.html
        """
        write_h5file(self.data, path_to_file, compression=compression)

    @property
    def images(self):
        """
        :return: List with sequence images
        :rtype: list
        """
        return self.data['X']

    @property
    def images_ids(self):
        """
        :return: List with image ids.
        :rtype: list
        """
        return self.data['X_ids']

    def images_complete_id(self, idx):
        """ Gets the complete id of a certain image frame. This means that
        typhoon name is also included. In particular it has the the following
        structure: *typhonID_YYYYMMDDHH*.

        :param idx: Index of the image frame.
        :type idx: int
        :return: Complete id of the image frame.
        :rtype: str
        """
        return self.name + "_" + str(self.images_ids[idx])

    def images_date(self, idx):
        """ Obtains the date from a certain image frame.

        :param idx: Image frame position at the sequence.
        :type idx: int
        :return: Date of image frame at position idx.
        :rtype: datetime.datetime
        """
        return self.get_date_from_id(str(self.images_ids[idx]))

    @property
    def best(self):
        """
        :return: List with best track data.
        :rtype: list
        """
        return self.data['Y']

    @property
    def best_ids(self):
        """
        :return: List with best track ids.
        :rtype: list
        """
        return self.data['Y_ids']

    def best_complete_id(self, idx):
        """ Gets the complete id of a certain best track frame. This means that
        typhoon name is also included. In particular it has the the following
        structure: *typhonID_YYYYMMDDHH*.

        :param idx: Index of the best track frame.
        :type idx: int
        :return: Complete id of the best track frame.
        :rtype: str
        """
        return self.name + "_" + str(self.best_ids[idx])

    def best_date(self, idx):
        """ Obtains the date from a certain best track frame.

        :param idx: Best track frame position at the sequence.
        :type idx: int
        :return: Date of best track frame at position idx.
        :rtype: datetime.datetime
        """
        return self.get_date_from_id(self.best_ids[idx])

    def get_date_from_id(self, identifier):
        """ Gets the date of the frame at position idx

        :param identifier: Identifier of an image or best track frame
        :type identifier:
        :return: Date of the frame
        :rtype: datetime.datetime
        """
        year = int(identifier[:4])
        month = int(identifier[4:6])
        day = int(identifier[6:8])
        hour = int(identifier[8:])
        date = dt(year, month, day, hour)
        return date

    def get_image_frames_distance(self, idx_0, idx_1, mode='image'):
        """ Obtains the time distance in seconds between frames at position
        idx_0 and idx_1.

        :param idx_0: Index of first frame.
        :type idx_0: int
        :param idx_1: Index of second frame.
        :type idx_1: int
        :param mode: Frame distance can be obtained from two sources: images
            or best track data. For the former use ``mode='image'``, for the
            latter use ``mode='best'``.
        :type mode: str
        :return: Time distance between frames in seconds.
        :rtype: int
        """
        # Get identifiers
        if mode == 'image' or mode == 'best':
            if mode == 'image':
                date_frame_0 = self.images_date(idx_0)
                date_frame_1 = self.images_date(idx_1)
            else:
                date_frame_0 = self.best_date(idx_0)
                date_frame_1 = self.best_date(idx_1)
            # Get time distance between identifiers
            return (date_frame_1 - date_frame_0).total_seconds()
        else:
            raise Exception("argument mode can take two values: image or best")

    def insert_frames(self, frames, frames_ids, idx):
        """ Insert a batch of frames at a certain position. It also adds the
        corresponding image_ids.

        :param frames: List of names to be inserted.
        :type frames: list
        :param frames_ids: List of image ids corresponding to frames.
        :type frames_ids: list
        :param idx: Position at which frames are to be inserted.
        :type idx: int
        """
        # TODO: Check that index within possible range
        # Insert frames
        self.images[idx:idx] = frames
        # Insert ids
        self.images_ids[idx:idx] = frames_ids
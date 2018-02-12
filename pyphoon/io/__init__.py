"""
This module provides a handful of tools to read (and also write) several
data formats (e.g. HDF and TSV files). Therefore, this has become an
essential tool to interact with the Digital Typhoon data.

+-------------------------------------------+---------------------------------------------------------------------------------------------------+
| method/class name                         | Description                                                                                       |
+===========================================+===================================================================================================+
| :class:`TyphoonList`                      | Class encapsulating images and best track data of a certain typhoon sequence                      |
+-------------------------------------------+---------------------------------------------------------------------------------------------------+
| :func:`create_typhoonlist_from_source`    | Creation of a :class:`TyphoonSequence` instance using best track and satellite image data sources |
+-------------------------------------------+---------------------------------------------------------------------------------------------------+
| :func:`read_typhoonlist_h5`               | Load previously stored (as H5) typhoon sequence data as a :class:`TyphoonSequence` instance       |
+-------------------------------------------+---------------------------------------------------------------------------------------------------+
"""
from pyphoon.utils import get_best_ids, get_image_ids, h5file_2_name, \
    folder_2_name
from pyphoon.io.h5 import read_h5file, write_h5file, read_images
from pyphoon.io.tsv import read_tsv
from pyphoon.utils import get_date_from_id
import numpy as np
import time


class TyphoonList(object):
    """ Object encapsulating the images and best track data of a certain
    typhoon sequence.

    :cvar data: Dictionary-shape data. The details on the shape of the
        dictionary are according to the output format of :func:`read_h5file`.
    :cvar name: Name of the sequence (str).

    |

    :Example: Creating a TyphoonList object and storing it as an HDF
        file is very easy. You just need to create an instance of
        TyphoonList and pass the paths of the image files and best
        track data fro ma certain typhoon sequence. This way, both data are
        merged and can be stored as a single HDF file.

        Accessing only one single file rather than several files per
        each sequence significantly reduces execution time.

        >>> from pyphoon.io import create_typhoonlist_from_source
        >>> path_images='../original_data/image/201626/'
        >>> path_best='../original_data/jma/201626.tsv'
        >>> typhoon_sequence = create_typhoonlist_from_source(path_images=path_images, path_best=path_best)
        >>> typhoon_sequence.save_as_h5("data/201626.h5")

        Loading a sequence as a TyphoonList object can be
        done in multiple ways. The easiest way is to retrieve the data
        from an HDF file generated using `create_typhoonlist_from_source`.

        >>> from pyphoon.io import read_typhoonlist_h5
        >>> # Load sequence from HDF file
        >>> path = "data/201626.h5"
        >>> typhoon_sequence = read_typhoonlist_h5(path_to_file=path)

        We can also load a typhoon sequence straight from a dictionary with
        format: {X: ..., Y: ...}. The details on the shape of the dictionary
        are according to the output format of :func:`read_h5file`.

        >>> from pyphoon.io import TyphoonList
        >>> from pyphoon.io.h5 import read_h5file
        >>> # Load sequence from a dictionary (format {X: ..., Y:...})
        >>> data = read_h5file(path_to_file="data/201626.h5")
        >>> typhoon_sequence_2 = TyphoonList(data=data, name="X")

        Once a sequence is loaded, you may want to plot a specific frame.
         it is very simple. Only need to set a start and end frames and an
         interval (time between frames) value.

        >>> import matplotlib.pyplot as plt
        >>> plt.imshow(typhoon_sequence_2.image[10])
        >>> plt.show())

    .. seealso:: :class:`~pyphoon.utils.__init__.DisplaySequence`

    """
    def __init__(self, data, name):
        self.data = data
        self.name = name

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

    def images_dates(self, idx):
        """ Obtains the date from a certain image frame.

        :param idx: Frame index from *self.images* to retrieve date from.
        :type idx: int
        :return: List with dates of image frames.
        :rtype: datetime.datetime
        """
        return get_date_from_id(self.data['X_ids'][idx])

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

    def best_dates(self, idx):
        """ Obtains the date from a certain best track frame.

        :param idx: Sample index from *self.best* to retrieve date from.
        :type idx: int
        :return: List with dates of best track frame at position idx.
        :rtype: datetime.datetime
        """
        return get_date_from_id(self.data['Y_ids'][idx])

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
        :return: Time distance between frames in hours.
        :rtype: int
        """
        # Get identifiers
        if mode == 'image' or mode == 'best':
            if mode == 'image':
                date_frame_0 = self.images_dates(idx_0)
                date_frame_1 = self.images_dates(idx_1)
            else:
                date_frame_0 = self.best_dates(idx_0)
                date_frame_1 = self.best_dates(idx_1)
            # Get time distance between identifiers
            return int((date_frame_1 - date_frame_0).total_seconds() // 3600)
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
        # TODO: Insert in image array is very slow!
        # Insert frames
        self.data['X'] = np.insert(self.data['X'], idx, frames, axis=0)

        # Insert ids
        self.data['X_ids'][idx:idx] = frames_ids

    @property
    def shape(self):
        """ Returns shape of typhoonlist as: (a, b, c, d), where a: shape of
        image frame array, b: shape of image ids list, c: shape of best data
        array, d: shape of best data ids list.

        :return: Shape of typhoonlist
        :rtype: tuple
        """
        s0 = self.data['X'].shape
        s1 = (len(self.data['X_ids']), 1)
        s2 = self.data['Y'].shape
        s3 = (len(self.data['Y_ids']), 1)
        s = (s0, s1, s2, s3)
        return s

    def __len__(self):
        """ Returns number of elements in the list. If not consistent (i.e.
        number of frames is not same as number of best data None value is
        returned). To make sure that it returns a valid number, note that the
        list should be read using the option *alignment* from
        :func:`read_typhoonlist_h5`.

        :return: Length of list
        """
        if len(self.data['X']) == \
                len(self.data['X_ids']) == \
                len(self.data['Y']) == \
                len(self.data['Y_ids']):
            return len(self.data['X'])
        else:
            return None

    def __iter__(self):
        if len(self):
            for i in range(len(self)):
                v0 = self.data['X'][i]
                v1 = self.data['X_ids'][i]
                v2 = self.data['Y'][i]
                v3 = self.data['Y_ids'][i]
                yield {'X': v0, 'X_ids': v1, 'Y': v2, 'Y_ids': v3}
        else:
            yield None

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


def merge_typhoonlists(typhoon_list1, typhoon_list2):
    return typhoon_list1


#######################################
#        READ/WRITE TYPHOONLIST       #
#######################################

def create_typhoonlist_from_source(path_images, path_best=None):
    """ Groups the images and best track data from a certain typhoon and
    generates a `TyphoonList` instance. As input it requires an HDF
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
    :rtype: TyphoonList

    .. seealso:: :class:`TyphoonList`
    """
    # Get sequence name
    seq_name = folder_2_name(path_images)

    # Get the images from the HDF file and their corresponding IDs.
    data = {
        'X': read_images(path_images),
        'X_ids': get_image_ids(path_images),
    }

    # Get the best track data from the TSV file and their corresponding IDs.
    # Also, detect samples in best data belonging to existing image frames in
    #  the sequence
    if path_best:
        Y = np.array(read_tsv(path_best))
        Y = np.append(Y, np.zeros((Y.shape[0], 2)), axis=1)
        data['Y'] = Y
        data['Y_ids'] = get_best_ids(Y, seq_name)
        data['Y'][:, -2] = [best_id in data['X_ids'] for best_id in data[
            'Y_ids']]

    # Ensure that all image have associated best data!
    data['X'] = np.array([data['X'][i] for i in range(len(data['X'])) if
                          data['X_ids'][i] in data['Y_ids']])
    data['X_ids'] = [image_id for image_id in data['X_ids'] if image_id in
                     data['Y_ids']]
    # Get name of the
    name = folder_2_name(path_images)
    return TyphoonList(data, name=name)


# Johny M. Reggae artist
def read_typhoonlist_h5(path_to_file, path_images=None, overwrite_ids=False,
                        overwrite_flags=False, alignment=False):
    """ Loads a typhoon sequence stored as an HDF file as an instance of
    TyphoonList. The loaded data is assumed to have, at least,
    one field corresponding to the images (X) and another to the
    corresponding best track metadata (Y). Additionally, it may have ids.

    :param path_to_file: Path to the HDF file to load.
    :type path_to_file: str
    :param path_images: Path to the original image folder (i.e. folder
        containing image H5 files). This path is relevant if the IDs or dates of
        any of the data (images or best data) are to be set. Otherwise ignore.
    :type path_images: str, optional
    :param overwrite_ids: Set to True if the loaded typhoon sequence does
        have IDs already but you want to overwrite them.
    :type overwrite_ids: bool
    :param overwrite_flags:
    :type overwrite_flags:
    :param alignment: Set to True if frames and best data are to be
        aligned.
    :type alignment: bool
    :return: Object containing images and bes track data of a typhoon sequence.
    :rtype: TyphoonList instance

    .. seealso:: :class:`TyphoonList`
    """
    # Read HDF file
    data = read_h5file(path_to_file)

    # Get typhoon sequence name
    if path_images:
        seq_name = folder_2_name(path_images)
    else:
        seq_name = ""

    # Only consider best data referring to existing image frames in the sequence
    # IDs
    if overwrite_ids:
        data['X_ids'] = get_image_ids(path_images)
        data['Y_ids'] = get_best_ids(data['Y'], seq_name)
    else:
        if 'X_ids' not in data and path_images:
            data['X_ids'] = get_image_ids(path_images)
        if 'Y_ids' not in data:
            data['Y_ids'] = get_best_ids(data['Y'], seq_name)

    # FLAGs (Add/Overwrite flag-columns to best data array)
    if data['Y'].shape[1] == 20:
        data['Y'] = np.append(data['Y'], np.zeros((data['Y'].shape[0], 2)),
                              axis=1)
        data['Y'][:, -2] = [best_id in data['X_ids'] for best_id in data[
            'Y_ids']]
    if overwrite_flags and data['Y'].shape[1] == 22:
        data['Y'][:, -2] = [best_id in data['X_ids'] for best_id in data[
            'Y_ids']]
        data['Y'][:, -1] = np.zeros((data['Y'].shape[0], 1))

    if alignment:
        pos = [flag == 1 for flag in data['Y'][:, -2]]
        data['Y'] = data['Y'][pos]
        data['Y_ids'] = list(np.array(data['Y_ids'])[pos])

    # Ensure that all image have associated best data!
    data['X'] = np.array([data['X'][i] for i in range(len(data['X'])) if
                          data['X_ids'][i] in data['Y_ids']])
    data['X_ids'] = [image_id for image_id in data['X_ids'] if image_id in
                     data['Y_ids']]
    # Obtain Sequence name
    name = h5file_2_name(path_to_file)
    return TyphoonList(data, name=name)


#######################################
#  TyphoonSequence RELATED FUNCTIONS  #
#######################################

def _create_TyphoonList(path_images, path_best=None):
    """ Groups the images and best track data from a certain typhoon and
    generates a `TyphoonList` instance. As input it requires an HDF
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
    :rtype: TyphoonList

    .. seealso:: :class:`TyphoonList`
    """
    # Get the images from the HDF file and their corresponding IDs.
    data = {
        'X': read_images(path_images),
        'X_ids': get_image_ids(path_images),
    }
    # Get the best track data from the TSV file and their corresponding IDs.
    if path_best:
        Y = read_tsv(path_best)
        data['Y'] = Y
        data['Y_ids'] = get_best_ids(Y)

    # Get name of the
    name = folder_2_name(path_images)
    return TyphoonList(data, name=name)


def _load_TyphoonList(path_to_file, path_images=None, overwrite_ids=False):
    """ Loads a typhoon sequence stored as an HDF file as an instance of
    TyphoonList. The loaded data is assumed to have, at least,
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
    :rtype: TyphoonList instance

    .. seealso:: :class:`TyphoonList`
    """
    # Read HDF file
    data = read_h5file(path_to_file)
    # Get ids
    if 'X_ids' not in data and path_images:
        data['X_ids'] = get_image_ids(path_images)
    if 'Y_ids' not in data:
        data['Y_ids'] = get_best_ids(data['Y'])
    if overwrite_ids:
        data['X_ids'] = get_image_ids(path_images)
        data['Y_ids'] = get_best_ids(data['Y'])
    else:
        data['X_ids'] = sorted(data['X_ids'])

    name = h5file_2_name(path_to_file)
    return TyphoonList(data, name=name)


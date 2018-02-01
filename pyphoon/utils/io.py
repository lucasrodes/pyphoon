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

from os import listdir
from os.path import isfile, join, isdir

import h5py
import numpy as np
from pyphoon.utils.utils import get_ids_best, get_ids_images, h5file_2_name, \
    folder_2_name
from pyphoon.preprocessing.preprocessing import resize_image, interpolate
from datetime import datetime as dt
from pyphoon.utils.utils import DisplaySequence


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

        >>> from pyphoon.utils.io import read_h5file, TyphoonSequence
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

    .. seealso:: :class:`~pyphoon.utils.utils.DisplaySequence`

    """
    def __init__(self, data, name):
        self.data = data
        self.name = name

    def save_as_h5(self, path_to_file):
        """ Stores the data as an HDF file.

        :param path_to_file: Path to the directory where typhoon sequence data
            will be stored.
        :type path_to_file: str
        """
        write_h5file(self.data, path_to_file)

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


##########################
#  H5 RELATED FUNCTIONS  #
##########################

def get_h5_filenames(directory):
    """ Obtains the list of H5 file names within the given directory. If the
    specified directory is a H5 file itself, then the name of the file is
    returned.

    :param directory: Path to an H5 file or a folder with a set of H5 files.
    :type directory: str
    :return: List with the paths to all H5 files available according to the
        specified directory. List is empty if no file was found).
    :rtype: list
    """
    if isdir(directory):
        files = [f for f in listdir(directory) if
                 f.endswith('.h5') and isfile(join(directory, f))]
        files = sorted(files)
    elif directory.endswith('.h5'):
        directory = directory.split('/')[-1]
        files = [directory]
    else:
        files = []
    return files


def read_h5file(path_to_file):
    """ Reads an HDF file and returns its content in a dictionary-fashion.

    :param path_to_file: Path to an H5 file.
    :type path_to_file: str
    :return: Content of the H5 file as a dictionary. Keys stand for data
        field names, values are the corresponding data.
    :rtype: dict
    """
    f = h5py.File(path_to_file, 'r')
    # List all groups
    keys = list(f.keys())
    # Get the data
    data = {key: list(f[key]) for key in keys if key != "name"}
    # Get file name
    # name = path_to_file.split('/')[-1].split('.h5')[-2]
    # data['name'] = name
    return data


def write_h5file(data, path_to_file):
    """ Constructs and stores an H5 file containing the given data.

    :param data: Dictionary containing the data to be stored. Keys stand for
        data field names, values are the corresponding data.
    :type data: dict
    :param path_to_file: Path where the new H5 file will be created.
    :type path_to_file: str
    """
    h5f = h5py.File(path_to_file, 'w')
    for key, value in data.items():
        h5f.create_dataset(key, data=value)


###########################
#  TSV RELATED FUNCTIONS  #
###########################

def read_tsvs(directory='original_data/jma/'):
    """ Reads all the files from the jma directory and returns a list of *N*
    elements, each being a list of typhoon features.

    :param directory: Path of the JMA metadata
    :return: List with the metadata of the *N* images
    """
    files = listdir(directory)
    metadata = []
    for f in files:
        f = join(directory, f)
        metadata.extend(read_tsv(f))
    return metadata


def read_tsv(path_to_file):
    """ Reads a TSV file from the best track dataset.

    :param path_to_file: Complete path to the TSV file
    :return: *NxD* Numpy array (*N*: #samples, *D*: #features)
    """
    metadata = []
    if isfile(path_to_file):
        ff = open(path_to_file, 'r').readlines()
        for fff in ff:
            _metadata = fff.split('\t')
            _metadata[-1] = _metadata[-1].split('\n')[0]
            __metadata = list(map(float, _metadata))
            # index = [0, 1, 2, 3, 4]
            # for i in index:
            #    __metadata[i] = int(__metadata[i])
            # __metadata[-1] = bool(__metadata[-1])
            metadata.append(__metadata)
    return metadata


def check_constant_distance_in_tsv(path_best="original_data/jma",
                                   time_distance=3600):
    """ Checks that all provided JMA data is correct, i.e. that all samples
    within a typhoon sequence have a constant tome distance between themselves.

    :param path_best: Directory containing TSV files.
    :type path_best: str
    :param time_distance: Distance between frames in seconds.
    :type time_distance: int
    :return: List with the number of samples with distance different than 1h
        with the previous one. Element n:th in the list refers to the n:th
        typhoon sequence.
    """

    assert isinstance(time_distance, int), "time_distance is not aninteger: " \
                                           "%r" % time_distance

    files = listdir(path_best)
    error = []
    for file in files:
        data = np.array(read_tsv(join(path_best, file)))
        _error = 0
        for i in range(len(data)-1):
            d0 = dt(int(data[i][0]), int(data[i][1]), int(data[i][2]),
                    int(data[i][3]))
            d1 = dt(int(data[i+1][0]), int(data[i+1][1]), int(data[i+1][2]),
                    int(data[i+1][3]))
            delta = (d1-d0).total_seconds()
            if delta != time_distance:
                _error += 1
                print("Error at", i, "of", delta, "seconds")
        error.append(_error)
    return error


##############################
#  IMAGES RELATED FUNCTIONS  #
##############################

def read_images(path_to_folder, resize=None):
    """ Reads all image files within a given folder. Note that all images are
    assumed to have the same dimensionality. In addition, an image should have
    been stored as a dataset, with name 'infrared', in an HDF file.

    :param path_to_folder: Complete path to the folder containing HDF image
        files.
    :return: *NxWxH* Numpy array (*N*: #images, *W*: image width, *H*: image
        height)
    """
    files = get_h5_filenames(path_to_folder)
    images = []
    for file in files:
        img = read_image(join(path_to_folder, file))
        if resize:
            img = resize_image(img, basewidth=resize)
        images.append(img)
    return np.array(images)


def read_image(path_to_file):
    """ Reads an image from an HDF file. It assumes that the image was stored
    as a dataset with name 'infrared'.

    :param path_to_file: Path to the HDF file storing the image.
    :type path_to_file: str
    :return: Image
    :rtype: list
    """
    data = read_h5file(path_to_file)
    return data['infrared']

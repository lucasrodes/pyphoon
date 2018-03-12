import h5py
from os import listdir
from os.path import isfile, join, isdir
import numpy as np
import warnings
import collections
import ast


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


def read_h5groupfile(path_to_file):
    """ Reads an H5 file and returns its content in a dictionary-fashion.
    Note that the H5 file is assumed to have a set of groups with two
    datasets ('data' and 'ids'). The groups refer to the different data
    fields used as source data for Digital Typhoon.

    :param path_to_file: Path to an H5 file.
    :type path_to_file: str
    :return: Content of the H5 file as a dictionary. Keys stand for data
        field names, the corresponding value is a dictionary with two fields:
        'data', which contains the data itself and 'ids' which contains the
        ids associated to the samples from 'data'. Hence, the format of the
        returned file is a 2-nested dictionary.
    :rtype: dict
    """
    data = collections.defaultdict(dict)

    with h5py.File(path_to_file, 'r') as hf:
        for key, value in hf.items():
            data[key]['data'] = value.get('data').value
            data[key]['ids'] = ast.literal_eval(value.get('ids').value)

    return dict(data)


def write_h5groupfile(data, path_to_file, compression):
    """ Constructs and stores an H5 file containing the given data.

    :param data: Dictionary containing the data to be stored. Keys stand for
        data field names, the corresponding value is a dictionary with two
        fields: 'data', which contains the data itself and 'ids' which
        contains the ids associated to the samples from 'data'. Hence,
        ``data`` is a 2-nested dictionary.
    :type data: dict
    :param path_to_file: Path where the new H5 file will be created.
    :type path_to_file: str
    :param compression: Use to compress H5 file. Find more details at
            the `h5py documentation`_

    .. _h5py documentation:
            http://docs.h5py.org/en/latest/high/dataset.html
    """
    with h5py.File(path_to_file, 'w') as hf:
        for key, value in data.items():
            g1 = hf.create_group(key)
            g1.create_dataset('data', data=value['data'],
                              compression=compression)
            g1.create_dataset('ids', data=str(value['ids']))


################################################################################
#  IMAGES RELATED FUNCTIONS
################################################################################

def read_source_images(path_to_folder):
    """ Reads all image files within a given folder. Note that all images are
    assumed to have the same dimensionality. In addition, an image should have
    been stored as a dataset, with name 'infrared', in an HDF file.

    :param path_to_folder: Complete path to the folder containing HDF image
        files.
    :type path_to_folder: str
    :return: *NxWxH* Numpy array (*N*: #images, *W*: image width, *H*: image
        height)
    :rtype: list
    """
    files = get_h5_filenames(path_to_folder)
    images = []
    for file in files:
        img = read_source_image(join(path_to_folder, file))
        images.append(img)
    return images


def read_source_image(path_to_file):
    """ Reads an image from an HDF file. It assumes that the image was stored
    as a dataset with name 'infrared'.

    :param path_to_file: Path to the HDF file storing the image.
    :type path_to_file: str
    :return: Image
    :rtype: a
    """
    with h5py.File(path_to_file, 'r') as h5f:
        image = h5f.get('infrared').value
    return image


def write_image(path_to_file, image, compression='gzip'):
    """
    Writes image in the original format
    :param compression: Compression
    :param path_to_file: Path to the HDF file storing the image.
    :param image: Image information
    :return:
    """
    with h5py.File(path_to_file, 'w') as h5f:
        h5f.create_dataset(name='infrared', data=image, compression=compression)


################################################################################
# DEPRECATED
################################################################################
def read_h5file(path_to_file):
    """ Reads an HDF file and returns its content in a dictionary-fashion.

    :param path_to_file: Path to an H5 file.
    :type path_to_file: str
    :return: Content of the H5 file as a dictionary. Keys stand for data
        field names, values are the corresponding data.
    :rtype: dict

    .. seealso:: Deprecated for :func:`read_h5groupfile`

    """
    warnings.warn("deprecated, use read_h5groupfile() instead",
                  DeprecationWarning)
    with h5py.File(path_to_file, 'r') as h5f:
        keys = list(h5f.keys())
        data = {}
        for key in keys:
            if key != "name":
                # Decode list of byte-strings
                value = h5f[key][:]
                if (isinstance(value, np.ndarray)) and isinstance(value[0],
                                                                  bytes):
                    _value = value
                    value = [n.decode("utf-8") for n in _value]
                data[key] = value
    return data


def write_h5file(data, path_to_file, compression):
    """ Constructs and stores an H5 file containing the given data.

    :param data: Dictionary containing the data to be stored. Keys stand for
        data field names, values are the corresponding data.
    :type data: dict
    :param path_to_file: Path where the new H5 file will be created.
    :type path_to_file: str
    :param compression: Use to compress H5 file. Find more details at
            the `h5py documentation`_

    .. seealso:: Deprecated for :func:`write_h5groupfile`

    .. _h5py documentation:
            http://docs.h5py.org/en/latest/high/dataset.html
    """
    warnings.warn("deprecated, use write_h5groupfile() instead",
                  DeprecationWarning)
    with h5py.File(path_to_file, 'w') as h5f:
        for key, value in data.items():
            if isinstance(value, list):
                if not value:
                    continue
                # Encode byte-string lists
                elif isinstance(value[0], str):
                    _value = value
                    value = [n.encode("ascii", "ignore") for n in _value]
            h5f.create_dataset(key, data=value, compression=compression)
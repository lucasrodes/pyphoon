"""
Some tools ot assist in reading source data.
"""

from datetime import datetime as dt
from pyphoon.io.h5 import get_h5_filenames


############################
#        IMAGE             #
############################
def get_image_ids(sequence_folder):
    """ Gets ids of all images within the folder ``sequence_folder``.

    :param sequence_folder: Folder name containing images stored as single H5
        files with the original naming convention.
    :type sequence_folder: str
    :return: List with the ids of all images within the folder
        ``sequence_folder``.
    :rtype: list

    .. seealso:: :func:`imagename2id`
    """
    files = get_h5_filenames(sequence_folder)
    ids = [imagefilename2id(file) for file in files]
    return sorted(ids)


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
    dates = [imagefilename2date(file) for file in files]
    return dates


############################
#         BEST             #
############################

def get_best_ids(best_data, seq_name):
    """ Gets ids for each sample in the best track data. It uses the date
    attribute from ``best_data`` to generate the id.

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


def get_best_dates(best_data):
    """ Gets the dates of samples in a best data array.

    :param best_data: Array containing the data from Best Track.
    :type best_data: numpy.array
    :return: List of datetime.datetime elements.
    :rtype: list
    """
    dates = [dt(int(d[0]), int(d[1]), int(d[2]), int(d[3])) for d in best_data]
    return dates


############################
#        CONVERSORS        #
############################

def id2date(identifier):
    """ Gets the date of the frame at position idx.

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


def id2seqno(identifier):
    """ Gets sequence id number from id.

    :param identifier: 
    :return:
    """
    parts = str.split(identifier, sep='_')
    if (not len(parts) == 2) or not len(identifier) == 17:
        Exception('wrong id format provided')
    return int(parts[0])


def date2id(date, name):
    """ Generates the id of a sample given its date and the id of the typhoon
    sequence it belongs to.

    :param date: Date of the sample
    :type date: datetime.datetime
    :param name: Name of the typhoon sequence, e.g. "199607".
    :type name: str
    :return: Id of the sample corresponding to the given sequence name and date.
    :rtype: str
    """
    return name + "_" + date.strftime("%Y%m%d%H")


def hdffile2name(path_h5file):
    """ Given a path to an HDF file, obtains the file name (without format
    extension).

    :param path_h5file: Path to an HDF file.
    :type path_h5file: str
    :return: Name of file
    :rtype: str
    """
    return path_h5file.split('/')[-1].split('.h5')[0]


def folder2name(path_folder):
    """ Given a path to a folder, obtains the file name.

    :param path_folder: Path to a folder.
    :type path_folder: str
    :return: Name of file
    :rtype: str
    """
    name = path_folder.split('/')[-1]
    if name == '':
        name = path_folder.split('/')[-2]
    return name


def imagefilename2id(filename):
    """ Gets id of an image. The id is constructed using the date of the
    typhoon. Note that typhoons from different sequences might have the
    same ID since they were recorded at the same time. Therefore, the final
    id is constructed using both the date and the typhoon ID together.
    To build the image id, the name of the original HDF file is used,
    which have the following structure: ``YYYYMMDDHH-<typhoon id>-<satellite
    model>.h5``. We can then parse it to the id, namely
    ``<typhoon id>_YYYYMMDDHH``.

    :param filename: Name of the HDF image file.
    :type filename: str
    :return: Image frame id
    :rtype: int
    """
    return filename.split('-')[1] + "_" + filename.split('-')[0]


def imagefilename2date(filename):
    """ Extracts the date from a file with a specific filename. To obtain the
    image date from the filename, the filename must have the following
    structure: ``YYYYMMDDHH-<typhoon id>-<satellitemodel>.h5``.

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
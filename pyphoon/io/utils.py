"""
Some tools ot assist in reading source data.
"""

from datetime import datetime as dt
from pyphoon.io.h5 import get_h5_filenames


############################
#        IMAGE             #
############################
def get_image_ids(sequence_folder):
    """ Gets ids of all image HDF5 files in **sequence_folder**. To do the
    conversion filename to id it makes use of :func:`imagefilename2id`.

    :param sequence_folder: Path to the folder containing images stored as
        single HDF5 files with the original `naming convention`_.
    :type sequence_folder: str
    :return: List with the ids of all images within the folder
        **sequence_folder**.
    :rtype: list

    .. _naming convention:
            http://lcsrg.me/pyphoon/build/html/data.html
    """
    files = get_h5_filenames(sequence_folder)
    ids = [imagefilename2id(file) for file in files]
    return sorted(ids)


def get_image_dates(sequence_folder):
    """ Gets the dates from all image HDF5 files stored in *sequence_folder*.
    To do the conversion filename to id it makes use of
    :func:`imagefilename2date`.

    :param sequence_folder: Path to the folder containing images stored as
        single HDF5 files with the original `naming convention`_.
    :type sequence_folder: str
    :return: List with the dates of all images within the folder
        **sequence_folder**.
    :rtype: list

    .. _naming convention:
            http://lcsrg.me/pyphoon/build/html/data.html
    """
    files = get_h5_filenames(sequence_folder)
    dates = [imagefilename2date(file) for file in files]
    return dates


############################
#         BEST             #
############################

def get_best_ids(best_data, seq_no):
    """ Gets ids for each sample in the best track data. It obtains the date
    from each sample using :func:`get_best_date` and converts it to a typhoon id
     using the sequence number **seq_no** and method :func:`date2id`.

    :param best_data: Array containing the Best Track data.
    :type best_data: numpy.array
    :param seq_no: Name of the typhoon sequence
    :type seq_no: str
    :return: List with the ids of all samples from input Best Track data.
    :rtype: list
    """
    ids = [
        date2id(get_best_date(d), seq_no) for d in best_data
    ]
    return ids


def get_best_dates(best_data):
    """ Gets the dates for each sample in the best track data. To extract the
    date from the filename it uses :func:`get_best_date`.

    :param best_data: Array containing the data from Best Track.
    :type best_data: numpy.array
    :return: List of datetime.datetime elements.
    :rtype: list


    """
    dates = [get_best_date(d) for d in best_data]
    return dates


def get_best_date(best_data_sample):
    """ Get the date of best data sample **best_data_sample**. To this end,
    it uses the date features of the sample, namely the *year*, *month*,
    *day* and *hour* features.

    :param best_data_sample:
    :return:
    """
    return dt(int(best_data_sample[0]),
              int(best_data_sample[1]),
              int(best_data_sample[2]),
              int(best_data_sample[3])
              )


############################
#        CONVERSORS        #
############################

def id2date(identifier):
    """ Gets the date of a typhoon image frame with id given by
    **identifier**. A typical id is in the format *<seq_no>_<YYYYMMDD>*,
    where *seq_no* denotes the sequence number (e.g. *199801*).

    :param identifier: Identifier of an image or best track frame.
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
    """ Gets sequence number from a typhoon id. E.g, *199802_199980101 ->
    199802*

    :param identifier: Typhoon unique identifier, e.g. *199802_199980101*.
    :type identifier: str
    :return: Sequence number.
    :rtype: str
    """
    parts = str.split(identifier, sep='_')
    if (not len(parts) == 2) or not len(identifier) == 17:
        Exception('wrong id format provided')
    return int(parts[0])


def date2id(date, seq_no):
    """ Generates the id of an image frame sample using its date and the id of
    the typhoon sequence it belongs to.

    :param date: Date of the sample
    :type date: datetime.datetime
    :param seq_no: Typhoon sequence number, e.g. "199607".
    :type seq_no: str
    :return: Id of the sample corresponding to the given sequence name and date.
    :rtype: str
    """
    return seq_no + "_" + date.strftime("%Y%m%d%H")


def hdffile2name(path_h5file):
    """ Given a path to an HDF5 file it obtains the file name (without format
    extension). E.g, *file.h5 -> file*

    :param path_h5file: Path to an HDF file.
    :type path_h5file: str
    :return: Name of file without format extension.
    :rtype: str
    """
    return path_h5file.split('/')[-1].split('.h5')[0]


def folder2name(path_folder):
    """ Given a path to a folder it obtains the name of the folder alone.
    E.g. */path/to/some/folder -> folder*

    :param path_folder: Path to a folder.
    :type path_folder: str
    :return: Name of folder.
    :rtype: str
    """
    name = path_folder.split('/')[-1]
    if name == '':
        name = path_folder.split('/')[-2]
    return name


def imagefilename2id(filename):
    """ Gets the id of an image sample. The id is generated using two main
    components.
    -   The date of the typhoon sample.
    -   Typhoon sequence number.

    Note that typhoons from different sequences might have the same ID since
    they were recorded at the same time. Therefore, the final id is
    constructed using both the date and the typhoon sequence number together.

    To build the image id, the name of the original HDF file is used,
    which have the following structure:

    *YYYYMMDDHH-<typhoon id>-<satellite model>.h5*

    We can then parse it to the id, namely:

    *<typhoon id>_YYYYMMDDHH*.

    :param filename: HDF image filename.
    :type filename: str
    :return: Image frame identifier.
    :rtype: int
    """
    return filename.split('-')[1] + "_" + filename.split('-')[0]


def imagefilename2date(filename):
    """ Extracts the date from a file with a specific filename. To obtain the
    image date from the filename, the filename must have the following
    structure:

    *YYYYMMDDHH-<typhoon id>-<satellitemodel>.h5*.

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
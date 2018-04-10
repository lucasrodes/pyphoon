from os import listdir
from os.path import isfile, join
from datetime import datetime as dt
import numpy as np


###########################
#  TSV RELATED FUNCTIONS  #
###########################

def read_tsvs(path_best):
    """ Reads all the files from the jma directory and returns a list of *N*
    elements, each being a list of typhoon features. To this end, it assumes
    that **path_best** contains all .TSV JMA data files.

    :param path_best: Path to the directory containing the JMA .TSV data files.
    :type path_best: str
    :return: List with all best data from all samples in the .TSV files.
    :rtype: list
    """
    files = listdir(path_best)
    metadata = []
    for f in files:
        f = join(path_best, f)
        metadata.extend(read_tsv(f))
    return metadata


def read_tsv(path_to_file):
    """ Retrieves the data from a .TSV JMA data file.

    :param path_to_file: Complete path to the TSV file
    :type path_to_file: str
    :return: List with JMA data extracted from given .TSV file. The length of
        the list is equal to the number of samples and each element in the
        list is a list with length equal to number of features.
    :rtype: list
    """
    metadata = []
    if isfile(path_to_file):
        ff = open(path_to_file, 'r').readlines()
        for fff in ff:
            _metadata = fff.split('\t')
            _metadata[-1] = _metadata[-1].split('\n')[0]
            __metadata = list(map(float, _metadata))
            metadata.append(__metadata)
    return metadata


def check_constant_distance_in_tsv(path_best, time_distance=3600):
    """ Checks that within a typhoon sequence the time distance between
    consecutive image frames remains constant.

    :param path_best: Directory containing TSV files.
    :type path_best: str
    :param time_distance: Distance between frames in seconds.
    :type time_distance: int
    :return: List providing, per each sequence (tsv file), the number of
        time-gaps greater than **time_distance** without a satellite image.
        Element n:th in the list refers to the n:th typhoon sequence.
    :rtype: list
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
from os import listdir
from os.path import isfile, join
from datetime import datetime as dt


def get_ids_images(sequence_folder):
    """ Gets ids for each image. It uses the date of the data to generate the
    id.
    :param sequence_folder: Array containing the data from Best Track
    :return: List with the ids of all images.
    """
    ids = [int(f.split('-')[0]) for f in listdir(sequence_folder) if isfile(
        join(sequence_folder, f)) and f.endswith('.h5')]
    return sorted(ids)


def get_ids_best(best_data):
    """ Gets ids for each sample in the best track data. It uses the date of
    the data to generate the id.
    :param best_data: Array containing the data from Best Track
    :return: List with the ids of all samples from input Best Track data.
    """
    ids = [int(dt(int(d[0]), int(d[1]), int(d[2]), int(d[3])).strftime(
        "%Y%m%d%H")) for d in best_data]
    return ids


def h5file_2_name(path_h5file):
    return path_h5file.split('/')[-1].split('.h5')[0]


def folder_2_name(path_folder):
    name = path_folder.split('/')[-1]
    if name == '':
        name = path_folder.split('/')[-2]
    return name

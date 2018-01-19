from os import listdir
from os.path import isfile, join, isdir

import h5py
import numpy as np
from pyphoon.utils.utils import get_ids_best, get_ids_images, h5file_2_name, \
    folder_2_name
from pyphoon.preprocessing.preprocessing import resize_image, interpolate
from datetime import datetime as dt
#from pyphoon.utils.vis import DisplaySequence


##########################
#  H5 RELATED FUNCTIONS  #
##########################

def get_h5_filenames(directory):
    """ Obtains the list of H5 filenames within the given directory
    :param directory: Path to an H5 file or a folder with H5 files.
    :return: List with the paths to all H5 files available according to the
    specified directory (List might be empty if no file was found).
    """
    if isdir(directory):
        files = [f for f in listdir(directory) if
                 f.endswith('.h5') and isfile(join(directory, f))]
        files = sorted(files)
    elif directory.endswith('.h5'):
        files = [directory]
    else:
        files = []
    return files


def read_h5file(path_to_file):
    """ Reads an H5 file and obtains its content
    :param path_to_file: Complete path to the H5 file
    :return: Content of the H5 file as a dictionary. Keys stand for data
    fieldnames, values are the data themselves.
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


def write_h5file(path_to_file, data):
    """ Constructs and stores an H5 file containing the given data.
    :param path_to_file: Complete path where the new H5 file is to be stored.
    :param data: Dictionary containing the data to be stored. Keys stand for
    data field names, values are the data themselves.
    """
    h5f = h5py.File(path_to_file, 'w')
    for key, value in data.items():
        h5f.create_dataset(key, data=value)


#######################################
#  TyphoonSequence RELATED FUNCTIONS  #
#######################################

def create_TyphoonSequence(path_images, path_best=None):
    """ Groups the typhoon images from a given sequence with its
    corresponding best track metadata.
    :param path_images: Path to the folder containing all the typhoon images.
    :param path_best: Path to the TSV file containing the metadata for the
    given sequence
    :return: H5DTFile instance
    """
    data = {
        'X': read_images(path_images),
        'X_ids': get_ids_images(path_images),
    }
    if path_best:
        Y = read_tsv(path_best)
        data['Y'] = Y
        data['Y_ids'] = get_ids_best(Y)

    name = folder_2_name(path_images)
    return TyphoonSequence(data, name=name)


def load_TyphoonSequence(path_to_file, path_images=None, overwrite_ids=False):
    """ Loads an H5 DT (Digital Typhoon) file. This file is assumed to have,
    at least, one field corresponding to the images (X) and another to the
    corresponding best track metadata (Y). Additionally, it may have ids.
    :param path_to_file: Path to the H5 file.
    :param path_images: Path to the original image folder.
    :return: H5DTFile instance
    """
    data = read_h5file(path_to_file)
    # Get ids
    if 'X_ids' not in data and path_images:
        data['X_ids'] = get_ids_images(path_images)
    if 'Y_ids' not in data and path_images:
        data['Y_ids'] = get_ids_best(data['Y'])
    if overwrite_ids:
        data['X_ids'] = get_ids_images(path_images)
        data['Y_ids'] = get_ids_best(data['Y'])
    name = h5file_2_name(path_to_file)
    return TyphoonSequence(data, name=name)


class TyphoonSequence(object):
    def __init__(self, data, name):
        self.data = data
        self.name = name

    def align(self):
        return 0

    def save_as_h5(self, path_to_file):
        write_h5file(path_to_file, self.data)

    def get_frame_id(self, frame):
        return self.data['X_ids'][frame]

    def find_corrupted_frames(self):
        mean = np.mean(self.data['X'], axis=1).mean(axis=1)
        maxv = np.max(self.data['X'], axis=1).max(axis=1)
        minv = np.min(self.data['X'], axis=1).min(axis=1)

        mean_th = [235, 292]
        max_th = [277, 324]
        min_th = [165, 235]
        corrupted_frames = []
        corrupted_info = []
        for i in range(len(mean)):
            corrupted_info_ = {}
            added = False
            if mean[i] < mean_th[0] or mean[i] > mean_th[1]:
                corrupted_info_["mean"] = mean[i]
                if not added:
                    corrupted_frames.append(i)
                    added = True
            if maxv[i] < max_th[0] or maxv[i] > max_th[1]:
                corrupted_info_["max"] = maxv[i]
                if not added:
                    corrupted_frames.append(i)
                    added = True
            if minv[i] < min_th[0] or minv[i] > min_th[1]:
                corrupted_info_["min"] = minv[i]
                if not added:
                    corrupted_frames.append(i)
                    added = True

            if bool(corrupted_info_):
                corrupted_info.append(corrupted_info_)

        return corrupted_frames, corrupted_info

    """
    def visualize(self, interval=100, start_frame=0, end_frame=-1):
        DisplaySequence(
            typhoon_sequence=self,
            interval=interval,
            start_frame=start_frame,
            end_frame=end_frame
        ).run()
    """


class new_h5(object):
    """
    Creates a new H5 file from Satellite Image and Best Track data sources.
    """
    def __init__(self, filename, path_images, path_best, ids=True,
                 interpolation=False):
        self.filename = filename
        X, Y = self.get_data(path_images, path_best)
        self.data = {'X': X, 'Y': Y}
        if ids:
            X_ids, Y_ids = self.get_ids(path_images)
            self.data['X_ids'] = X_ids
            self.data['Y_ids'] = Y_ids
            if interpolation:
                self.data['X'] = interpolate(self.data['X'], self.data['X_ids'],
                                             self.data['Y_ids'], mode='linear')

    def get_ids(self, path_images):
        X_ids = get_ids_images(path_images)
        Y_ids = get_ids_best(self.data['Y'])
        return X_ids, Y_ids

    def get_data(self, path_images, path_best):
        # NxWxH Numpy array of images (N: #typhoons, W: image width, H: image
        #  height   )
        X = read_images(path_images)
        # NxD Numpy array of metadata (N: #typhoons, D: #features)
        Y = read_tsv(path_best)
        return X, Y

    def generate(self):
        """ Generates and creates the new H5 file
        :return:
        """
        write_h5file(self.filename, self.data)


class update_h5(object):
    """
    Updates an H5 file. Some update options include image interpolation,
    metadata management etc.
    """
    def __init__(self, filename, ids=True, path_images=None,
                 interpolation=False):
        self.filename = filename
        X, Y = self.get_data()
        self.data = {'X': X, 'Y': Y}
        if ids and path_images:
            X_ids, Y_ids = self.get_ids(path_images)
            self.data['X_ids'] = sorted(X_ids)
            self.data['Y_ids'] = Y_ids
        if interpolation:
            match = (np.array(sorted(self.data['X_ids'])) == np.array(
                self.data['Y_ids'])).sum()

            self.data['X'] = interpolate(self.data['X'], self.data['X_ids'],
                                         self.data['Y_ids'], mode='linear')

    def get_data(self):
        data = read_h5file(self.filename)
        X = data['X']
        Y = data['Y']
        return X, Y

    def get_ids(self, path_images):
        filename_ = self.filename.split('/')[-1].split('.h5')[0]
        X_ids = get_ids_images(join(path_images, filename_))
        Y_ids = get_ids_best(self.data['Y'])
        return X_ids, Y_ids

    def generate(self):
        """ Generates and creates the new H5 file
        """
        write_h5file(self.filename, self.data)


###########################
#  TSV RELATED FUNCTIONS  #
###########################

def read_tsvs(directory='original_data/jma/'):
    """
    Reads all the files from the jma directory and returns a list of N
    elements, each being a list of typhoon features.
    :param directory: Path of the JMA metadata
    :return: List with the metadata of the N images
    """
    files = listdir(directory)
    metadata = []
    for f in files:
        f = join(directory, f)
        metadata.extend(read_tsv(f))
    return metadata


def read_tsv(path_to_file):
    """ Reads a TSV file from the best track dataset
    :param path_to_file: Complete path to the TSV file
    :return: NxD Numpy array (N: #samples, D: #features)
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
    #return np.array(metadata)
    return metadata


def check_1hdistance_in_tsv(path_best="original_data/jma"):
    """ Checks that all provided JMA data is correct, i.e. that all samples
    within a typhoon sequence have a distance of 1h between themselves.
    :return: List with the number of samples with distance different than 1h
    with the previous one. Element n:th in the list refers to the n:th typhoon
    sequence.
    """
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
            delta = (d1-d0).seconds
            if delta != 3600:
                _error += 1
                print("Error at", i, "of", delta, "seconds")
        error.append(_error)
    return error


##############################
#  IMAGES RELATED FUNCTIONS  #
##############################

def read_images(path_to_folder, resize=None):
    """ Reads all image files within a given folder
    :param path_to_folder: Complete path to the folder containing H5 image
    files.
    :return: NxWxH Numpy array (N: #images, W: image width, H: image height)
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
    data = read_h5file(path_to_file)
    return data['infrared']

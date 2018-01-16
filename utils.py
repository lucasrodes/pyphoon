import numpy as np
from os.path import isfile, join, isdir
from os import listdir
import h5py
from skimage import transform
import pandas as pd


def get_h5_filenames(directory):
    """ Obtains the list of image filenames to be plotted
    :param directory: Path to the image or folder with images.
    :return: List with paths to images to be displayed (List might be empty if no file was found).
    """
    if isdir(directory):
        files = [join(directory, f) for f in listdir(directory) if
                 f.endswith('.h5') and isfile(join(directory, f))]
        files = sorted(files)
    elif directory.endswith('h5'):
        files = [directory]
    else:
        files = []
    return files


def read_h5file(filename):
    """ Reads an H5 file to get the sampels and labels
    :param filename: name of the H5 file
    :return: Samples and labels, as matrix and list, respectively
    """
    f = h5py.File(filename, 'r')
    # Get the data
    X = list(f['X'])
    Y = list(f['Y'])
    # Convert to numpy array
    return X, Y


def read_tsvs(directory='original_data/jma/'):
    """
    Reads all the files from the jma directory and returns a list of N elements, each being a list of typhoon features
    :param directory: Path of the JMA metadata
    :return: List with the metadata of the N images
    """
    files = listdir(directory)
    metadata = []
    for f in files:
        f = join(directory, f)
        metadata.extend(read_tsv(f))
    return metadata


def read_tsv(filename):
    """ Reads a tsv file
    :param filename:
    :return:
    """
    metadata = []
    if isfile(filename):
        ff = open(filename, 'r').readlines()
        for fff in ff:
            _metadata = fff.split('\t')
            _metadata[-1] = _metadata[-1].split('\n')[0]
            __metadata = list(map(float, _metadata))
            index = [0, 1, 2, 3, 4]
            for i in index:
                __metadata[i] = int(__metadata[i])
            __metadata[-1] = bool(__metadata[-1])
            metadata.append(__metadata)
    return metadata


def read_images(directory, resize=None):
    """ Reads all image files within a certain folder
    :param directory:
    :return:
    """
    files = get_h5_filenames(directory)
    images = []
    for file in files:
        img = read_image(file)
        if resize:
            img = resize_image(img, basewidth=resize)
        images.append(img)
    return images


def read_image(filename):
    """ Gets image as an array
    :param filename: Image name (full path)
    :return: Numpy array with image data
    """
    f = h5py.File(filename, 'r')
    # List all groups
    a_group_key = list(f.keys())[0]
    # Get the data
    data = list(f[a_group_key])
    # Convert to numpy array
    data = np.array(data)
    return data


def resize_image(image, basewidth):
    return transform.resize(image, (basewidth, basewidth), order=0)


def _split(files, ratio):
    indices = np.random.choice(len(files), size=round(ratio * len(files)), replace=False)
    count = 0
    files_1 = []
    files_2 = []
    for file in files:
        if count in indices:
            files_1.append(file)
        else:
            files_2.append(file)
        count += 1
    return files_1, files_2


def split(ratio_test, ratio_val, directory="original_data/image/"):
    files = [f for f in listdir(directory) if isdir(join(directory, f))]

    # Randomly select some files for training, validation and test
    np.random.seed(0)
    _files_train, files_test = _split(files, ratio=ratio_test)
    files_train, files_valid = _split(_files_train, ratio=ratio_val)

    return files_train, files_valid, files_test


##################
##################
##################


def get_normalized_data(path=None):
    """ Obtain training data (centered and normalized)
    :return:
        X:  Training samples
        Y:  Training labels
    """
    if path is None:
        path = "train.csv"

    print("Reading in and transforming data...")

    if not os.path.exists(path):
        print('Looking for train.csv')
        print('You have not downloaded the data and/or not placed the files in the correct location.')
        print('Please get the data from: https://www.kaggle.com/c/digit-recognizer')
        print('Place train.csv in the folder large_files adjacent to the class folder')
        exit()

    # Load training data and shuffle
    df = pd.read_csv(path)
    data = df.as_matrix().astype(np.float32)
    np.random.shuffle(data)

    # Get (normalized) samples and corresponding labels
    X = data[:, 1:]
    mu = X.mean(axis=0)
    std = X.std(axis=0)
    np.place(std, std == 0, 1)
    X = (X - mu) / std  # normalize the data
    Y = data[:, 0]

    return X, Y
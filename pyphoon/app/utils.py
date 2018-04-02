from pyphoon.io.h5 import read_h5_dataset_file
import numpy as np
import h5py
from os.path import join


################################################################################
# H5 CHUNKs (for training)
################################################################################
# TODO: Only return two elements - (i) images, (ii) best
# NOTE: Only works with tcxtc chunks, need to create new one for generic data.
def read_h5datachunk_old(path_to_file, shuffle=False):
    """ Reads a chunk of data stored as h5.

    :param path_to_file: Path name to the H5 file to read
    :type path_to_file: str
    :param shuffle: Set to true if data should be shuffled.
    :type shuffle: bool
    :return: Array of images (X), array of labels (Y)
    :rtype: list
    """
    # Read H5 file
    file = read_h5_dataset_file(path_to_file)
    # Load input (X) and output (Y)
    X = file['X']
    Y = file['Y']
    # Load ids corresponding to data samples
    ids = file['ids']
    # Load other parameters if available
    if 'others' in file:
        others = file['others']
    else:
        others = None

    # Shuffle data
    if shuffle:
        pos = np.arange(X.shape[0])
        np.random.shuffle(pos)
        X = X[pos]
        Y = Y[pos]
        ids = list(np.array(ids)[pos])
        if others is not None:
            others = list(np.array(others)[pos])
        else:
            others = None
    return X, Y, ids, others


def load_h5datachunks(dataset_dir, chunk_filenames, features,
                      ignore_classes=None, display=False):
    """ Loads a set of h5 files as individual arrays in a list.

    :param dataset_dir: Directory containing the chunk files.
    :type dataset_dir: str
    :param chunk_filenames: Filenames of the data chunks.
    :type chunk_filenames: list
    :param features: Features to retrieve from the h5 data chunks as string
        names.
    :type features: list
    :param ignore_classes: List of class labels to consider. Labels as ints.
        By default it considers all classes.
    :type ignore_classes: list, default None
    :param display: Set to True to have some informative messages printed out.
    :type display: bool, default False
    :return: List with the data chunks as numpy.arrays.
    :rtype: list
    """
    #  Exceptions
    if features is None:
        with h5py.File(join(dataset_dir, chunk_filenames[0]), 'r') as f:
            available_features = list(f.keys())
        raise Exception("Please specify which features you want to load from "
                        "the h5 chunk file. Available features are:",
                        str(available_features))

    # Data
    data = {}
    for chunk_filename in chunk_filenames:
        with h5py.File(join(dataset_dir, chunk_filename), 'r') as f:
            # Get available features
            available_features = list(f.keys())

            # Load class labels
            try:
                Y_chunk = f.get('class').value
            except:
                raise Exception("Weird file. Could not find field with key "
                                "class. Make sure the datachunk " + join(
                                 dataset_dir, chunk_filename) + " has a field "
                                                                "'class'.")

            # Only consider finite class values
            valid_samples = np.isfinite(Y_chunk)

            # Ignore classes
            if ignore_classes is not None:
                for ignore_class in ignore_classes:
                    consider = Y_chunk != ignore_class
                    valid_samples = valid_samples == consider

            # Load data
            for feature in features:
                if feature not in available_features:
                    raise Exception("Could not find field with key " + feature +
                                    "class. Make sure the datachunk " + join(
                                     dataset_dir, chunk_filename) + " has "
                                                                    "this "
                                                                    "field.")
                else:
                    if feature not in data:
                        data[feature] = []

                    if feature == 'class':
                        data[feature].append(Y_chunk[valid_samples])
                    else:
                        data[feature].append(f.get(feature).value[valid_samples])

        print(" file", chunk_filename, "read") if display else 0

    return list(data.values())


################################################################################
# Data generators
################################################################################
# TODO: Extend for unsupervised models, i.e. Y argument optional
def data_generator(X, Y, batch_sz, shuffle=True):
    """ Generates batches of data from samples **X** and labels **Y**.

    :param X: Sample data.
    :type X: numpy.array
    :param Y: Label data.
    :type Y: numpy.array
    :param batch_sz: Batch size.
    :type batch_sz: int
    :param shuffle: Set to True to shuffle the batch data (recommended)
    :type shuffle: bool, default True
    :return:
    """
    while True:

        if shuffle:
            # Shuffle data
            pos = np.arange(X.shape[0])
            np.random.shuffle(pos)
            _X = X[pos]
            _Y = Y[pos]
        else:
            _X = X
            _Y = Y

        # Generate batches
        imax = int(X.shape[0] / batch_sz)
        for i in range(imax):
            # Find list of IDs
            x = _X[i * batch_sz:(i + 1) * batch_sz]
            y = _Y[i * batch_sz:(i + 1) * batch_sz]
            yield x, y


def data_generator_chunklist(X, Y, batch_sz, shuffle=True):
    """ Generates batches of data from samples **X** and labels **Y**.

    :param X: Sample data.
    :type X: list
    :param Y: Label data.
    :type Y: list
    :param batch_sz: Batch size.
    :type batch_sz: int
    :param shuffle: Set to True to shuffle the batch data (recommended)
    :type shuffle: bool, default True
    :return:
    """
    n_chunks = len(X)
    indices = list(range(n_chunks))
    np.random.shuffle(indices)
    while True:
        if shuffle:
            np.random.shuffle(indices)
        for idx in indices:
            _X = X[idx]
            _Y = Y[idx]
            if shuffle:
                # Shuffle data
                pos = np.arange(_X.shape[0])
                np.random.shuffle(pos)
                _X = _X[pos]
                _Y = _Y[pos]
            else:
                pass

            # Generate batches
            imax = int(_X.shape[0] / batch_sz)
            for i in range(imax):
                # Find list of IDs
                x = _X[i * batch_sz:(i + 1) * batch_sz]
                y = _Y[i * batch_sz:(i + 1) * batch_sz]
                yield x, y



"""
# TODO: not implemented
def _data_generator_from_file(file, Y, batch_sz, shuffle=True):
    Generates batches of data from samples **X** and labels **Y**.

    :param X: Sample data.
    :type X: numpy.array
    :param Y: Label data.
    :type Y: numpy.array
    :param batch_sz: Batch size.
    :type batch_sz: int
    :param shuffle: Set to True to shuffle the batch data (recommended)
    :type shuffle: bool, default True
    :return:

    count = 0
    while True:
        # Read

        # Shuffle
        if shuffle:
            # Shuffle data
            pos = np.arange(X.shape[0])
            np.random.shuffle(pos)
            _X = X[pos]
            _Y = Y[pos]
        else:
            _X = X
            _Y = Y

        # Generate batches
        imax = int(X.shape[0] / batch_sz)
        for i in range(imax):
            # Find list of IDs
            x = _X[i * batch_sz:(i + 1) * batch_sz]
            y = _Y[i * batch_sz:(i + 1) * batch_sz]
            yield x, y
"""
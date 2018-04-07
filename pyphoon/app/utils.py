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


def parse_to_tcxtc_task(original_labels):
    """ Maps an array with original labeling (i.e. 2, 3, 4, 5 and 6)
    corresponding to an array of samples to the labeling for a binary
    classifier "Tropical Cyclone" (0) vs "Extratropical Cyclone" (1).
    Furthermore, it carefully chooses the samples to have a balanced category
    distribution, which means two things:
        - The amount of xTC and TC samples is roughly of 50% each.
        - Considering only TC samples, this method tries to have a uniform
        distribution of samples from categories 2, 3, 4 and 5.

    :param original_labels:
    :type original_labels: numpy.array
    :return: Tuple with (1) new labels and (2) corresponding sample indices.
    :rtype: tuple
    """
    pos = []  # Array storing positions to be used
    label = []  # Array storing sample label indices

    # Find positions of class 6 samples
    pos_6 = np.argwhere(original_labels == 6)
    n_6 = len(pos_6)
    pos.append(pos_6)
    label.append(np.ones(n_6, dtype=int))

    # Get number of samples to take from each category (we want balanced
    # distribution)
    _ratio = np.ceil(n_6 / 4)  # Balanced number of samples from each category
    if _ratio == 0:
        _ratio = 1

    # Find positions of non-6 class samples
    for i in range(2, 6):
        available_pos = np.argwhere(original_labels == i)
        n_samples = len(available_pos)
        if n_samples != 0:
            ratio = int(np.minimum(_ratio, n_samples))
            _pos = np.random.choice(n_samples, ratio, replace=False)
            pos.append(available_pos[_pos])
            label.append(np.zeros(ratio, dtype=int))
    pos = np.concatenate(pos)[:, 0]
    label = np.concatenate(label)

    return label, pos


################################################################################
# Data generators
################################################################################
def data_generator_from_chunklist(X, Y, batch_sz, crop=None):
    """ Generates batches of data from samples **X** and labels **Y**.

    :param X: Sample data.
    :type X: list
    :param Y: Label data.'
    :type Y: list
    :param batch_sz: Batch size.
    :type batch_sz: int
    :return: Generator of batches of samples, labels and weights (importance
        of samples).
    :rtype: tuple
    :param crop: Define the cropping shape (number of pixels width and
        height). It crops the input image according to this shape. The crop
        is placed in the centre of the image.
    :type crop: int
    """
    n_chunks = len(X)
    indices = list(range(n_chunks))

    chunk_count = 0
    while True:
        # Randomise chunk order once all chunks have been seen
        if chunk_count % n_chunks == 0:
            np.random.shuffle(indices)

        # Get chunk for batch generation
        idx = indices[chunk_count % n_chunks]
        _X = X[idx]
        _Y = Y[idx]
        # Shuffle batch data
        n_samples = len(_Y)
        pos = np.arange(n_samples)
        np.random.shuffle(pos)
        _X = _X[pos]
        if crop:
            base = int(crop / 2)
            _X = _X[:, base:base + crop, base:base + crop]
        _Y = _Y[pos]
        #  Y = np_utils.to_categorical(_Y - 2, num_classes=4)

        # Generate batches
        imax = int(n_samples / batch_sz)
        for i in range(imax):
            # Find list of IDs
            x = _X[i * batch_sz:(i + 1) * batch_sz]
            y = _Y[i * batch_sz:(i + 1) * batch_sz]
            sample_weights = np.ones(len(y))
            # sample_weights[y < 960] = 2
            # sample_weights[y < 930] = 4
            yield x, y, sample_weights
        chunk_count += 1
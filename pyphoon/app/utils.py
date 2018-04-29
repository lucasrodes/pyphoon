from pyphoon.io.h5 import read_h5_dataset_file
import numpy as np
import h5py
from os.path import join
from keras.utils import np_utils
import warnings


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
                      ignore_classes=None, verbose=False, crop=None):
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
    :param verbose: Set to True to have some informative messages printed out.
    :type verbose: bool, default False
    :param crop: Defines the cropping shape (number of pixels width and
            height). It crops the input image according to this shape. The crop
            is placed in the centre of the image.
    :type crop: int, default None
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
                    elif feature == 'data' and crop:
                        base = int(crop / 2)
                        data[feature].append(
                            f.get(feature).value[valid_samples]
                            [:, base:base + crop, base:base + crop]
                        )
                    else:
                        data[feature].append(f.get(feature).value[valid_samples])

        print(" file", chunk_filename, "read") if verbose else 0

    return list(data.values())


def parse_to_tcxtc_task(original_labels, seed=0):
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
    :param seed: Set seed to compare results
    :type seed: int, default 0
    :return: Tuple with (1) new labels and (2) corresponding sample indices.
    :rtype: tuple
    """
    # Set seed
    np.random.seed(seed)

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


def balance_dataset(Y, categories, seed=0):
    """

    :param Y: Labels of a batch of data.
    :type Y: numpy.array
    :param categories: List with the possible category indices. For TC tasks,
        usually [2,3,4,5]
    :type categories: list
    :param seed: Set seed to compare results
    :type seed: int, default 0
    :return: Positions of samples to preserve.
    :rtype: list
    """

    # Set seed
    np.random.seed(seed)

    # Find category with less appearances
    categories.append(categories[-1]+1)
    cat_hist = np.histogram(Y, categories)[0]
    cat_min = np.argmin(cat_hist) + 2
    cat_min_nsamples = np.min(cat_hist)

    # Collect positions of samples
    pos = []
    for category in categories[:-1]:
        available_pos = np.argwhere(Y == category)
        if category == cat_min:
            pos.extend(available_pos[:, 0])
        else:
            _pos = np.random.choice(len(available_pos), cat_min_nsamples,
                                    replace=False)
            pos.extend(available_pos[_pos][:, 0])

    return pos


################################################################################
# Data generators
################################################################################
class DataGeneratorFromChunklist:
    """ Generates batches of data.

        :param batch_sz: Batch size.
        :type batch_sz: int
        :param preprocess_algorithm: Algorithm to preprocess a batch of data.
        :type preprocess_algorithm: callable
        :param crop: Defines the cropping shape (number of pixels width and
            height). It crops the input image according to this shape. The crop
            is placed in the centre of the image.
        :type crop: int
        :param target_enc: If target values are ints, they can be encoded using
            one hot encoding ('ohe') or cummulative one hot encoding ('cumohe').
        :type target_enc: str
        :param target_offset: Labels are assumed to be consecutive, but allowed
        to start at an arbirtary integer value. For instance, '2', '3' and '4'
        is a valid set of class labels. In the case of Digital Typhoon dataset,
        the lowest label integer is '2', hence use target_offset = 2 (set by
        default).
        :type target_offset: int, default = 2
        :param verbose: Set to True to display information.
        :type verbose: bool
        """

    def __init__(self, batch_sz, preprocess_algorithm=None, crop=None,
                 target_enc=None, num_classes=4, target_offset=2,
                 verbose=False):
        self.batch_sz = batch_sz
        self.crop = crop
        self.target_enc = target_enc
        self.target_offset = target_offset
        self.num_classes = num_classes
        self.verbose = verbose
        self.preprocess_algorithm = preprocess_algorithm

    def _crop(self, X):
        base = int(self.crop / 2)
        return X[:, base:base + self.crop, base:base + self.crop]

    def feed(self, X, Y, shuffle_batches=True, shuffle_samples=True):
        """
        :param X: Sample data.
        :type X: list
        :param Y: Label data.
        :type Y: list
        :param shuffle_batches: Set to true to shuffle the order of the batches.
        :type shuffle_batches: bool
        :param shuffle_samples: Set to true to shuffle the order of the
            samples within the data batches.
        :type shuffle_samples: bool
        :return: Generator of batches of samples, labels and weights (importance
            of samples).
        :rtype: tuple
        """
        # Get number of chunks
        n_chunks = len(X)
        indices = list(range(n_chunks))

        chunk_count = 0
        while True:
            # Randomise chunk order once all chunks have been seen
            print(chunk_count) if self.verbose else 0
            if chunk_count % n_chunks == 0 and shuffle_batches:
                np.random.shuffle(indices)

            # Get chunk for batch generation
            idx = indices[chunk_count % n_chunks]
            _X = X[idx]
            _Y = Y[idx]

            # Preprocess batch if needed
            if self.preprocess_algorithm:
                _X = self.preprocess_algorithm(_X)

            # Shuffle batch data
            n_samples = len(_Y)
            if shuffle_samples:
                pos = np.arange(n_samples)
                np.random.shuffle(pos)
                _X = _X[pos]
                _Y = _Y[pos]

            # Crop image if needed
            if self.crop:
                _X = self._crop(_X)
            # Encode target values
            if self.target_enc:
                _Y = _target_encoder(_Y, self.target_enc,
                                     self.num_classes, self.target_offset)

            # Generate batches
            imax = np.ceil(n_samples / self.batch_sz).astype(int)
            for i in range(imax):
                # Find list of IDs
                if i == imax:
                    x = _X[i * self.batch_sz:]
                    y = _Y[i * self.batch_sz:]

                    print(x)
                    print('************************************************')
                    print(y)
                else:
                    x = _X[i * self.batch_sz:(i + 1) * self.batch_sz]
                    y = _Y[i * self.batch_sz:(i + 1) * self.batch_sz]

                sample_weights = np.ones(len(y))
                # sample_weights[y < 960] = 2
                # sample_weights[y < 930] = 4
                yield x, y, sample_weights

            chunk_count += 1


def _target_encoder(_Y, encoding, num_classes, offset):
    """
    Encodes an array of integers to the appropriate format.

    :param _Y: Array with target values.
    :type _Y: numpy.array
    :param encoding: Encoding format.
    :type encoding: str
    :param num_classes: Number of classes.
    :type num_classes: int
    :param offset: Use this if lowest label is not zero.
    :type offset: int
    :return: Encoded labels.
    :rtype: list
    """
    if encoding == 'ohe':
        return np_utils.to_categorical(_Y - offset, num_classes)
    elif encoding == 'cumohe':
        return _cumohe(_Y - offset, num_classes)
    else:
        raise Exception("Please chose a valid encoder. 'ohe' for one-hot or "
                        "'cumohe' for cummulative one-hot.")


def _cumohe(_Y, num_classes):
    """
    :param _Y: List of labels
    :param num_classes: Number of classes
    :type num_classes: int
    :return: Encoded list of labels using cumohe.
    :rtype: list
    """
    _Y = np.array(_Y, dtype='int')
    new_Y = np.zeros((len(_Y), num_classes))
    for yy, ny in zip(_Y, new_Y):
        ny[:yy+1] = 1
    return new_Y


def data_generator_from_chunklist(X, Y, batch_sz, crop=None, target_enc=None,
                                  num_classes=4, target_offset=2):
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
    :param crop: Defines the cropping shape (number of pixels width and
        height). It crops the input image according to this shape. The crop
        is placed in the centre of the image.
    :type crop: int
    :param target_enc: If target values are ints, they can be encoded using
        one hot encoding ('ohe') or cummulative one hot encoding ('cumohe').
    :type target_enc: str
    :param target_offset: Labels are assumed to be consecutive, but allowed
    to start at an arbirtary integer value. For instance, '2', '3' and '4'
    is a valid set of class labels. In the case of Digital Typhoon dataset,
    the lowest label integer is '2', hence use target_offset = 2 (set by
    default).
    :type target_offset: int, default = 2
    """
    warnings.warn("This method has been depracated. Use class "
                  "DataGeneratorFromChunklist instead", DeprecationWarning)
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
        _Y = _target_encoder(_Y, target_enc, num_classes, target_offset)
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
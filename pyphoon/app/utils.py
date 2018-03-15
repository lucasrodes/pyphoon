from pyphoon.app.preprocess import ImagePreprocessor
from pyphoon.io.h5 import read_h5_dataset_file
import numpy as np
from pyphoon.app.preprocess import DefaultImagePreprocessor


################################################################################
# H5 CHUNKs (for training)
################################################################################
# TODO: Only return two elements - (i) images, (ii) best
def read_h5datachunk(path_to_file, shuffle=False, preprocessor=None):
    """ Reads a chunk of data stored as h5.

    :param path_to_file: Path name to the H5 file to read
    :type path_to_file: str
    :param shuffle: Set to true if data should be shuffled.
    :type shuffle: bool
    :param preprocessor: Preprocessor used to preprocess the data.
    :type preprocessor: :class:`~pyphoon.app.preprocess.ImagePreprocessor` or
        child classes
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
    # Preprocess images
    if isinstance(preprocessor, ImagePreprocessor):
        X = preprocessor.apply(X)

    return X, Y, ids, others


# TODO:
def merge_datachunks():
    pass


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
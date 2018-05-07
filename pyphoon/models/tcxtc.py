from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, \
    Activation
from keras.layers.normalization import BatchNormalization
import h5py
from pyphoon.app.preprocess import MeanImagePreprocessor
import os


def tcxtcNet(weights_path):
    """
    Network model to estimate if an image is a Tropical cyclone or an
    Extratropical cyclone.

    :param weights_path: Path to the HDF5 file containing the weights of
    pre-trained model.
    :type weights_path: str
    :return: Keras model of the network.
    :rtype: keras.models.Model
    """
    # Dropout probability
    p_drop = 0.2

    model = Sequential()
    ############################################################################
    # Convolutional Layers
    ############################################################################
    model.add(Conv2D(filters=8, kernel_size=(3, 3), input_shape=(256, 256, 1),
                     use_bias=False, name='conv2d_1'))
    model.add(Activation('relu', name='activation_1'))
    model.add(BatchNormalization(name="batch_normalization_1"))
    model.add(MaxPooling2D(pool_size=(2, 2), name="max_pooling2d_1"))

    model.add(Conv2D(filters=16, kernel_size=(3, 3), use_bias=False,
                     name="conv2d_2"))
    model.add(Activation('relu', name="activation_2"))
    model.add(BatchNormalization(name="batch_normalization_2"))
    model.add(MaxPooling2D(pool_size=(2, 2), name="max_pooling2d_2"))

    model.add(Conv2D(filters=32, kernel_size=(3, 3), use_bias=False,
                     name="conv2d_3"))
    model.add(Activation('relu', name="activation_3"))
    model.add(BatchNormalization(name="batch_normalization_3"))
    model.add(MaxPooling2D(pool_size=(2, 2), name="max_pooling2d_3"))

    ############################################################################
    # Dense Layers
    ############################################################################
    model.add(Flatten(name="flatten_1"))

    model.add(Dense(100, use_bias=False, name="dense_1"))
    model.add(Activation('relu', name="activation_4"))
    model.add(BatchNormalization(name="batch_normalization_4"))
    model.add(Dropout(p_drop, name="dropout_1"))

    model.add(Dense(50, use_bias=False, name="dense_2"))
    model.add(Activation('relu', name="activation_5"))
    model.add(BatchNormalization(name="batch_normalization_5"))

    ############################################################################
    # Output Layer
    ############################################################################
    model.add(Dense(units=1, activation='sigmoid', name="dense_3"))

    if weights_path is not None:
        model.load_weights(weights_path)

    return model


class tcxtcPreprocessor(MeanImagePreprocessor):
    """
        Preprocessor for tcxtcNet.

        :param path_to_params: Path to the hdf5 file containing preprocessing
            parameters. By default it uses the one the library provides.
        :type path_to_params: str
        :param add_axis: Adds axis to arrays. See
        :class:`~pyphoon.app.preprocess.ImagePreprocessor`
        :type add_axis: list of int
        """
    def __init__(self, path_to_params=None, add_axis=None, resize_factor=None):
        if not path_to_params:
            this_dir, this_filename = os.path.split(__file__)
            path_to_params = os.path.join(this_dir, "preprocessing_params",
                                          "tcxtc_year.h5")

        # Load pre-processing parameters
        with h5py.File(path_to_params) as f:
            mean = f.get('image_mean').value
            scale_factor = f.get('max_value').value - f.get('min_value').value

        if add_axis:
            super().__init__(mean, scale_factor, add_axis=add_axis,
                             resize_factor=resize_factor)
        else:
            super().__init__(mean, scale_factor, add_axis=[3],
                             resize_factor=resize_factor)

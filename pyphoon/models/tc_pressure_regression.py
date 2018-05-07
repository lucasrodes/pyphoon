from keras.models import Model
from keras.layers import Input, Dense, Conv2D, MaxPooling2D, Flatten, \
    Activation, Dropout
from keras.layers.normalization import BatchNormalization
from keras.regularizers import l2

from pyphoon.app.preprocess import MeanImagePreprocessor
import h5py
import os


def tcRegNet(weights_path, input_img=None):
    """
    Network model to estimate the centre pressure of a typhoon given its
    satellite image (regression task).

    :param weights_path: Path to the HDF5 file containing the weights of
    pre-trained model.
    :type weights_path: str
    :param input_img: Network input keras layer.
    :type input_img: keras.layers.Input
    :return: Keras model of the network.
    :rtype: keras.models.Model
    """
    if input_img is None:
        input_img = Input(shape=(128, 128, 1), name="in")

    # Conv layers
    x = Conv2D(64, (3, 3), strides=(1, 1), padding='same', name='conv2d_1',
               kernel_regularizer=l2(0.01), use_bias=False)(
        input_img)
    x = Activation('relu', name='activation_1')(x)
    x = BatchNormalization(name="batch_normalisation_1")(x)
    x = MaxPooling2D((2, 2), strides=(2, 2), padding='same',
                     name='max_pooling2d_1')(x)

    x = Conv2D(128, (3, 3), strides=(1, 1), padding='same', name='conv2d_2',
               kernel_regularizer=l2(0.1), use_bias=False)(x)
    x = Activation('relu', name='activation_2')(x)
    x = BatchNormalization(name="batch_normalisation_2")(x)
    x = MaxPooling2D((2, 2), strides=(2, 2), padding='same',
                     name='max_pooling2d_2')(x)

    x = Conv2D(128, (3, 3), strides=(1, 1), padding='same', name='conv2d_3',
               kernel_regularizer=l2(0.01), use_bias=False)(x)
    x = Activation('relu', name='activation_3')(x)
    x = BatchNormalization(name="batch_normalisation_3")(x)
    x = MaxPooling2D((2, 2), strides=(2, 2), padding='same',
                     name='max_pooling2d_3')(x)

    x = Conv2D(256, (3, 3), strides=(1, 1), padding='same', name='conv2d_4',
               kernel_regularizer=l2(0.01), use_bias=False)(x)
    x = Activation('relu', name='activation_4')(x)
    x = BatchNormalization(name="batch_normalisation_4")(x)
    x = MaxPooling2D((2, 2), strides=(2, 2), padding='same',
                     name='max_pooling2d_4')(x)

    x = Conv2D(256, (3, 3), strides=(1, 1), padding='same', name='conv2d_5',
               kernel_regularizer=l2(0.01), use_bias=False)(x)
    x = Activation('relu', name='activation_5')(x)
    x = BatchNormalization(name="batch_normalisation_5")(x)
    x = MaxPooling2D((2, 2), strides=(2, 2), padding='same',
                     name='max_pooling2d_5')(x)

    # Dense layers
    x = Flatten()(x)

    x = Dense(1024, use_bias=False, name="dense_1")(x)
    x = Activation('relu', name="activation_6")(x)
    x = BatchNormalization(name="batch_normalisation_6")(x)
    x = Dropout(0.2, name="dropout_1")(x)

    x = Dense(256, use_bias=False, name="dense_2")(x)
    x = Activation('relu', name="activation_7")(x)
    x = BatchNormalization(name="batch_normalisation_7")(x)

    # Out
    x = Dense(1, use_bias=True, name="dense_3")(x)
    # x = Activation('tanh', name="out")(x)

    # Model
    model = Model(input_img, x)

    if weights_path is not None:
        model.load_weights(weights_path)

    return model


class tcRegPreprocessor(MeanImagePreprocessor):
    """
        Preprocessor for tcRegNet.

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
            path_to_params = os.path.join(this_dir,
                                          "preprocessing_params",
                                          "tc_centre_pressure_year.h5")

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
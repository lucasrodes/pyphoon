from keras.models import Model
from keras.layers import Input, Dense, Conv2D, MaxPooling2D, Flatten, \
    Activation, Dropout
from keras.layers.normalization import BatchNormalization

from pyphoon.app.preprocess import MeanImagePreprocessor
import h5py
import os


def tcNet(weights_path, input_img=None):
    """
    Network model to estimate the intensity of a typhoon given its
    satellite image.

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

    ############################################################################
    # Convolutional Layers
    ############################################################################
    x = Conv2D(64, (3, 3), strides=(1, 1), padding='same', name='conv2d_1')(
        input_img)
    x = Activation('relu', name='activation_1')(x)
    x = BatchNormalization(name="batch_normalization_1")(x)
    x = MaxPooling2D((2, 2), strides=(2, 2), padding='same',
                     name='max_pooling2d_1')(x)

    x = Conv2D(128, (3, 3), strides=(1, 1), padding='same', name='conv2d_2')(x)
    x = Activation('relu', name='activation_2')(x)
    x = BatchNormalization(name="batch_normalization_2")(x)
    x = MaxPooling2D((2, 2), strides=(2, 2), padding='same',
                     name='max_pooling2d_2')(x)

    x = Conv2D(128, (3, 3), strides=(1, 1), padding='same', name='conv2d_3')(x)
    x = Activation('relu', name='activation_3')(x)
    x = BatchNormalization(name="batch_normalization_3")(x)
    x = MaxPooling2D((2, 2), strides=(2, 2), padding='same',
                     name='max_pooling2d_3')(x)

    x = Conv2D(256, (3, 3), strides=(1, 1), padding='same', name='conv2d_4')(x)
    x = Activation('relu', name='activation_4')(x)
    x = BatchNormalization(name="batch_normalization_4")(x)
    x = MaxPooling2D((2, 2), strides=(2, 2), padding='same',
                     name='max_pooling2d_4')(x)
    ############################################################################
    # Dense Layers
    ############################################################################
    x = Flatten()(x)

    x = Dense(512, use_bias=True, name="dense_1")(x)
    x = Activation('relu', name="activation_5")(x)
    x = BatchNormalization(name="batch_normalization_5")(x)
    x = Dropout(0.2, name="dropout_1")(x)

    x = Dense(256, use_bias=True, name="dense_2")(x)
    x = Activation('relu', name="activation_6")(x)
    x = BatchNormalization(name="fc_bn2")(x)

    ############################################################################
    # Output
    ############################################################################
    x = Dense(4, use_bias=True, name="dense_3")(x)
    x = Activation('softmax', name="out")(x)

    ############################################################################
    # Model
    ############################################################################
    model = Model(input_img, x)

    if weights_path is not None:
        model.load_weights(weights_path)

    return model


class tcPreprocessor(MeanImagePreprocessor):
    """
        Preprocessor for tcNet.

        :param path_to_params: Path to the hdf5 file containing preprocessing
            parameters. By default it uses the one the library provides.
        :type path_to_params: str
        :param add_axis: Adds axis to arrays. See
        :class:`~pyphoon.app.preprocess.ImagePreprocessor`
        :type add_axis: list of int
        :param random: Set to True to use weights trained on random dataset
            split. See repo for more details.
        :type random: bool
        """
    def __init__(self, path_to_params=None, add_axis=None, resize_factor=None,
                 random=False):
        if not path_to_params:
            this_dir, this_filename = os.path.split(__file__)
            if random:
                path_to_params = os.path.join(this_dir,
                                              "preprocessing_params",
                                              "tc_multiclass_random.h5")
            else:
                path_to_params = os.path.join(this_dir,
                                              "preprocessing_params",
                                              "tc_multiclass_year.h5")

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
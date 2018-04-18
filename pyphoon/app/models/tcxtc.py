from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, \
    Activation
from keras.layers.normalization import BatchNormalization


def tcxtcNet(weights_path):
    """
    Network model to estimate if an image is a Tropical cyclone or an
    Extratropical cyclone.

    :param weights_path: Path to the HDF5 file containing the weights.
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

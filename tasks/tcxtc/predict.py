# Import keras libraries
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, \
    Activation
from keras.layers.normalization import BatchNormalization
import argparse
import numpy as np


def get_model():
    p_drop = 0.2

    model = Sequential()
    ############################################################################
    # Convolutional Layers
    ############################################################################
    model.add(Conv2D(filters=8, kernel_size=(3, 3), input_shape=(256, 256, 1),
                     use_bias=False))
    model.add(Activation('relu'))
    model.add(BatchNormalization())
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(filters=16, kernel_size=(3, 3), use_bias=False))
    model.add(Activation('relu'))
    model.add(BatchNormalization())
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(filters=32, kernel_size=(3, 3), use_bias=False))
    model.add(Activation('relu'))
    model.add(BatchNormalization())
    model.add(MaxPooling2D(pool_size=(2, 2)))
    ############################################################################
    # Dense Layers
    ############################################################################
    model.add(Flatten())

    model.add(Dense(100, use_bias=False))
    model.add(Activation('relu'))
    model.add(BatchNormalization())
    model.add(Dropout(p_drop))

    model.add(Dense(50, use_bias=False))
    model.add(Activation('relu'))
    model.add(BatchNormalization())

    ############################################################################
    # Output Layer
    ############################################################################
    model.add(Dense(units=1, activation='sigmoid'))

    return model


def get_parser_arguments():
    parser = argparse.ArgumentParser()
    # Positional arguments
    parser.add_argument(
        "weights",
        help="Path to the HDF5 file with pre-trained model weights.",
        type=str
    )
    parser.add_argument(
        "input",
        help="Image file in .npy format",
        type=str
    )

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    # Load input arguments
    args = get_parser_arguments()
    weights = args.weights
    X = args.input

    # Check X has good shape
    exception_msg = "Wrong image shape. Accepted shapes are: (256, 256), " \
                    "(256, 256, 1) or (1, 256, 256, 1) for single images and" \
                    "(N, 256, 256) or (N, 256, 256, 1) for image batches."
    if X.ndim == 2:
        if X.shape[0] == 256 and X.shape[1] == 256:
            X = np.expand_dims(np.expand_dims(X, axis=0), axis=3)
        else:
            raise Exception(exception_msg)
    elif X.ndim == 3:
        if X.shape[0] == 256 and X.shape[1] == 256 and X.shape[2] == 1:
            X = np.expand_dims(X, axis=0)
        elif X.shape[1] == 256 and X.shape[2] == 256:
            X = np.expand_dims(X, axis=3)
        else:
            raise Exception(exception_msg)
    elif X.ndim == 4:
        if X.shape[1] == 256 and X.shape[2] == 256 and X.shape[3] == 1:
            pass
        else:
            raise Exception(exception_msg)
    else:
        raise Exception(exception_msg)

    # Load model
    model = get_model()
    model.load_weights(weights)

    # Normalise
    X = (X - 0) / 1

    # Predict
    y = model.predict(X)
    print(y)
import sys
sys.path.insert(0, '../..')


def get_model():
    from keras.models import Sequential
    from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, \
        Activation
    from keras.layers.normalization import BatchNormalization

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

    return model


def get_parser_arguments():
    parser = argparse.ArgumentParser(description="Performs prediction on a "
                                                 "set of images. Predicted "
                                                 "labels are 0 for 'Tropical "
                                                 "cyclone' and 1 for "
                                                 "'Extratropical cyclone'.")
    # Positional arguments
    parser.add_argument(
        "weights",
        help="Path to the HDF5 file with pre-trained model weights.",
        type=str
    )
    parser.add_argument(
        "input",
        help="Image file in .npy format.",
        type=str
    )

    parser.add_argument(
        "-b",
        "--batch_size",
        help="Size of batch when doing the prediction. If "
             "you are using GPU, make sure the batch of images fits in "
             "memory. Also, to make the prediction faster, you might want to "
             " this value. Default is 16.",
        type=int
    )

    parser.add_argument(
        "-p",
        "--probabilities",
        help="Use this option to print probabilities of images belonging to "
             "an Extratropical cyclone instead of class labels.",
        action='store_true'
    )

    parser.add_argument(
        "-v",
        "--verbose",
        help="Add verbosity.",
        action='store_true'
    )

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    import os
    import warnings
    warnings.filterwarnings("ignore")
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

    # Load input arguments
    import argparse
    args = get_parser_arguments()
    weights = args.weights
    filepath = args.input
    probabilities = args.probabilities
    if args.batch_size:
        batch_size = args.batch_size
    else:
        batch_size = 16
    verbose = args.verbose

    # Load image
    import numpy as np
    X = np.load(filepath)

    # Load preprocessing params
    from pyphoon.app.preprocess import MeanImagePreprocessor
    import h5py

    with h5py.File('preprocessing_year.h5') as f:
        mean = f.get('image_mean').value
        scale_factor = f.get('max_value').value - f.get('min_value').value

    # Check X has good shape
    exception_msg = "Input shape was "+str(X.shape)+". Accepted shapes are (" \
                                                    "256, 256) for an image " \
                                                    "or (N, 256, 256) for a " \
                                                    "batch of images."
    if X.ndim == 2:
        if X.shape[0] == 256 and X.shape[1] == 256:
            axis = [0, 3]
        else:
            raise Exception(exception_msg)
    elif X.ndim == 3:
        if X.shape[1] == 256 and X.shape[2] == 256:
            axis = [3]
        else:
            raise Exception(exception_msg)
    else:
        raise Exception(exception_msg)

    # Preprocess
    preprocessor = MeanImagePreprocessor(mean, scale_factor, add_axis=axis,
                                         resize_factor=(256, 256))
    X = preprocessor.apply(X)
    from os import environ
    environ["CUDA_VISIBLE_DEVICES"] = "1"
    # Load model
    model = get_model()
    print('> Loading weights...') if verbose else 0
    model.load_weights(weights)

    # Predict
    print('> Predicting...') if verbose else 0
    y = model.predict(X, batch_size=batch_size)[:, 0]

    # Print results
    print("\n--------------------") if verbose else 0
    print("> Prediction(s):") if verbose else 0
    print("--------------------") if verbose else 0
    if probabilities:
        print(y)
    else:
        print(np.round(y).astype(int))

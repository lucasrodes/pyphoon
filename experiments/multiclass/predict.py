import sys
sys.path.insert(0, '../..')


def get_model():
    from keras.models import Model
    from keras.layers import Input, Conv2D, MaxPooling2D, Flatten, Dense, \
        Dropout, Activation
    from keras.layers.normalization import BatchNormalization

    p_drop = 0.2

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
    # Modelshinjuku to asa
    ############################################################################
    model = Model(input_img, x)

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
        help="Use this option to print the output softmax layer with the "
             "probabilities of input image(s) being each of the four "
             "categories.",
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
    preprocessor = MeanImagePreprocessor(mean, scale_factor, add_axis=axis)
    X = preprocessor.apply(X)

    # Use this to limit GPU usage. Remove if you don't really care
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
        c = np.argmax(y, axis=1) + 2
        print(c)

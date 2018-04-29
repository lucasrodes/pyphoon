import numpy as np
from keras import backend as K
import copy
import cv2

def good_shape_conv_weights(weight):
    """
    By default, when getting the weights from a keras model with method
    layer.get_weights() the shape is hard to work with.

    An example usage is shown below:

        >>> model = ... # load or define model
        >>> w = model.layers[0].get_weights()  # Get weights of first layer
        >>> from pyphoon.app.explore import good_shape_conv_weights
        >>> W = good_shape_conv_weights(w)

    :param weight: Weights of a layer as layer.get_weights() returns it.
    :type weight: list of arrays
    :return: Weights of the kernels as a numpy array with shape (N, W,
        H), where N: # number of kernels, W: width and H: height.
    :rtype: numpy.array
    """
    W = np.swapaxes(weight[0], 1, 2)
    W = np.swapaxes(W, 0, 1)
    return np.swapaxes(W, 0, 3)


# Function to get activation specific layer
def get_activations(model, layer, X, dense=False, expand=None):
    """
    Gets the activations from **layer**. For convolutional layers, it gets
    the activations as a numpy.array of shape (N, W, H) with N: #kernels,
    W: width and H: height. For dense layers, the numpy.array is IxO,
    where I: #input units and O: #output units.

    Reference: https://github.com/keras-team/keras/issues/41

    :param model: Keras model
    :type model: keras.models.Model
    :param layer: Name of the layer
    :type layer: str
    :param X: Input sample to the model
    :type X: numpy.array
    :param dense: Set to True if **layer** is a dense layer.
    :type dense: bool
    :param expand: Set a number to expand the output's width. It
        basically pads the output activation vector for easier visualisation.
    :type expand: int
    :return: Matrix of shape (N, W, H), where N: #Number of feature maps,
        W: width, H: height.
    :rtype: numpy.array
    """
    y = model.get_layer(layer).output

    _get_activations = K.function(
        [model.input, K.learning_phase()],
        [y,]
    )
    activations = _get_activations([X, 0])
    if dense:
        if expand:
            return np.vstack([activations[0]]*expand).T
        else:
            return activations[0].T
    else:
        return np.swapaxes(activations[0], 0, 3)[:, :, :, 0]


def get_patched_images(X, patch_size, stride, patch):
    """
    Given an image of shape (1, W, H, 1), previously preprocessed,
    this function adds a patch of constant value given by **patch** in all
    possible positions using a certain **stride**.

    :param X: Input image of shape (1, W, H, 1).
    :type X: numpy.array
    :param patch_size: Size of the patch. Note that we use squared patches.
    :type patch_size: int
    :param stride: Stride to use when placing the patch. This determines the
        number of possible patch allocations. If using low values (e.g. 1),
        this method might take a while.
    :type stride: int
    :param patch: Value of the patch pixels (all the same).
    :type patch: int
    :return: Array with all variantes of patched images.
    :rtype: numpy.array
    """
    m_max = X.shape[1]-patch_size
    n_max = X.shape[2]-patch_size

    # Add patch to image
    X_patch = []
    for n in range(0, n_max+1, stride):
        for m in range(0, m_max+1, stride):
            X_ = copy.copy(X)
            X_[0, n:n+patch_size, m:m+patch_size, 0] = patch
            X_patch.append(X_)
    X_patch = np.vstack(X_patch)
    return X_patch


def _predictions2image_reshape(predictions, resize_factor):
    sz = int(np.sqrt(len(predictions)))
    attribution_image = predictions.reshape(sz, sz)
    return cv2.resize(attribution_image, resize_factor)


def get_attribution_image(model, X, patch_size, stride, patch):
    """
    Obtains the attribution matrix, which displays, per pixel, the model
    output when the patch is placed at that pixel.

    :param model: Keras model to explore.
    :type model: Keras.models.Model
    :param X: Input image of shape (1, W, H, 1).
    :type X: numpy.array
    :param patch_size: Size of the patch. Note that we use squared patches.
    :type patch_size: int
    :param stride: Stride to use when placing the patch. This determines the
        number of possible patch allocations. If using low values (e.g. 1),
        this method might take a while.
    :type stride: int
    :param patch: Value of the patch pixels (all the same).
    :type patch: int
    :return: Tuple with three variables:
        -   Attribution image
        -   Pixel locations for the patch that provided 30 worst performances.
        -   All patched image variants as a numpy.array.
    :rtype: tuple
    """
    # Get patched images
    X_patch = get_patched_images(X, patch_size=patch_size, stride=stride,
                                 patch=patch)

    #  Do predictions
    predictions = model.predict(X_patch, batch_size=16)[:, 0]
    # Get worst results
    worst_results_loc = predictions.argsort()[:30]
    worst_results_val = predictions[worst_results_loc]

    # Reshape to obtain image
    n = X.shape[1]
    attribution_image = _predictions2image_reshape(predictions, (n, n))

    return attribution_image, worst_results_loc, X_patch
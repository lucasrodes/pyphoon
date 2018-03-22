import numpy as np
from skimage.transform import downscale_local_mean
import cv2


################################################################################
# IMAGE OPERATIONS
################################################################################
def get_mean_image(X):
    """ Computes the mean image from a list of image batches.

    :param X: List containing image batches. That is, an element of the list
        is of shape (N, W, H), where N: #samples, W: image width, H: image
        height.
    :type X: list
    :return: Mean image.
    :rtype: numpy.array
    """
    mean = None
    count = 0
    n_samples = 0
    for x in X:
        print(count)
        count += 1
        if mean is None:
            mean = np.sum(x, axis=0)
        else:
            mean += np.sum(x, axis=0)

        n_samples += len(x)

    mean /= n_samples
    return mean


def get_max_min(X):
    """ Gets the maximum and minimum pixel values of a list of image batches.

    :param X: List containing image batches. That is, an element of the list
        is of shape (N, W, H), where N: #samples, W: image width, H: image
        height.
    :type X: list
    :return: Maximum (first element) and minimum (second element) values.
    :rtype: tuple
    """
    max_value = None
    min_value = None
    for x in X:
        if max_value is None:
            max_value = np.max(x)
        else:
            max_value = np.maximum(max_value, np.max(x))

        if min_value is None:
            min_value = np.min(x)
        else:
            min_value = np.minimum(min_value, np.min(x))

    return max_value, min_value


def resize(X, size):
    """ Resizes the image according to **size**.

    :param X: Image of shape (N, W, H), where N: #samples, W: image width,
        H: image height.
    :type X: numpy.array
    :param size: Size to reshape images.
    :type size: tuple
    :return: List containing image batches with resized images.
    :rtype: numpy.array
    """
    im = np.array([cv2.resize(x, size) for x in X]).astype(np.float32)
    return im  # np.expand_dims(im, axis=3)


################################################################################
# PROCESSORS
################################################################################
class ImagePreprocessor(object):
    """
    Parent class for image preprocessing classes. This class does not
    implement any method, please refer to its child classes.

    :param reshape_mode: Use the mode according to your DL framework.
        Available modes:
            * **keras**: Reshape to have an extra axis for Keras.
    """

    def __init__(self, reshape_mode):
        self.reshape_mode = reshape_mode

    def apply(self, X):
        """ Applies the preprocessing pipeline to **data**.

        :param X: Array with images.
        :type X: numpy array
        """
        pass

    def reshape(self, X):
        """ Reshapes the dimensions of the list so that it is suitable for
        the specified DL framework.

        :param X: List of images.
        :type X: numpy.ndarray
        :return: List of reshaped images
        :rtype: list
        """
        if self.reshape_mode == 'keras':
            return X.reshape(-1, X.shape[1], X.shape[2], 1)


class DefaultImagePreprocessor(ImagePreprocessor):
    """ Class of :class:`~pyphoon.app.preprocess.ImagePreprocessor`,
    implementing an specific preprocessing of images. Assuming an input image
    :math:`X`, this preprocessor first centres and normalises it as

    .. math::  \\frac{X-\mu}{\sigma}

    where :math:`\mu` and :math:`\sigma` denote the pixel mean and standard
    deviation, respectively. Next, it resizes the image using the method
    :func:`skimage.transform.downscale_local_mean`.


    :var resize_factor: To resize the image. For instance, half the
        dimensions by setting this parameter equal to 2.
    :var mean: Used to centre the data.
    :var std: Used to normalise the data.
    :var reshape_mode: Used to normalise the data. See
        :class:`~pyphoon.app.preprocess.ImagePreprocessor`
    """
    def __init__(self, mean, std, resize_factor, reshape_mode):
        super().__init__(reshape_mode)
        self.mean = mean
        self.std = std
        self.resize_factor = resize_factor

    def apply(self, X):
        """ Processes an array of images, scaling and normalising them
        as required and, eventually, reshapes the list to be suitable for a
        specific DL framework.

        :param X: List with image data (images as numpy arrays).
        :type X: numpy.ndarray
        :return: Updated, preprocessed list of images.
        """
        if not isinstance(X, np.ndarray):
            raise TypeError("Expected type for X is numpy.ndarray but got " +
                            X.__class__.__name__)
        if X.ndim != 3:
            raise Exception("X.ndim must be 3 with X.shape = (N, W, H), "
                            "where N: #samples, W: image_width, "
                            "H: # image_height")

        # Scale chunk images
        X = np.array(
            [
                downscale_local_mean(x, (self.resize_factor,
                                         self.resize_factor))
                for x in X
            ]
        )

        X -= self.mean
        X /= self.std

        # Normalise
        X = self.reshape(X)

        return X


class MeanImagePreprocessor(ImagePreprocessor):
    """ Class of :class:`~pyphoon.app.preprocess.ImagePreprocessor`,
    implementing an specific preprocessing of images. Assuming an input image
    :math:`X`, this preprocessor first centres and normalises it as

    .. math::  \\frac{X-\mu}{\sigma}

    where :math:`\mu` and :math:`\sigma` denote the pixel mean and standard
    deviation, respectively. Next, it resizes the image using the method
    :func:`skimage.transform.downscale_local_mean`.


    :var mean_image: Mean image (2D matrix)
    :var scale_factor: Used to normalise the data.
    :var resize: To resize the image. Define the new size of the images.
    :var reshape_mode: Used to normalise the data. See
        :class:`~pyphoon.app.preprocess.ImagePreprocessor`
    """
    def __init__(self, mean_image, scale_factor, resize, reshape_mode):
        super().__init__(reshape_mode)
        self.mean = mean_image
        self.scale = scale_factor
        self.resize = resize

    def apply(self, X):
        """ Processes an array of images, scaling and normalising them
        as required and, eventually, reshapes the list to be suitable for a
        specific DL framework.

        :param X: List with image data (images as numpy arrays).
        :type X: numpy.ndarray
        :return: Updated, preprocessed list of images.
        """
        if not isinstance(X, np.ndarray):
            raise TypeError("Expected type for X is numpy.ndarray but got " +
                            X.__class__.__name__)

        if X.ndim != 3:
            raise Exception("X.ndim must be 3 with X.shape = (N, W, H), "
                            "where N: #samples, W: image_width, "
                            "H: # image_height")

        # Scale chunk images
        X = resize(X, self.resize)
        # Centre & normalise
        X = (X - self.mean)/self.scale

        return X
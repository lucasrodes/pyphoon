import numpy as np
import cv2


################################################################################
# IMAGE OPERATIONS
################################################################################
def get_mean_image(X, display=False):
    """ Computes the mean image from a list of image batches.

    :param X: List containing image batches. That is, an element of the list
        is of shape (N, W, H), where N: #samples, W: image width, H: image
        height. Arrays of size (N, W, H, C) with C: #channels are also accepted.
        If you only have a single batch (e.g. ``B``), you just need to
        encapsulate it in a list (i.e. ``[B]``).
    :type X: list
    :param display: Set to True to display information as function is executed.
    :type display: bool
    :return: Mean image (size W x H).
    :rtype: numpy.array
    """
    mean = None
    count = 0
    n_samples = 0
    for x in X:
        print(count) if display else 0
        count += 1
        if mean is None:
            mean = np.sum(x, axis=0)
        else:
            mean += np.sum(x, axis=0)

        n_samples += len(x)

    mean /= n_samples
    return mean


def get_mean_pixel(X, display=False):
    """ Computes the mean pixel from all samples in the list of image batches
    **X**.

    :param X: List containing image batches. That is, an element of the list
        is of shape (N, W, H), where N: #samples, W: image width, H: image
        height. Arrays of size (N, W, H, C) with C: #channels are also accepted.
        If you only have a single batch (e.g. ``B``), you just need to
        encapsulate it in a list (i.e. ``[B]``).
    :type X: list
    :param display: Set to True to display information as function is executed.
    :type display: bool
    :return: Pixel mean (scalar).
    :rtype: float
    """
    pmean = 0
    n_samples = 0
    count = 0
    for x in X:
        if display:
            print(count)
            count += 1
        pmean += len(x) * x.mean()
        n_samples += len(x)
    pmean /= n_samples
    return pmean


def get_std_pixel(X, pmean, display=False):
    """ Computes the pixel standard deviation from all samples in the list of
    image batches **X**.

    :param X: List containing image batches. That is, an element of the list
        is of shape (N, W, H), where N: #samples, W: image width, H: image
        height. Arrays of size (N, W, H, C) with C: #channels are also accepted.
        If you only have a single batch (e.g. ``B``), you just need to
        encapsulate it in a list (i.e. ``[B]``).
    :type X: list
    :param pmean: Pixel mean of bath list **X** (see :func:`get_mean_pixel`).
    :type pmean: float
    :param display: Set to True to display information as function is executed.
    :type display: bool
    :return: Pixel standard deviation (scalar).
    :rtype: float
    """
    pstd = 0
    n_samples = 0
    count = 0
    for x in X:
        if display:
            print(count)
            count += 1
        pstd += len(x) * (x ** 2).mean()
        n_samples += len(x)
    pstd /= n_samples
    pstd = np.sqrt(pstd - pmean ** 2)
    return pstd


def get_max_min(X, display=False):
    """ Gets the maximum and minimum pixel values of a list of image batches.

    :param X: List containing image batches. That is, an element of the list
        is of shape (N, W, H), where N: #samples, W: image width, H: image
        height. Arrays of size (N, W, H, C) with C: #channels are also accepted.
        If you only have a single batch (e.g. ``B``), you just need to
        encapsulate it in a list (i.e. ``[B]``).
    :type X: list
    :param display: Set to True to display information as function is executed.
    :type display: bool
    :return: Maximum (first element) and minimum (second element) values.
    :rtype: tuple
    """
    max_value = None
    min_value = None
    count = 0
    for x in X:
        print(count) if display else 0
        count += 1
        if max_value is None:
            max_value = np.max(x)
        else:
            max_value = np.maximum(max_value, np.max(x))

        if min_value is None:
            min_value = np.min(x)
        else:
            min_value = np.minimum(min_value, np.min(x))

    return max_value, min_value


def resize(X, size, ignore_last_axis=False):
    """ Resizes the image according to **size** using `cv2.resize`_ with
    bilinear interpolation.

    ..  _cv.resize:
            https://docs.opencv.org/3.4.0/da/d54/group__imgproc__transform.html#ga47a974309e9102f5f08231edc7e7529d

    :param X: Image of shape (N, W, H), where N: #samples, W: image width,
        H: image height.
    :type X: numpy.array
    :param size: Size to reshape images.
    :type size: tuple
    :param ignore_last_axis: Set to True if images have dimensionality
        (W, H, 1).
    :type ignore_last_axis: bool
    :return: List containing image batches with resized images. E.g. (2,2).
    :rtype: numpy.array
    """
    if ignore_last_axis:
        im = np.array([cv2.resize(x[:, :, 0], size) for x in X]).astype(
            np.float32)
    else:
        im = np.array([cv2.resize(x, size) for x in X]).astype(np.float32)
    return im


################################################################################
# PROCESSORS
################################################################################
class ImagePreprocessor(object):
    """ Parent class for image preprocessing classes. This class does not
    implement any method, please refer to its child classes.

    :param reshape_mode: Use the mode according to your DL framework.
        Available modes:

            *   *keras*: Reshape to have an extra axis for Keras.
    """

    def __init__(self, reshape_mode):
        self.reshape_mode = reshape_mode

    def apply(self, X):
        """ Applies the preprocessing pipeline to class attribute **data**.

        :param X: Array with images.
        :type X: numpy array
        """
        pass

    def reshape(self, X):
        """ Reshapes the dimensions of the list so that it is suitable for
        the specified DL framework. So far, only 'keras' option is available.

        :param X: List of images.
        :type X: numpy.ndarray
        :return: List of reshaped images
        :rtype: list
        """
        if not self.reshape_mode:
            return X
        elif self.reshape_mode == 'keras':
            return X.reshape(-1, X.shape[1], X.shape[2], 1)


class DefaultImagePreprocessor(ImagePreprocessor):
    """ Child of of :class:`~pyphoon.app.preprocess.ImagePreprocessor`.
    Assuming an input image :math:`X`, this preprocessor first centres and
    normalises it as

    .. math::  \\frac{X-\mu}{\sigma}

    where :math:`\mu` and :math:`\sigma` denote the pixel mean and standard
    deviation, respectively. Next, it resizes the image using the method
    :func:`resize`.


    :var resize_factor: To resize the image. For instance, half the
        dimensions by setting this parameter equal to 2.
    :var mean: Used to centre the data.
    :var std: Used to normalise the data.
    :var reshape_mode: Used to normalise the data. See
        :class:`~pyphoon.app.preprocess.ImagePreprocessor`
    """
    def __init__(self, mean, std, resize_factor=None, reshape_mode=None):
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
        #if X.ndim != 3:
        #    raise Exception("X.ndim must be 3 with X.shape = (N, W, H), "
        #                    "where N: #samples, W: image_width, "
        #                    "H: # image_height")

        # Resize chunk images
        if self.resize_factor:
            X = cv2.resize(X, self.resize_factor)

        # Normalise
        X = (X - self.mean)/self.std

        X = self.reshape(X)
        return X


class MeanImagePreprocessor(ImagePreprocessor):
    """ Child of :class:`~pyphoon.app.preprocess.ImagePreprocessor`. Assuming an
    input image :math:`X`, this preprocessor first centres and normalises it as

    .. math::  \\frac{X \ominus \hat{X}}{s}

    where :math:`\hat{X}` denotes the image mean (same size as :math: `X`),
    :math:`s` is the scale factor (scalar) and :math:`\ominus` is pixel-wise
    subtraction operations. Next, it resizes the image using the method
    :func:`resize`.

    :var mean_image: Mean image (2D matrix)
    :var scale_factor: Used to normalise the data. By default it does not scale.
    :var resize_factor: To resize the image. Define the new size of the images.
    :var reshape_mode: Used to normalise the data. See
        :class:`~pyphoon.app.preprocess.ImagePreprocessor`
    """
    def __init__(self, mean_image, scale_factor=1,
                 resize_factor=None, reshape_mode=None):
        super().__init__(reshape_mode)
        self.mean = mean_image
        self.scale = scale_factor
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

        # Resize chunk images
        if self.resize_factor:
            X = cv2.resize(X, self.resize_factor)
        # Centre & normalise
        X = (X - self.mean)/self.scale

        return X
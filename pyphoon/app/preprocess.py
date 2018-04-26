import numpy as np
import cv2


################################################################################
# IMAGE OPERATIONS
################################################################################
def get_mean_image(X, verbose=False):
    """ Computes the mean image from a list of image batches.

    :param X: List containing image batches. That is, an element of the list
        is of shape (N, W, H), where N: #samples, W: image width, H: image
        height. Arrays of size (N, W, H, C) with C: #channels are also accepted.
        If you only have a single batch (e.g. ``B``), you just need to
        encapsulate it in a list (i.e. ``[B]``).
    :type X: list
    :param verbose: Set to True to display information as function is executed.
    :type verbose: bool
    :return: Mean image (size W x H).
    :rtype: numpy.array
    """
    mean = None
    count = 0
    n_samples = 0
    for x in X:
        print(count) if verbose else 0
        count += 1
        if mean is None:
            mean = np.sum(x, axis=0)
        else:
            mean += np.sum(x, axis=0)

        n_samples += len(x)

    mean = mean/n_samples
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


def get_std_pixel(X, pmean, verbose=False):
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
    :param verbose: Set to True to display information as function is executed.
    :type verbose: bool
    :return: Pixel standard deviation (scalar).
    :rtype: float
    """
    mu2 = 0
    n_samples = 0
    count = 0
    for x in X:
        if verbose:
            print(count)
            count += 1
        mu2 += len(x) * (x.astype(np.float16) ** 2).mean()
        n_samples += len(x)
    mu2 = mu2/n_samples
    s = mu2 - pmean ** 2
    pstd = np.sqrt(s)
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


def resize(X, resize_factor):
    """ Resizes the image according to **size** using `cv2.resize`_ with
    bilinear interpolation.

    ..  _cv.resize:
            https://docs.opencv.org/3.4.0/da/d54/group__imgproc__transform.html#ga47a974309e9102f5f08231edc7e7529d

    :param X: Image of shape (W, H) or batch of images of shape (N, W, H),
        where N: #samples, W: image width, H: image height.
    :type X: numpy.array
    :param resize_factor: Size to reshape images.
    :type resize_factor: tuple
    :return: List containing image batches with resized images. E.g. (2,2).
    :rtype: numpy.array
    """
    im = []
    if X.ndim == 2:
        im = cv2.resize(X, resize_factor)
    elif X.ndim == 3:
        im = np.array([cv2.resize(x, resize_factor) for x in X])
    return im


################################################################################
# PROCESSORS
################################################################################
def generate_preprocess_params(X, filepath, verbose=False):
    """
    Generates an HDF5 file with the preprocessing parameters. These include:

        - Mean image: Image containing the mean for each pixel location.
        - Pixel mean: Overal pixel intensity mean (scalar value).
        - Pixel standard deviation: Overall pixel standard deviation (scalar
            value).
        - Pixel maximum value: Overall maximum pixel intensity value (scalar
            value).
        - Pixel minimum value: Overall minimum pixel intensity value (scalar
            value).

    This
    :param X: List with numpy.arrays of data. Each array is a chunk of the
        data. If you only have one single array, say `B`, just use `[B]`.
    :type X: list
    :param filepath: Path where preprocessing param file will be stored.
    :type filepath: str
    :return:
    """
    # Compute image mean
    print("Computing mean image...") if verbose else 0
    mean = get_mean_image(X)
    # Find maximum/Minimum values
    print("Computing max/min values...") if verbose else 0
    max_value, min_value = get_max_min(X)
    # Get pixel mean
    print("Computing mean pixel...") if verbose else 0
    pmean = get_mean_pixel(X)
    # Get pixel standard deviation
    print("Computing pixel std...") if verbose else 0
    pstd = get_std_pixel(X, pmean)

    # Create dictionary with params
    data = {
        'image_mean': mean,
        'pixel_mean': pmean,
        'pixel_std': pstd,
        'max_value': max_value,
        'min_value': min_value
    }
    from pyphoon.io.h5 import write_h5_dataset_file
    # Store params
    print("Storing...") if verbose else 0
    write_h5_dataset_file(data, filepath, compression=None)


class ImagePreprocessor(object):
    """ Parent class for image preprocessing classes. This class does not
    implement any method, please refer to its child classes.

    :param add_axis: Adds an axis to your data files. This is convenient as
        many DL frameworks require specific shapes, like Keras which requires
        number of channels to be present. You can expand several axis,
        be careful, however that order matters. Therefore if you want to add to
        position 0 and N, use **add_axis** = [0, N+1] or [N, 0].
    :type add_axis: list of int
    :param type: Specify the type of the image file after preprocessing.
    :type: type
    """

    def __init__(self, add_axis, type):
        self.add_axis = add_axis
        self.type = type

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
        if not self.add_axis:
            if self.type:
                X = X.astype(self.type)
        else:
            for axis in self.add_axis:
                X = np.expand_dims(X, axis=axis)
            X = X.astype(self.type)
        return X


class DefaultImagePreprocessor(ImagePreprocessor):
    """ Child of of :class:`~pyphoon.app.preprocess.ImagePreprocessor`.
    Assuming an input image :math:`X`, this preprocessor first centres and
    normalises it as

    .. math::  \\frac{X-\mu}{\sigma}

    where :math:`\mu` and :math:`\sigma` denote the pixel mean and standard
    deviation, respectively. Next, it resizes the image using the method
    :func:`resize`.


    :param resize_factor: To resize the image. For instance, half the
        dimensions by setting this parameter equal to 2.
    :param mean: Used to centre the data.
    :param std: Used to normalise the data.
    :param add_axis: Adds axis to arrays. See
        :class:`~pyphoon.app.preprocess.ImagePreprocessor`
    :type add_axis: list of int
    :param type: Specify the type of the image file after preprocessing.
    :type: type
    """
    def __init__(self, mean, std, resize_factor=None, add_axis=None, type=None):
        super().__init__(add_axis, type)
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
            X = resize(X, self.resize_factor)

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

    :param mean_image: Mean image (2D matrix)
    :type mean_image: numpy.array
    :param scale_factor: Used to normalise the data. By default it does not
        scale.
    :type scale_factor: int
    :param resize_factor: To resize the image. Define the new size of the images.
    :type resize_factor: tuple
    :param add_axis: Adds axis to arrays. See
        :class:`~pyphoon.app.preprocess.ImagePreprocessor`
    :type add_axis: list of int
    :param type: Specify the type of the image file after preprocessing.
    :type: type
    """
    def __init__(self, mean_image, scale_factor=1,
                 resize_factor=None, add_axis=None, type=None):
        super().__init__(add_axis, type)
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

        #if X.ndim != 3:
        #    raise Exception("X.ndim must be 3 with X.shape = (N, W, H), "
        #                    "where N: #samples, W: image_width, "
        #                    "H: # image_height")

        # Resize chunk images
        if self.resize_factor:
            X = resize(X, self.resize_factor)

        # Centre & normalise
        X = (X - self.mean)/self.scale

        # Reshape
        X = self.reshape(X)
        return X
"""
This submodule contains different methods to detect corrupted images. The
standard notation is ``detect_corrupted_pixels_<method index>``.
"""
# TODO: Generic method able to call specific detection methods. See decorators
################################################################################
# Detection methods
################################################################################


def detect_corrupted_pixels_1(image_frame, params):
    """ Detects pixel positions that are corrupted using a rather simple
    approach. It forces all pixels to be within the range defined by
    [min_th, max_th].

    :param image_frame: Image frame
    :type image_frame: numpy.array
    :param params: Should contain two keys:

        *   ``min_th``: Minimum tolerated pixel intensity (temperature) value.
        *   ``max_th``: Maximum tolerated pixel intensity (temperature) value.
    :type params: dict
    :return:
    """
    if 'min_th' not in params:
        params['min_th'] = 160
    elif type(params['min_th']) is not int:
        raise Exception("Invalid type for params['min_th']. It should be int.")
    if 'max_th' not in params:
        params['max_th'] = 310
    elif type(params['max_th']) is not int:
        raise Exception("Invalid type for params['max_th']. It should be int.")

    return (image_frame < params['min_th']) + (image_frame > params['max_th'])


################################################################################
# Deprecated
################################################################################


"""
def find_corrupted_frames_1(typhoon_sequence, max_th=None, min_th=None):
    Finds corrupted frames within the sequence under certain
    criteria. This simple approach basically verifies that all pixel values
    are within a range, defined by variables **max_th** and **min_th**.

    :param typhoon_sequence: Sequence of a certain typhoon
    :type typhoon_sequence: TyphoonList
    :param max_th: Maximum pixel intensity value allowed.
    :type max_th: float
    :param min_th: Minimum pixel intensity value allowed.
    :type min_th: float
    :return: List with corrupted frame indices. Also a list with the details
                about the corrupted files.
    |
    :Example:
        >>> from pyphoon.io.typhoonlist import read_typhoonlist_h5
        >>> # Load sequence from HDF file
        >>> path = "data/201626.h5"
        >>> typhoon_sequence = read_typhoonlist_h5(path_to_file=path)
        >>> corrupted_frames, corrupted_info = typhoon_sequence.find_corrupted_frames_1()
    # Get mean, maximum and minimum values of each image in the sequence
    maxv = np.max(typhoon_sequence.data['X'], axis=1).max(axis=1)
    minv = np.min(typhoon_sequence.data['X'], axis=1).min(axis=1)

    # Criteria for non-acceptable (corrupted) image
    if max_th is None:
        max_th = 310
    if min_th is None:
        min_th = 160

    corrupted_frames = []
    corrupted_info = []
    # Iterate over all images in the sequence
    for i in range(len(maxv)):
        corrupted_info_ = {}
        added = False
        # (A) Pixel too high
        if maxv[i] > max_th:
            corrupted_info_["max"] = maxv[i]
            if not added:
                corrupted_frames.append(i)
                added = True
        # (B) Pixel too low
        if minv[i] < min_th:
            corrupted_info_["min"] = minv[i]
            if not added:
                corrupted_frames.append(i)

        # If applicable, add details on the criteria that this frame was
        # classified as corrupted
        if bool(corrupted_info_):
            corrupted_info.append(corrupted_info_)

    return corrupted_frames, corrupted_info


def find_corrupted_frames_2(typhoon_sequence, mean_th=None, max_th=None,
                             min_th=None):
    Finds corrupted frames within the sequence under certain
    criteria. There are three different categories under which a frame
    can fall as corrupted.

    1.  Mean-corrupted: A frame is considered *mean-corrupted* if its
        pixel intensity mean is not in the range given by the function
        argument *mean_th*.
    2.  Max-corrupted: A frame is considered *max-corrupted* if its
        maximum pixel intensity value is not within the range given by the
        function argument *max_th*.
    3.  Min-corrupted: A frame is considered *min-corrupted* if its
        minimum pixel intensity value is not within the range given by the
        function argument *min_th*.

    :param typhoon_sequence: Sequence of a certain typhoon
    :type typhoon_sequence: TyphoonList
    :param mean_th: Minimum and maximum value accepted for an image pixel
                    intensity mean. By default range [235, 292] is used.
    :type mean_th: list
    :param max_th: Minimum and maximum value accepted for an image
                    maximum pixel intensity value. By default range [277,
                    324] is used.
    :type max_th: list
    :param min_th: Minimum and maximum value accepted for an image
                    minimum pixel intensity value. By default range [165,
                    235] is used.
    :type min_th: list
    :return: List with corrupted frame indices. Also a list with the details
                about the corrupted files.
    |
    :Example:
        >>> from pyphoon.io import read_typhoonlist_h5
        >>> # Load sequence from HDF file
        >>> path = "data/201626.h5"
        >>> typhoon_sequence = read_typhoonlist_h5(path_to_file=path)
        >>> corrupted_frames, corrupted_info = typhoon_sequence.find_corrupted_frames_2()
    # Get mean, maximum and minimum values of each image in the sequence
    mean = np.mean(typhoon_sequence.data['X'], axis=1).mean(axis=1)
    maxv = np.max(typhoon_sequence.data['X'], axis=1).max(axis=1)
    minv = np.min(typhoon_sequence.data['X'], axis=1).min(axis=1)

    # Criteria for non-acceptable (corrupted) image
    if mean_th is None:
        mean_th = [235, 292]
    if max_th is None:
        max_th = [277, 324]
    if min_th is None:
        min_th = [165, 235]

    corrupted_frames = []
    corrupted_info = []
    # Iterate over all images in the sequence
    for i in range(len(mean)):
        corrupted_info_ = {}
        added = False
        # (A) Irregular mean value
        if mean[i] < mean_th[0] or mean[i] > mean_th[1]:
            corrupted_info_["mean"] = mean[i]
            if not added:
                corrupted_frames.append(i)
                added = True
        # (B) Irregular maximum value
        if maxv[i] < max_th[0] or maxv[i] > max_th[1]:
            corrupted_info_["max"] = maxv[i]
            if not added:
                corrupted_frames.append(i)
                added = True
        # (C) Irregular minimum value
        if minv[i] < min_th[0] or minv[i] > min_th[1]:
            corrupted_info_["min"] = minv[i]
            if not added:
                corrupted_frames.append(i)

        # If applicable, add details on the criteria that this frame was
        # classified as corrupted
        if bool(corrupted_info_):
            corrupted_info.append(corrupted_info_)

    return corrupted_frames, corrupted_info
"""
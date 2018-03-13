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
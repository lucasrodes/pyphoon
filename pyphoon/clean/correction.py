"""
This submodule contains different methods to correct corrupted images. The
standard notation is ``correct_corrupted_pixels_<method index>``.
"""

import numpy as np
# TODO: Generic method able to call specific correction methods. See decorators
################################################################################
# Correction methods
################################################################################


def correct_corrupted_pixels_1(typhoon_sequence, index, pos,
                               detect_fct, display, params):
    """Corrects the pixels in region pos from image frame at position index
    of typhoon_sequence. To this end, it uses interpolation of this
    region in nearby frames.

    :param typhoon_sequence: List of typhoon frames
    :type typhoon_sequence: TyphoonList
    :param index: Frame index from typhoon_sequence
    :type index: int
    :param pos: Numpy array of same dimensionality than
        *typhoon_sequence.image[index]* with True values in regions
        containing corrupted pixels. False values refer to regions with no
        corrupted pixels.
    :type pos: numpy.array
    :param detect_fct: Callable function that detects corrupted values from
        an array according to some given rules.
    :type detect_fct: callable
    :param display: Set to True if execution information should be printed.
    :type display: True
    :param params: Parameters for detection function
    :type params: dict
    :return:
    """
    K = len(typhoon_sequence.get_data('images'))

    # BACKWARD
    if index > 0:
        region_n = typhoon_sequence.get_data('images')[index - 1][pos]
        c_n = np.ones_like(region_n)
        pos_n = detect_fct(region_n, params)

        k = 2
        print(" backward") if display else 0
        print("  - 1") if display else 0
        while True in pos_n and index - k >= 0:
            print("  -", k) if display else 0
            region_n[pos_n] = typhoon_sequence.get_data('images')[index - k][
                pos][pos_n]
            if k < 15:
                c_n[pos_n] *= np.exp(-1)
            pos_n = detect_fct(region_n, params)
            k += 1

        if True in pos_n:
            # TODO: Change to mean image values (using pos)
            print("  exception") if display else 0
            region_n[pos_n] = 270
            # c_n[pos_n] *= np.exp(-1)

    else:
        c_n = 0
        region_n = 0

    # FORWARD
    if index < K - 1:
        region_p = typhoon_sequence.get_data('images')[index + 1][pos]
        c_p = np.ones_like(region_p)
        pos_p = detect_fct(region_p, params)

        k = 2
        print(" forward") if display else 0
        print("  + 1") if display else 0
        while True in pos_p and index + k < K:
            print("  +", k) if display else 0
            region_p[pos_p] = typhoon_sequence.get_data('images')[index + k][
                pos][pos_p]
            if k < 15:
                c_p[pos_p] *= np.exp(-1)
            pos_p = detect_fct(region_p, params)
            k += 1

        if True in pos_p:
            # TODO: Change to mean image values (using pos)
            print("  exception") if display else 0
            region_p[pos_p] = 270
            # c_p[pos_p] *= np.exp(-1)
    else:
        c_p = 0
        region_p = 0

    return (c_n*region_n + c_p*region_p)/(c_n + c_p)
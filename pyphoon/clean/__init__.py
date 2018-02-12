import numpy as np
import copy
import time


def fix_sequence(typhoon_sequence, correct_frames=True, gap_filling=False,
                 display=False, n_frames_th=6, fix_params=None):
    """ Goes through a typhoon sequence and corrects its frames. This includes
    detecting and correcting corrupted images as well as filling some
    image temporal gaps by using interpolation.

    :param typhoon_sequence: Sequence of typhoon data. All frames should
        belong to a certain typhoon sequence.
    :type typhoon_sequence: TyphoonList
    :param correct_frames: Set to False if frames should not be corrected.
    :type correct_frames: bool, default True
    :param gap_filling: Set to True if temporal image
        frame gaps should be filled with synthetic image frames.
    :type gap_filling: bool, default False
    :param display: Set to True if alerts and running information should be
        displayed
    :param n_frames_th:
    :param fix_params: parameters required for the detection/correction of
        corrupted image frame regions.
    :return: Fixed typhoon sequence
    :rtype: TyphoonList
    :Example:

        For this example, we use the typhoon sequence *198702*.

        >>> from pyphoon.io import read_typhoonlist_h5
        >>> typhoon_sequence = read_typhoonlist_h5('path/to//198702.h5')

        Next, we can fix the sequence in multiple ways. By default, temporal
        gaps are not filled and. To have information messages about the fixing
        process we set the option *display* to be True.

        >>> from pyphoon.clean import fix_sequence
        >>> typhoon_sequence_new = fix_sequence(typhoon_sequence, display=True)

        If we want to change the detection/correction parameters, say to
        lower the minimum threshold we can do as following:

        >>> typhoon_sequence_new = fix_sequence(typhoon_sequence, display=True, params={'min_th': 150})

        In case that we want to fill the temporal gaps, use as follows

        >>> typhoon_sequence_new = fix_sequence(typhoon_sequence, gap_filling=True, display=True, params={'min_th': 150})
    """
    # Set thresholds for pixel values
    if fix_params is None:
        fix_params = {}

    typhoon_sequence_new = copy.deepcopy(typhoon_sequence)

    # Correct frames
    if correct_frames:
        for index in range(len(typhoon_sequence_new.images)):
            fix_frame(
                typhoon_sequence_new,
                index,
                display=display,
                params=fix_params,
                detect_fct=_detect_corrupted_pixels_1,
                correct_fct=_correct_corrupted_pixels_1
            )

    #  Fill temporal gaps
    if gap_filling:
        t0 = time.time()
        fill_gaps(typhoon_sequence_new, n_frames_th)

    return typhoon_sequence_new


#######################################
#     FRAME FIX RELATED FUNCTIONS     #
#######################################

# TODO: Document which functions are there available for detection/correction
def fix_frame(typhoon_sequence, index, display, params, detect_fct,
              correct_fct):
    """ Searches for frame regions with corrupted pixels and attempts to
    correct those.

    :param typhoon_sequence: Sequence of typhoon data.
    :type typhoon_sequence: TyphoonList
    :param index: Frame position within *typhoon_sequence*.
    :type index: int
    :param display: Set to True to have information messages printed.
    :type display: bool
    :param params: Parameters required for detection and correction functions.
    :type params: dict
    :param detect_fct: Corrupted pixel area detection function.
    :type detect_fct: callable
    :param correct_fct: Corrupted pixel area correction function.
    :type correct_fct: callable
    """
    print("\n-----------\nindex:", index) if display else 0

    # GET AFFECTED AREA
    pos = detect_fct(typhoon_sequence.images[index], params=params)

    # CORRECT AREA
    if True in pos:
        # Correct frame
        typhoon_sequence.images[index][pos] = \
            correct_fct(typhoon_sequence, index, pos, detect_fct, display,
                        params=params)
        # Add fix-flag: Frame has been corrected
        image_id = typhoon_sequence.images_ids[index]
        index_best = typhoon_sequence.best_ids.index(image_id)
        typhoon_sequence.data['Y'][index_best, -1] = 1


def _detect_corrupted_pixels_1(image_frame, params):
    """ Detects pixel positions that are corrupted using a rather simple
    approach. It forces all pixels to be within the range defined by *[
    min_th, max_th]*

    :param image_frame: Image frame
    :type image_frame: numpy.array
    :param params: Should contain two keys:
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


# TODO: Change interpolation weight using time frame distance rather than raw
#  frame distance
def _correct_corrupted_pixels_1(typhoon_sequence, index, pos,
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
    K = len(typhoon_sequence.images)

    # BACKWARD
    if index > 0:
        region_n = typhoon_sequence.images[index - 1][pos]
        c_n = np.ones_like(region_n)
        pos_n = detect_fct(region_n, params)

        k = 2
        print(" backward") if display else 0
        print("  - 1") if display else 0
        while True in pos_n and index - k >= 0:
            print("  -", k) if display else 0
            region_n[pos_n] = typhoon_sequence.images[index - k][pos][pos_n]
            c_n[pos_n] *= np.exp(-k + 1)
            pos_n = detect_fct(region_n, params)
            k += 1

        if True in pos_n:
            # TODO: Change to mean image values (using pos)
            print("  exception") if display else 0
            region_n[pos_n] = 270
            c_n[pos_n] *= np.exp(-k + 1)

    else:
        c_n = 0
        region_n = 0

    # FORWARD
    if index < K - 1:
        region_p = typhoon_sequence.images[index + 1][pos]
        c_p = np.ones_like(region_p)
        pos_p = detect_fct(region_p, params)

        k = 2
        print(" forward") if display else 0
        print("  + 1") if display else 0
        while True in pos_p and index + k < K:
            print("  +", k) if display else 0
            region_p[pos_p] = typhoon_sequence.images[index + k][pos][pos_p]
            c_p[pos_p] *= np.exp(-k + 1)
            pos_p = detect_fct(region_p, params)
            k += 1

        if True in pos_p:
            # TODO: Change to mean image values (using pos)
            print("  exception") if display else 0
            region_p[pos_p] = 270
            c_p[pos_p] *= np.exp(-k + 1)
    else:
        c_p = 0
        region_p = 0

    return (c_n*region_n + c_p*region_p)/(c_n + c_p)


#######################################
#   TEMPORAL GAPS RELATED FUNCTIONS   #
#######################################

def fill_gaps(typhoon_sequence, n_frames_th):
    """ Fills the temporal image frame gaps of *typhoon_sequence* with
    interpolated image frames.

    :param typhoon_sequence: Sequence of typhoon data.
    :type typhoon_sequence: TyphoonList
    :param n_frames_th: Threshold above which it should not be interpolated
        anymore. This is done so as to prevent from filling too long gaps,
        which could lead to very blurry and distorted frames.
    :type n_frames_th: int
    """
    # Copy typhoon sequence
    typhoon_sequence_raw = copy.deepcopy(typhoon_sequence)

    n_frames_cum = 0  # index shift in new typhoon sequence
    for index in range(len(typhoon_sequence_raw.images)):
        if index != 0:
            n_frames_cum = _fill_gaps(typhoon_sequence_raw, typhoon_sequence,
                                      index, n_frames_cum, n_frames_th)


def _fill_gaps(typhoon_sequence_raw, typhoon_sequence, index, n_frames_cum,
               n_frames_th):
    """ Checks if there is a temporal gap between frames at positions index-1
    and index. If there is a gap and it is within the tolerable range,
    it proceeds to generate new frames through interpolation of
    temporal-nearby frames.

    :param typhoon_sequence_raw: Original typhoon sequence.
    :type typhoon_sequence_raw: TyphoonList
    :param typhoon_sequence: New typhoon sequence where new synthetic frames
        should be added.
    :type typhoon_sequence: TyphoonList
    :param index: We check if there are any temproal gaps between frame
        at position *index*-1 and *index* from sequence *typhoon_sequence_raw*.
    :type index: int
    :param n_frames_cum: Total number of frames added to the sequence so far.
    :type n_frames_cum: int
    :param n_frames_th: Frame distance threshold above which we should not
        interpolate anymore.
    :return: Updated cummulative number of added frames to the sequence
    :rtype: int
    """
    # Distance in hours between frame at position index and frame at index - 1
    frame_dist = typhoon_sequence_raw.get_image_frames_distance(index - 1,
                                                                index) -1

    # Fill gap only if frame distance is below a certain threshold
    if 0 < frame_dist < n_frames_th+10:
        # Interpolate frames
        new_frames = interpolate_image_frames(typhoon_sequence_raw,
                                              index - 1, index,
                                              n_frames=frame_dist)
        # Generate ids for new frames
        new_frames_ids = generate_image_frames_ids(typhoon_sequence_raw,
                                                   index-1, index,
                                                   n_frames=frame_dist)
        # Add synthetic image flags for new frames
        index_best = typhoon_sequence.best_ids.index(new_frames_ids[0])
        for idx in range(len(new_frames)):
            typhoon_sequence.data['Y'][index_best + idx, -2] = 1
            typhoon_sequence.data['Y'][index_best + idx, -1] = 2

        # Insert new image frames and ids
        # TODO: This takes a lot of time!
        typhoon_sequence.insert_frames(new_frames, new_frames_ids, index +
                                       n_frames_cum)
        n_frames_cum += frame_dist
    elif frame_dist >= n_frames_th:
        print(index, frame_dist)
    return n_frames_cum


def interpolate_image_frames(typhoon_sequence, frame_idx_0, frame_idx_1,
                             n_frames=1):
    """ Linearly interpolates two frames from a typhoon sequence.

    :param typhoon_sequence: Sequence of typhoon data
    :type typhoon_sequence: TyphoonList
    :param frame_idx_0: First frame index
    :type frame_idx_0: int
    :param frame_idx_1: Second frame index
    :type frame_idx_1: int
    :param n_frames: Number of frames to generate using interpolation
    :type n_frames: int
    :return: List with the new generated frames
    :rtype: list
    """
    frame_0 = typhoon_sequence.images[frame_idx_0]
    frame_1 = typhoon_sequence.images[frame_idx_1]
    frames_new = [((n_frames-n)*frame_0 + (n+1)*frame_1) / (n_frames+1) for
                  n in range(n_frames)]
    # TODO: Reduce number of different values appearing in all elements in
    # frames_new
    return frames_new


# TODO: Place in better file location
def generate_image_frames_ids(typhoon_sequence, frame_idx_0, frame_idx_1,
                              n_frames=1):
    """ Generates ids of n_frames in between positions frame_idx_0 and
    fram_idx_1. This is useful when new image frames have been generated
    through interpolation and require an id.

    :param typhoon_sequence: Sequence of typhoon
    :type typhoon_sequence: TyphoonList
    :param frame_idx_0: Index of first frame
    :type frame_idx_0: int
    :param frame_idx_1: Index of second frame
    :type frame_idx_1: int
    :param n_frames: Number of frames for which an id has to be generated.
    :return: List of newly generated ids.
    :rtype: list
    """
    dif = typhoon_sequence.images_dates(frame_idx_1) - \
          typhoon_sequence.images_dates(frame_idx_0)

    name = typhoon_sequence.images_ids[0].split('_')[0]
    ids_new = [
        name + "_" + (typhoon_sequence.images_dates(frame_idx_0) + (n + 1)/(
            n_frames + 1) * dif).strftime("%Y%m%d%H") for n in range(n_frames)
    ]

    return ids_new


#######################################
#        FIND CORRUPTED FRAMES        #
#######################################

def find_corrupted_frames_1(typhoon_sequence, mean_th=None, max_th=None,
                          min_th=None):
    """ Finds corrupted frames within the sequence under certain
    criteria. This simple approach basically verifies that all pixel values
    are within a range, defined by variables **max_th** and **min_th**.

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
        >>> corrupted_frames, corrupted_info = typhoon_sequence.find_corrupted_frames_1()
    """
    # Get mean, maximum and minimum values of each image in the sequence
    maxv = np.max(typhoon_sequence.data['X'], axis=1).max(axis=1)
    minv = np.min(typhoon_sequence.data['X'], axis=1).min(axis=1)

    # Criteria for non-acceptable (corrupted) image
    max_th = 310
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
    """ Finds corrupted frames within the sequence under certain
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
    """
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
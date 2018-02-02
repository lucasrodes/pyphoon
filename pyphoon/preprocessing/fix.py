import numpy as np
import copy


def fix_sequence(typhoon_sequence):
    """ Goes through a typhoon sequence and corrects it. This includes
    detecting and correcting corrupted images as well as filling some
    image temporal gaps by using interpolation.

    :param typhoon_sequence: Sequence of typhoon data
    :type typhoon_sequence: TyphoonSequence
    :return:
    """
    # Correct frames
    for index in range(len(typhoon_sequence.images)):
        # check if frame is corrupted and fix frame
        correct_frame(typhoon_sequence, index)
    #
    #  Fill temporal gaps
    fill_gaps(typhoon_sequence)

    # TODO: flag to typhoon_sequence.best stating whether frame was fixed


def fill_gaps(typhoon_sequence):
    """ Fills the temporal image gaps of typhoon sequence.

    :param typhoon_sequence: Sequence of typhoon data.
    :type typhoon_sequence: TyphoonSequence
    """
    # Fill temporal gaps
    acc = 0
    typhoon_sequence_raw = copy.deepcopy(typhoon_sequence)
    for index in range(len(typhoon_sequence.images)):
        if index != 0:
            acc = _fill_gaps(typhoon_sequence_raw, typhoon_sequence, index, acc)


def _fill_gaps(typhoon_sequence_raw, typhoon_sequence, index, acc):
    # check distance between images
    n_frames = int(typhoon_sequence_raw.get_image_frames_distance(index - 1,
                                                                  index) //
                   3600 - 1)
    # insert new frames
    if n_frames != 0:
        # check if original frames are corrupted
        print(index, ":", n_frames)
        if n_frames < 5:
            # Interpolate frames
            new_frames = interpolate_image_frames(typhoon_sequence_raw, index,
                                            index - 1, n_frames=n_frames)
            # Generate ids for new frames
            new_frames_ids = generate_image_frames_ids(typhoon_sequence_raw,
                                                       index - 1, index,
                                                       n_frames=n_frames)
            # Insert new image frames and ids
            typhoon_sequence.insert_frames(new_frames,
                                           new_frames_ids, index + acc)
            acc += n_frames
    return acc


def interpolate_image_frames(typhoon_sequence, frame_idx_0, frame_idx_1,
                            n_frames=1):
    """ Linearly interpolates two frames from a typhoon sequence.

    :param typhoon_sequence: Sequence of typhoon data
    :type typhoon_sequence: TyphoonSequence
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
    return frames_new


def generate_image_frames_ids(typhoon_sequence, frame_idx_0, frame_idx_1,
                              n_frames=1):
    """ Generates ids of n_frames in between positions frame_idx_0 and
    fram_idx_1. This is useful when new image frames have been generated
    through interpolation and require an id.

    :param typhoon_sequence: Sequence of typhoon
    :type typhoon_sequence: TyphoonSequence
    :param frame_idx_0: Index of first frame
    :type frame_idx_0: int
    :param frame_idx_1: Index of second frame
    :type frame_idx_1: int
    :param n_frames: Number of frames for which an id has to be generated.
    :return: List of newly generated ids.
    :rtype: list
    """
    dif = typhoon_sequence.images_date(frame_idx_1) - \
          typhoon_sequence.images_date(frame_idx_0)

    ids_new = [int((typhoon_sequence.images_date(frame_idx_0) + (n + 1) / (
        n_frames + 1) * dif).strftime("%Y%m%d%H")) for n in range(n_frames)]
    return ids_new


# TODO: do comparison pixel-wise. Use mean image + 2deviation image!
def correct_frame(typhoon_sequence, index, min_th=160, max_th=325):
    """
    Possible ways to correct:
        1. Interpolate regions of affected pixels in nearby images
        2. Saturate pixel intensities within a pre-defined range
        3. Use mean image
        4. Discard image

    :param typhoon_sequence:
    :param index:
    :param min_th:
    :param max_th:
    :param pos:
    """
    if index == 0:
        pass
    elif index == len(typhoon_sequence.images) - 1:
        pass
    else:
        # 1. Interpolate nearby images

        # Update max/min thresholds
        _max = (np.max(typhoon_sequence.images[index-1]) +
                     np.max(typhoon_sequence.images[index+1]))/2
        _min = (np.min(typhoon_sequence.images[index - 1]) +
                     np.min(typhoon_sequence.images[index + 1]))/2
        if max_th - _max > 10:
            _max_th = (max_th + _max)/2
        else:
            _max_th = max_th
        if min_th - _min < -10:
            _min_th = (min_th + _min)/2
        else:
            _min_th = min_th

        # Find corrupted pixels
        pos = (typhoon_sequence.images[index] < _min_th) + (
            typhoon_sequence.images[index] > _max_th)
        # Interpolate corrupted pixels with nearby images
        typhoon_sequence.images[index][pos] \
            = (typhoon_sequence.images[index-1][pos] +
               typhoon_sequence.images[index+1][pos])/2

        if True in pos:
            typhoon_sequence.images[index][pos] = 270
            #print(index)
        #pos = (typhoon_sequence.images[index][pos] < min_th) \
        #                            + (typhoon_sequence.images[index][pos] >
        #  max_th)
    """
    k = 2
    while True in pos:
        # interpolate with next frames
        if index - k >= 0 and index + k < len(typhoon_sequence.images):
            typhoon_sequence.images[index][pos] = (typhoon_sequence.images[
                index - k][pos] + typhoon_sequence.images[index + k][pos]) / 2
        # TODO: Interpolate with average image
        else:
            typhoon_sequence.images[index][pos] = 270
        k += 1
        pos = typhoon_sequence.images[index][pos] < min_th \
                                                    + typhoon_sequence.images[
                                                        index][pos] > max_th
    """


def find_corrupted_frames(typhoon_sequence, mean_th=None, max_th=None,
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
    :type typhoon_sequence: TyphoonSequence
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

        >>> from pyphoon.utils.io import load_TyphoonSequence
        >>> # Load sequence from HDF file
        >>> path = "data/201626.h5"
        >>> typhoon_sequence = load_TyphoonSequence(path_to_file=path)
        >>> corrupted_frames, corrupted_info = typhoon_sequence.find_corrupted_frames()
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
                added = True

        # If applicable, add details on the criteria that this frame was
        # classified as corrupted
        if bool(corrupted_info_):
            corrupted_info.append(corrupted_info_)

    return corrupted_frames, corrupted_info
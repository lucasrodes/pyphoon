import copy

################################################################################
# Main Class: FixAlgorithm
################################################################################


class TyphoonListImageFixAlgorithm(object):
    """
    Encapsulates an algorithm to correct and clean ("fix") a typhoon sequence.

    :var detect_fct: Method used to detect corrupted frames (more details in
        :mod:`~pyphoon.clean.detection`)
    :var correct_fct: Method used to correct corrupted frames (more details in
        :mod:`~pyphoon.clean.correction`)
    :var fillgaps_fct: Method used to fill gaps in a sequence (more details in
        :mod:`~pyphoon.clean.fillgaps`)
    :var detect_params: Parameters required to assist the detection method.
        More details can be found in the specific detection method (see from
        :mod:`~pyphoon.clean.detection`)
    :var n_frames_th: Largest temporal gap to fill with newly generated image
        frames (measured in slots of 1h). In other words, if there is a
        temporal gap of more than ``n_frames_th`` hours no new image frames
        are generated.
    """
    def __init__(self, detect_fct=None, correct_fct=None,
                 fillgaps_fct=None, detect_params=None, n_frames_th=None):
        self.detect_fct = detect_fct
        self.correct_fct = correct_fct
        self.fillgaps_fct = fillgaps_fct
        self.detect_params = detect_params
        self.n_frames_th = n_frames_th
        self.fixed_ids = {'corrected': None, 'generated': None}

    def apply(self, typhoon_sequence, display=False):
        """ Applies the defined fix algorithm to a given typhoon
        sequence.

        :param typhoon_sequence: Input typhoon sequence to be fixed.
        :type typhoon_sequence: :class:`~pyphoon.io.typhoonlist.TyphoonList`
        :param display: Set to True to print execution information.
        :type display: bool
        :return: New typhoon sequence with cleaned data.
        :rtype: :class:`~pyphoon.io.typhoonlist.TyphoonList`
        """
        typhoon_sequence_new = copy.deepcopy(typhoon_sequence)

        # Detect and correct corrupted frames
        if self.detect_fct is not None and self.correct_fct is not None:
            ids = self.detect_and_correct(typhoon_sequence_new, display)
            self.fixed_ids['corrected'] = ids
        # Generate synthetic images
        if self.fillgaps_fct is not None:
            ids = self.fill_gaps(typhoon_sequence_new)
            self.fixed_ids['generated'] = ids

        return typhoon_sequence_new

    def clear(self):
        """ Resets the list of corrected/generated frame ids.
        """
        self.fixed_ids = {'corrected': None, 'generated': None}

    def detect_and_correct(self, typhoon_sequence, display):
        """ Detects and corrects irregularities in image frames from
        ``typhoon_sequence``  using the methods specified by attributes
        ``detect_fct`` and ``correct_fct``, respectively.

        :param typhoon_sequence: Input typhoon sequence to be fixed.
        :type typhoon_sequence: :class:`~pyphoon.io.typhoonlist.TyphoonList`
        :param display: Set to True to print execution information.
        :type display: bool
        :return: Ids of the corrected images
        :rtype: list

        .. seealso:: :mod:`pyphoon.clean.detection`,
                    :mod:`pyphoon.clean.correction`

        """
        new_ids = []

        for index in range(len(typhoon_sequence.get_data('images'))):
            print("\n-----------\nindex:", index) if display else 0

            # GET AFFECTED AREA
            pos = self.detect_fct(typhoon_sequence.get_data('images')[index],
                                  params=self.detect_params)

            # CORRECT AREA
            if True in pos:
                # Correct frame
                typhoon_sequence.get_data('images')[index][pos] = \
                    self.correct_fct(typhoon_sequence, index, pos,
                                     self.detect_fct, display,
                                     params=self.detect_params)
                new_ids.append(typhoon_sequence.get_id('images')[index])
                """
                # Add fix-flag: Frame has been corrected
                image_id = typhoon_sequence.images_ids[index]
                index_best = typhoon_sequence.best_ids.index(image_id)
                typhoon_sequence.data['Y'][index_best, -1] = 1
                """
        return new_ids

    def fill_gaps(self, typhoon_sequence):
        """ Fills the gaps in the given typhoon sequence using the method
        specified by attribute ``fillgaps_fct``.

        :param typhoon_sequence: Input typhoon sequence to be fixed.
        :type typhoon_sequence: :class:`~pyphoon.io.typhoonlist.TyphoonList`
        :return: List with the ids of the new generated frames
        :rtype: list

        .. seealso:: :mod:`pyphoon.clean.fillgaps`
        """
        # Copy typhoon sequence
        typhoon_sequence_raw = copy.deepcopy(typhoon_sequence)
        new_ids = []

        n_frames_cum = 0  # index shift in new typhoon sequence
        for index in range(len(typhoon_sequence_raw.get_data('images'))):
            if index != 0:
                n_frames_cum, _new_ids = self._fill_gaps(typhoon_sequence_raw,
                                                         typhoon_sequence,
                                                         index, n_frames_cum)
                new_ids.extend(_new_ids)

        typhoon_sequence.insert_ids('images', new_ids)
        return new_ids

    def _fill_gaps(self, typhoon_sequence_raw, typhoon_sequence, index,
                   n_frames_cum):
        """ Checks if there is a temporal gap between frames at positions
        index-1  and index. If there is a gap and it is within the tolerable
        range, it proceeds to generate new frames through interpolation of
        temporal-nearby frames.

        :param typhoon_sequence_raw: Original typhoon sequence.
        :type typhoon_sequence_raw: TyphoonList
        :param typhoon_sequence: New typhoon sequence where new synthetic frames
            should be added.
        :type typhoon_sequence: TyphoonList
        :param index: We check if there are any temporal gaps between frame
            at position ``index-1`` and ``index`` from sequence
            ``typhoon_sequence_raw``.
        :type index: int
        :param n_frames_cum: Total number of frames added to the sequence so
            far.
        :type n_frames_cum: int
        :rtype: int
        """

        new_frames_ids = []
        # Distance in hours between frame at position index and frame at
        # index - 1
        frame_dist = typhoon_sequence_raw.get_sample_distance('images',
                                                              index - 1,
                                                              index) - 1

        # Fill gap only if frame distance is below a certain threshold
        if 0 < frame_dist < self.n_frames_th:
            # Interpolate frames
            new_frames = self.fillgaps_fct(typhoon_sequence_raw, index - 1,
                                            index, n_frames=frame_dist)
            # Generate ids for new frames
            new_frames_ids = \
                generate_image_frames_ids(typhoon_sequence_raw, index - 1,
                                          index, n_frames=frame_dist)
            """
            # Add synthetic image flags for new frames
            index_best = typhoon_sequence.best_ids.index(new_frames_ids[0])
            for idx in range(len(new_frames)):
                typhoon_sequence.data['Y'][index_best + idx, -2] = 1
                typhoon_sequence.data['Y'][index_best + idx, -1] = 2
            """

            # Insert new image frames and ids
            # TODO: This takes a lot of time!
            typhoon_sequence.insert_samples('images', new_frames,
                                            index + n_frames_cum)
            n_frames_cum += frame_dist
        elif frame_dist >= self.n_frames_th:
            pass
            # print(index, frame_dist)
        return n_frames_cum, new_frames_ids


################################################################################
# Other methods
################################################################################

def generate_image_frames_ids(typhoon_sequence, frame_idx_0, frame_idx_1,
                              n_frames=1):
    """ Generates ids of n_frames in between positions ``frame_idx_0`` and
    ``frame_idx_1``. This is useful when new image frames have been generated
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
    dif = typhoon_sequence.get_date('images')[frame_idx_1] - \
          typhoon_sequence.get_date('images')[frame_idx_0]

    name = typhoon_sequence.get_id('images')[0].split('_')[0]
    ids_new = [
        name + "_" + (
        typhoon_sequence.get_date('images')[frame_idx_0] + (n + 1) / (
            n_frames + 1) * dif).strftime("%Y%m%d%H") for n in
        range(n_frames)
    ]

    return ids_new


################################################################################
# Deprecated
################################################################################


"""
def fix_sequence(typhoon_sequence, correct_frames=True, gap_filling=False,
                 display=False, n_frames_th=6, fix_params=None):
    Goes through a typhoon sequence and corrects its frames. This includes
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
        fill_gaps(typhoon_sequence_new, n_frames_th)

    return typhoon_sequence_new


#######################################
#     FRAME FIX RELATED FUNCTIONS     #
#######################################

# TODO: Document which functions are there available for detection/correction
def fix_frame(typhoon_sequence, index, display, params, detect_fct,
              correct_fct):
    Searches for frame regions with corrupted pixels and attempts to
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
"""
"""
This submodule contains different methods to fill the temporal gaps with new
synthetic images. The standard notation is ``generate_new_frames_<method
index>``.
"""


################################################################################
# Fill-Gaps methods
################################################################################


def generate_new_frames_1(typhoon_sequence, frame_idx_0, frame_idx_1,
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
    frame_0 = typhoon_sequence.get_data('images')[frame_idx_0]
    frame_1 = typhoon_sequence.get_data('images')[frame_idx_1]
    frames_new = [((n_frames-n)*frame_0 + (n+1)*frame_1) / (n_frames+1) for
                  n in range(n_frames)]
    # TODO: Reduce number of different values appearing in all elements in
    # frames_new
    return frames_new


################################################################################
# Deprecated
################################################################################

"""
def fill_gaps(typhoon_sequence, n_frames_th):
    Fills the temporal image frame gaps of *typhoon_sequence* with
    interpolated image frames.

    :param typhoon_sequence: Sequence of typhoon data.
    :type typhoon_sequence: TyphoonList
    :param n_frames_th: Threshold above which it should not be interpolated
        anymore. This is done so as to prevent from filling too long gaps,
        which could lead to very blurry and distorted frames.
    :type n_frames_th: int
    
    # Copy typhoon sequence
    typhoon_sequence_raw = copy.deepcopy(typhoon_sequence)

    n_frames_cum = 0  # index shift in new typhoon sequence
    for index in range(len(typhoon_sequence_raw.images)):
        if index != 0:
            n_frames_cum = _fill_gaps(typhoon_sequence_raw, typhoon_sequence,
                                      index, n_frames_cum, n_frames_th)
"""
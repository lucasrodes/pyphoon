"""
This submodule contains different methods to fill the temporal gaps with new
synthetic images. The standard notation is ``generate_new_frames_<method
index>``.
"""


################################################################################
# Fill-Gaps methods
################################################################################


def generate_new_frames_1(images, frame_idx_0, frame_idx_1,
                          n_frames=1):
    """ Linearly interpolates two frames from a typhoon sequence.

    :param images: List with image arrays. Each element of the list must be an
            array of 2 dimensions.
    :type images: list
    :param frame_idx_0: First frame index.
    :type frame_idx_0: int
    :param frame_idx_1: Second frame index.
    :type frame_idx_1: int
    :param n_frames: Number of frames to generate using interpolation.
    :type n_frames: int
    :return: List with the new generated frames.
    :rtype: list
    """
    frame_0 = images[frame_idx_0]
    frame_1 = images[frame_idx_1]
    frames_new = [((n_frames-n)*frame_0 + (n+1)*frame_1) / (n_frames+1) for
                  n in range(n_frames)]
    # TODO: Reduce number of different values appearing in all elements in
    # frames_new
    return frames_new
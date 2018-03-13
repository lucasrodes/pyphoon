import copy
from pyphoon.clean_satellite.utils import generate_image_ids, get_sample_distance
################################################################################
# Main Class: FixAlgorithm
################################################################################


class TyphoonListImageFixAlgorithm(object):
    """
    Encapsulates an algorithm to correct and clean the images from a typhoon
    sequence.

    :param detect_fct: Method used to detect corrupted frames (more details in
        :mod:`~pyphoon.clean.detection`)
    :type detect_fct: callable
    :param correct_fct: Method used to correct corrupted frames (more details in
        :mod:`~pyphoon.clean.correction`)
    :type correct_fct: callable
    :param generate_fct: Method used to fill gaps in a sequence (more details in
        :mod:`~pyphoon.clean.fillgaps`)
    :type generate_fct: callable
    :param detect_params: Parameters required to assist the detection method.
        More details can be found in the specific detection method (see from
        :mod:`~pyphoon.clean.detection`)
    :type detect_params: dict
    :param n_frames_th: Largest temporal gap to fill with newly generated image
        frames (measured in slots of 1h). In other words, if there is a
        temporal gap of more than ``n_frames_th`` hours no new image frames
        are generated.
    :type n_frames_th: int
    """
    def __init__(self, detect_fct=None, correct_fct=None,
                 generate_fct=None, detect_params=None, n_frames_th=None):
        self.detect_fct = detect_fct
        self.correct_fct = correct_fct
        self.generate_fct = generate_fct
        self.detect_params = detect_params
        self.n_frames_th = n_frames_th
        self.fixed_ids = {'corrected': None, 'generated': None}

    def apply(self, images, images_ids):
        """ Applies the defined fix algorithm to ``images``.

        :param images: List of image frames.
        :type images: list
        :param images_ids: List of image ids.
        :type images_ids: list
        :return: Tuple with two elements:
            *   New list of images
            *   New list of the corresponding ids.
        :rtype: tuple
        """
        images_new = copy.deepcopy(images)
        images_ids_new = copy.deepcopy(images_ids)

        # Detect and correct corrupted frames
        if self.detect_fct is not None and self.correct_fct is not None:
            ids = self.detect_and_correct(images_new, images_ids_new)
            self.fixed_ids['corrected'] = ids
        # Generate synthetic images
        if self.generate_fct is not None:
            ids = self.generate(images_new, images_ids_new)
            self.fixed_ids['generated'] = ids

        return images_new, images_ids_new

    def clear(self):
        """ Resets the list of corrected/generated frame ids.
        """
        self.fixed_ids = {'corrected': None, 'generated': None}

    ############################################################################
    # Detect/Correct
    ############################################################################
    def detect_and_correct(self, images, images_ids):
        """ Detects and tries to correct irregularities found in the image
        frames from the list ``images`` using the methods specified by attributes
        ``detect_fct`` and ``correct_fct``, respectively.

        :param images: List with image arrays. Each element of the list must be an
            array of 2 dimensions.
        :type images: list
        :param images_ids: List of the ids of the elements in the list *images*.
        :type images_ids: list
        :return: Ids of the corrected images
        :rtype: list

        .. seealso:: :mod:`pyphoon.clean_satellite.detection`,
                    :mod:`pyphoon.clean_satellite.correction`

        """
        new_ids = []

        for index in range(len(images)):

            # GET AFFECTED AREA
            pos = self.detect_fct(images[index],
                                  params=self.detect_params)

            # CORRECT AREA
            if True in pos:
                # Correct frame
                images[index][pos] = \
                    self.correct_fct(images, index, pos,
                                     self.detect_fct, params=self.detect_params)
                new_ids.append(images_ids[index])
        return new_ids

    ############################################################################
    # Generate
    ############################################################################
    def generate(self, images, images_ids):
        """ Fills the gaps in the given typhoon sequence using the method
        specified by attribute ``generate_fct``.

        :param images: List of image frames.
        :type images: list
        :param images_ids: List of image ids.
        :type images_ids: list
        :return: List with the ids of the new generated frames
        :rtype: list

        .. seealso:: :mod:`pyphoon.clean_satellite.generation`
        """
        images_original = copy.deepcopy(images)
        images_ids_original = copy.deepcopy(images_ids)

        new_ids = []

        n_frames_cum = 0  # index shift in new typhoon sequence
        for index in range(len(images_original)):
            if index != 0:
                n_frames_cum, _new_ids = self._generate(images_original,
                                                        images_ids_original,
                                                        images, index,
                                                        n_frames_cum)
                new_ids.extend(_new_ids)

        images_ids[:] = sorted(images_ids + new_ids)
        return new_ids

    def _generate(self, images_original, images_original_ids, images_new,
                  index, n_frames_cum):
        """ Checks if there is a temporal gap between frames at positions
        index-1  and index. If there is a gap and it is within the tolerable
        range, it proceeds to generate new frames through interpolation of
        temporal-nearby frames.

        :param images_original: Original list of image data.
        :type images_original: list
        :param images_original_ids: Original list of image ids.
        :type images_original_ids: list
        :param images_new: New list where new synthetic frames will be added.
        :type images_new: list
        :param index: We check if there are any temporal gaps between frame
            at position ``index-1`` and ``index`` from sequence
            ``typhoon_sequence_raw``.
        :type index: int
        :param n_frames_cum: Total number of frames added to the sequence so
            far.
        :type n_frames_cum: int
        :rtype: int
        """

        # Define list for new image ids
        new_frames_ids = []

        # Distance in hours between frame at position index and frame at
        # index - 1
        frame_dist = get_sample_distance(images_original_ids[index-1],
                                         images_original_ids[index]) - 1

        # Fill gap only if frame distance is below a certain threshold
        if 0 < frame_dist < self.n_frames_th:
            # Generate new frames
            new_frames = self.generate_fct(images_original, index - 1, index,
                                           n_frames=frame_dist)
            # Generate ids for new frames
            new_frames_ids = generate_image_ids(images_original_ids[index-1],
                                                images_original_ids[index],
                                                n_frames=frame_dist)

            # Insert new image frames and ids
            images_new[index + n_frames_cum:index + n_frames_cum] = \
                new_frames

            n_frames_cum += frame_dist
        elif frame_dist >= self.n_frames_th:
            pass
            # print(index, frame_dist)
        return n_frames_cum, new_frames_ids

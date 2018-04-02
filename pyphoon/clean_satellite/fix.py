import copy
from pyphoon.clean_satellite.utils import generate_image_ids, get_sample_distance
################################################################################
# Main Class: FixAlgorithm
################################################################################


class TyphoonListImageFixAlgorithm(object):
    """ Encapsulates an algorithm to correct and clean the images from a typhoon
    sequence.

    :param detect_fct: Method used to detect corrupted frames (more details in
        :mod:`~pyphoon.clean_satellite.detection`)
    :type detect_fct: callable
    :param correct_fct: Method used to correct corrupted frames (more details in
        :mod:`~pyphoon.clean_satellite.correction`)
    :type correct_fct: callable
    :param generate_fct: Method used to fill gaps in a sequence (more details in
        :mod:`~pyphoon.clean_satellite.generation`)
    :type generate_fct: callable
    :param detect_params: Parameters required to assist the detection method.
        More details can be found in the specific detection method (see from
        :mod:`~pyphoon.clean_satellite.detection`)
    :type detect_params: dict
    :param n_frames_th: Largest temporal gap to fill with newly generated image
        frames (measured in slots of 1h). In other words, if there is a
        temporal gap of more than **n_frames_th** hours no new image frames
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
        self.fixed_indices = {
            'original': {'corrected': None, 'generated': None},
            'fixed': {'corrected': None, 'generated': None}
        }
        if detect_fct and correct_fct:
            self.correction = True
        else:
            self.correction = False
        if generate_fct:
            self.generation = True
        else:
            self.generation = True
        self.index_offset = {}

    def apply(self, images, images_ids):
        """ Applies the defined fix algorithm to all image samples in
        **images**.

        :param images: List of image frames.
        :type images: list
        :param images_ids: List of image ids.
        :type images_ids: list
        :return: Tuple with two elements:

            *   New list of images.
            *   New list of the corresponding ids.
        :rtype: tuple
        """
        images_new = copy.deepcopy(images)
        images_ids_new = copy.deepcopy(images_ids)

        # Detect and correct corrupted frames
        if self.detect_fct is not None and self.correct_fct is not None:
            indices = self.detect_and_correct(images_new, images_ids_new)
            self.fixed_indices['original']['corrected'] = indices
            self.correction = True
        # Generate synthetic images
        if self.generate_fct is not None:
            indices = self.generate(images_new, images_ids_new)
            self.fixed_indices['original']['generated'] = indices['original']
            self.fixed_indices['fixed']['generated'] = indices['fixed']

            self.generation = True
            # Update indices from corrected frames
            self.fixed_indices['fixed']['corrected'] = self._update_idx_cor()
        else:
            self.fixed_indices['fixed']['corrected'] = self.fixed_indices[
                'original']['corrected']

        return images_new, images_ids_new

    def _update_idx_cor(self):
        indices = copy.deepcopy(self.fixed_indices['original']['corrected'])

        if indices is not None:
            for i in range(len(indices)):
                old_offset = 0
                for position, offset in self.index_offset.items():
                    if indices[i] >= position:
                        old_offset = offset
                    else:
                        break
                indices[i] += old_offset

        return indices

    def clear(self):
        """ Resets the list of corrected/generated frame ids.
        """
        self.fixed_indices = {
            'original': {'corrected': None, 'generated': None},
            'fixed': {'corrected': None, 'generated': None}
        }
        self.index_offset = {}

    ############################################################################
    # Detect/Correct
    ############################################################################
    def detect_and_correct(self, images, images_ids):
        """ Detects and tries to correct irregularities found in the image
        frames in the list **images** using the methods specified by class
        attributes **detect_fct** and **correct_fct**, respectively.

        :param images: List with image arrays. Each element of the list must
            be an array of 2 dimensions.
        :type images: list
        :param images_ids: Image ids.
        **images**.
        :type images_ids: list
        :return: Ids of the corrected images
        :rtype: list

        .. seealso:: :mod:`pyphoon.clean_satellite.detection`,
                    :mod:`pyphoon.clean_satellite.correction`

        """
        new_indices = []

        for index in range(len(images)):

            # GET AFFECTED AREA
            pos = self.detect_fct(images[index],
                                  params=self.detect_params)

            # CORRECT AREA
            if True in pos:
                # Correct frame
                images[index][pos] = \
                    self.correct_fct(images, index, pos, images_ids,
                                     self.detect_fct, params=self.detect_params)
                new_indices.append(index)
        return new_indices

    ############################################################################
    # Generate
    ############################################################################
    def generate(self, images, images_ids):
        """ Fills the gaps in the given typhoon sequence using the method
        specified by class attribute **generate_fct**.

        :param images: List of image frames.
        :type images: list
        :param images_ids: List of image ids.
        :type images_ids: list
        :return: Dictionary with the ids of the new generated frames. Keys:

            *   *original*: Frame position in original image list.
            *   *fixed*: Frame position in fixed image list.
        :rtype: dict

        .. seealso:: :mod:`~pyphoon.clean_satellite.generation`
        """
        images_original = copy.deepcopy(images)
        images_ids_original = copy.deepcopy(images_ids)

        new_ids = []
        new_indices = {'original': [], 'fixed': []}
        n_frames_cum = 0  # index shift in new typhoon sequence
        for index in range(len(images_original)):
            if index != 0:
                n_frames_cum, _new_ids, _new_indices = \
                    self._generate(images_original, images_ids_original,
                                   images, index, n_frames_cum)
                if _new_ids:
                    new_ids.extend(_new_ids)
                    new_indices['original'].extend(_new_indices['original'])
                    new_indices['fixed'].extend(_new_indices['fixed'])
                    self.index_offset[index] = n_frames_cum

        images_ids[:] = sorted(images_ids + new_ids)
        return new_indices

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
        """

        # Define list for new image ids and indices
        new_frames_ids = []
        new_indices = {'original': [], 'fixed': []}

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
            # Get indices for generated ids
            index_cum = index + n_frames_cum
            new_indices['original'] = [index - 1 for i in new_frames_ids]
            new_indices['fixed'] = [index_cum + i for i in range(len(
                new_frames_ids))]

            # Insert new image frames and ids
            images_new[index + n_frames_cum:index + n_frames_cum] = \
                new_frames

            n_frames_cum += frame_dist
        elif frame_dist >= self.n_frames_th:
            pass
            # print(index, frame_dist)
        return n_frames_cum, new_frames_ids, new_indices


################################################################################
# Other stuff
################################################################################

def generate_new_image_dataset(images_orig_dir, fix_algorithm,
                               images_corrected_dir=None,
                               images_generated_dir=None,
                               display=False,
                               folders=None):
    """ Inspects the original image data (assuming architecture explained in
    section `Data <data.html>`_ and corrects the detected corrupted images
    and/or generates the missing image data according to the algorithm
    defined by **fix_algorithm**. Note that only the new corrected/generated
    images are stored.

    :param images_orig_dir: Directory of the original image data.
    :type images_orig_dir: str
    :param fix_algorithm: Algorithm used to correct/generate the images.
    :type fix_algorithm:
        :class:`~pyphoon.clean_satellite.fix.TyphoonListImageFixAlgorithm`
    :param images_corrected_dir: Directory for the corrected image data. If
        not used, corrected images are not
    :type images_corrected_dir: str, default None
    :param images_generated_dir: Directory for the generated image data.
    :type images_generated_dir: str, default None
    :param display: Set to True to get information as the method is executed.
    :type display: bool
    :param folders: List of the typhoon sequences to generate/correct. If not
        used, all sequences are used.
    :type folders: list, default None.

    :raises: Exception
    """
    if not isinstance(fix_algorithm, TyphoonListImageFixAlgorithm):
        raise Exception('fix_algorithm should be an instance of '
                        'TyphoonListImageFixAlgorithm class')

    if images_corrected_dir and not fix_algorithm.correction:
        raise Exception('Path for corrected images is given but fix algorithm '
                        'does not implement a correction method.')

    if images_generated_dir and not fix_algorithm.generation:
        raise Exception('Path for generated images is given but fix algorithm '
                        'does not implement a generation method.')

    from os import listdir, makedirs
    from os.path import isdir, join, exists
    from pyphoon.io.h5 import read_source_images, write_image
    from pyphoon.io.utils import get_image_ids, get_h5_filenames

    # Get folders
    if folders is None:
        folders = sorted([f for f in listdir(images_orig_dir) if isdir(join(
            images_orig_dir, f))])
    # Iterate over all folders
    count = 0
    for folder in folders[185:]:
        print(folder, count) if display else 0
        count += 1
        # Load images
        images = read_source_images(join(images_orig_dir, folder))
        images_ids = get_image_ids(join(images_orig_dir, folder))
        image_filenames = get_h5_filenames(join(images_orig_dir, folder))

        # Correct images using algorithm
        images_corrected, images_ids_corrected = fix_algorithm.apply(images,
                                                                     images_ids)
        # 1) Get indices of corrected images
        if images_corrected_dir:
            corrected_indices_orig = fix_algorithm.fixed_indices['original'][
                'corrected']
            corrected_indices_fix = fix_algorithm.fixed_indices['fixed'][
                'corrected']
            # Store corrected images in a original-data-like-wise folder
            # hierarchy
            for i, j in zip(corrected_indices_orig, corrected_indices_fix):
                full_path = join(images_corrected_dir, folder)
                if not exists(full_path):
                    makedirs(full_path)
                #print(" saving", folder, j)
                write_image(path_to_file=join(full_path, image_filenames[i]),
                            image=images_corrected[j])

        # 2) Get indices of generated images
        if images_generated_dir:
            generated_indices_orig = fix_algorithm.fixed_indices['original'][
                'generated']
            generated_indices_fix = fix_algorithm.fixed_indices['fixed'][
                'generated']

            # Store generated images in a original-data-like-wise folder
            # hierarchy
            for i, j in zip(generated_indices_orig, generated_indices_fix):
                full_path = join(images_generated_dir, folder)
                if not exists(full_path):
                    makedirs(full_path)
                filename_1 = images_ids_corrected[j].split('_')[1]+"-"
                filename_2 = "-".join(image_filenames[i].split("-")[1:])
                image_filename = filename_1 + filename_2
                write_image(path_to_file=join(full_path, image_filename),
                            image=images_corrected[j])

        fix_algorithm.clear()
from os import path, listdir
import pandas as pd
from os.path import isdir, join, exists
import numpy as np
from pyphoon.io.h5 import read_source_image

feature_names = ["year", "month", "day", "hour", "class", "latitude",
                 "longitude", "pressure", "wind", "gust", "storm_direc",
                 "storm_radius_major", "storm_radius_minor", "gale_direc",
                 "gale_radius_major", "gale_radius_minor", "landfall",
                 "speed", "direction", "interpolated"]


class PDManager:
    """ Class to manage and help in the analysis of the dataset. It stores
    references to the image files, dates of the data, corrected images etc.
    in pandas.DataFrame objects.

    """
    def __init__(self, compression='gzip'):
        self.besttrack = pd.DataFrame()  #: DataFrame for best track data.
        self.images = pd.DataFrame()  #: DataFrame for original image data.
        self.missing = pd.DataFrame()  #: DataFrame for missing image data.
        self.corrupted = pd.DataFrame()  #: DataFrame for corrected image data.
        self._compression = compression  #: Compression, default 'gzip'.

    ############################################################################
    # Original images
    ############################################################################
    # TODO: add_original_images
    def add_orig_images(self, images_dir, file_refs_only=True):
        """ Adds information about original images to the class attribute
        ``images``.

        :param images_dir: Path to image dataset
        :type images_dir: str
        :param file_refs_only: Set to True to only store links to the files (
            recommended. Otherwise it reads and stores the image files as well.
        :type file_refs_only: bool, default True
        """
        # Get information
        image_data = self.get_info_image_dataset(images_dir, file_refs_only)

        # Create DataFrame
        self.images = pd.concat(image_data)
        self.images.set_index(['seq_no', 'obs_time'], inplace=True,
                              drop=True, verify_integrity=True)
        self.images.index.name = 'seq_no_obs_time'

    # TODO: pkl_save_original_images
    def save_images(self, filename):
        """ Saves the class attribute ``images`` as a pickle file.

        :param filename: Path to the pickle file.
        :type filename: str
        """
        self.images.to_pickle(filename, compression=self._compression)

    # TODO: pkl_load_original_images
    def load_orig_images(self, filename):
        """ Loads the image data from a pickle file as DataFrame storing
        it as the class attribute ``images``.

        :param filename: Path to the pickle file.
        :type filename: str
        """
        self.images = pd.read_pickle(filename, self._compression)

    ############################################################################
    # Best data
    ############################################################################
    def add_besttrack(self, directory):
        """ Adds information from the best data to the class attribute
        ``besttrack``.

        :param directory: Path where source files are stored
        :return:
        """
        files = listdir(directory)
        appended_data = []
        for f in files:
            _id = int(path.splitext(f)[0])
            f = path.join(directory, f)
            frame = pd.read_csv(filepath_or_buffer=f, sep='\t',
                                names=feature_names)
            frame['seq_no'] = _id
            appended_data.append(frame)
        self.besttrack = pd.concat(appended_data)
        self.besttrack['obs_time'] = pd.to_datetime(self.besttrack.loc[:,
                                                    'year':'hour'])
        self.besttrack.drop(self.besttrack.loc[:, 'year':'hour'], axis=1,
                            inplace=True)
        self.besttrack.set_index(['seq_no', 'obs_time'], inplace=True,
                                 drop=True, verify_integrity=True)
        self.besttrack.index.name = 'seq_no_obs_time'

    # TODO: pkl_save_besttrack
    def save_besttrack(self, filename):
        """ Saves the class attribute ``besttrack`` as a pickle file.

        :param filename: Path to the pickle file.
        :type filename: str
        """
        self.besttrack.to_pickle(filename, compression=self._compression)

    # TODO: pkl_load_besttrack
    def load_besttrack(self, filename):
        """ Loads the best data from a pickle file as DataFrame storing
        it as the class attribute ``besttrack``.

        :param filename: Path to the pickle file.
        :type filename: str
        """
        self.besttrack = pd.read_pickle(filename, self._compression)

    ############################################################################
    # Corrupted images
    ############################################################################

    # TODO: add_corrupted_images
    def add_corrupted(self, images_dir, file_refs_only=True):
        """Adds information about the corrected images to the class attribute
        ``corrupted``.

        :param images_dir: Path to image dataset.
        :type images_dir: str
        :param file_refs_only: Set to True to only store links to the files (
            recommended. Otherwise it reads and stores the image files as well.
        :type file_refs_only: bool, default True
        """

        # Get information
        image_data = self.get_info_image_dataset(images_dir, file_refs_only)

        self.corrupted = pd.concat(image_data)
        self.corrupted.set_index(['seq_no', 'obs_time'], inplace=True,
                                 drop=True, verify_integrity=True)
        self.corrupted.index.name = 'seq_no_obs_time'

    # TODO: pkl_save_corrupted_images
    def save_corrupted(self, filename):
        """Saves the class attribute ``corrupted`` as a pickle file.

        :param filename: Path to the pickle file.
        :type filename: str
        """
        self.corrupted.to_pickle(filename, compression=self._compression)

    # TODO: pkl_load_corrupted_images
    def load_corrupted(self, filename):
        """Loads the corrupted data from a pickle file as DataFrame storing
        it as the class attribute ``corrupted``.

        :param filename: Path to the pickle file.
        :type filename: str
        """
        self.corrupted = pd.read_pickle(filename, self._compression)

    def add_corrected_info(self, orig_images_dir, corrected_dir):
        """ Adds information about corrected images to the corrupted dataset

        :param orig_images_dir: original images folder
        :type orig_images_dir: str
        :param corrected_dir: corrected images folder
        :type corrected_dir: str

        :raises: Exception
        """
        joined = self.images.join(self.corrupted, how='inner')
        if len(joined) == 0:
            raise Exception('Both corrupted and original tables should be '
                            'loaded first')
        if not exists(orig_images_dir) or not exists(corrected_dir):
            raise Exception('Original or Corrected images folder does not '
                            'exist')
        for key in joined.index:
            subdir, filename = joined.loc[key, ['directory', 'filename']]
            corrected_filename = join(corrected_dir, subdir, filename)
            if exists(corrected_filename):
                try:
                    src_data = read_source_image(join(orig_images_dir,
                                                      subdir, filename))
                    corrected = read_source_image(corrected_filename)
                    diff = src_data - corrected
                    diff = np.abs(diff)
                    # discard small corrections
                    diff[diff < 1] = 0
                    self.corrupted.loc[key, 'corruption'] = np.count_nonzero(
                        diff) / (diff.shape[0] * diff.shape[1])
                except IOError as detail:
                    print('Error occured while reading files: ', detail)

    ############################################################################
    # Missing images
    ############################################################################
    # TODO: add_missing_images
    def add_missing_frames(self):
        """
        Creates a dataset with missing frames information

        :raises: Exception
        """
        joined = pd.concat([self.images, self.besttrack], axis=1, join='inner')
        if len(joined) == 0:
            raise Exception('Both corrupted and original tables should be '
                            'loaded first')
        seqs = joined.groupby('seq_no')
        frame_deltas = pd.DataFrame(
            columns=['start_time', 'time_step', 'frames_num', 'missing_num',
                     'completeness', 'missing_frames',
                     'have_good_neighbours'])
        frame_deltas.index.name = 'seq_no'
        for name, group in seqs:
            diffs = pd.Series([(group.index[i + 1][1] - group.index[i][1])
                               for i in range(0, len(group.index) - 1)])
            min_diff = diffs.mode()[0]
            missing = []
            for i in range(0, len(diffs)):
                if not min_diff == diffs[i]:
                    missing.append(i + 1)
            have_good_neighbours = []
            for i in missing:
                if i - 1 not in missing and i + 1 not in missing:
                    have_good_neighbours.append(i)
            frame_deltas.loc[name] = [group.index[0][1],
                                      min_diff,
                                      len(diffs) + 1 + len(missing),
                                      len(missing),
                                      (len(diffs) + 1) / (len(diffs) + 1 +
                                                          len(missing)),
                                      missing,
                                      have_good_neighbours]
        # frame_deltas = frame_deltas[frame_deltas.missing_num > 0]
        self.missing = frame_deltas

    # TODO: pkl_missing_images
    def save_missing(self, filename):
        """Saves the class attribute ``missing`` as a pickle file.

        :param filename: Path to the pickle file.
        :type filename: str
        """
        self.missing.to_pickle(filename, compression=self._compression)

    # TODO: pkl_load_missing_images
    def load_missing(self, filename):
        """Loads the missing data from a pickle file as DataFrame storing
        it as the class attribute ``missing``.

        :param filename: Path to the pickle file.
        :type filename: str
        """
        self.missing = pd.read_pickle(filename, self._compression)

    ############################################################################
    # Others
    ############################################################################
    @staticmethod
    def get_info_image_dataset(directory, file_refs_only):
        """ Explores the image dataset in ``directory`` (assuming format
        described in section `Data <data.html>`_) and related information.

        :param directory: Directory of the dataset.
        :type directory: str
        :param file_refs_only: Set to True to only store links to the files.
            Otherwise it reads and stores the image files as well (not
            recommended).
        :type file_refs_only: bool
        :return: List containing information of each image sample as a
            DataFrame.
        :rtype: list
        """
        from os import stat
        from pyphoon.io.h5 import get_h5_filenames
        from pyphoon.io.h5 import read_source_image
        from pyphoon.io.utils import imagefilename2date

        # Get folder names within directory
        folders = sorted([f for f in listdir(directory) if isdir(join(
            directory, f))])

        # Iterate over all image files and create a DataFrame with their
        # information
        image_data = []
        # For all sequences
        for folder in folders:
            path_images = join(directory, folder)

            sequence_data = []
            # For all files within the sequence
            for filename in get_h5_filenames(path_images):
                date = imagefilename2date(filename)
                fullname = join(directory, folder, filename)
                sample_data = {'obs_time': date, 'seq_no': folder,
                               'directory': folder, 'filename': filename,
                               'size': stat(fullname).st_size}
                if file_refs_only is False:
                    img = read_source_image(fullname)
                    sample_data['image_data'] = img
                sequence_data.append(sample_data)
            # Add sequence data to main list
            image_data.append(pd.DataFrame(sequence_data))
        return image_data

    def get_obs_time_from_frame_num(self, seq_no, frame_num):
        """ Returns Timestamp object related to a missing frame (numeration
        starts from 0).

        :param seq_no: number of sequence
        :type seq_no: int
        :param frame_num: number of image in sequence
        :return:
        """
        time_shift = self.missing.get_value(index=seq_no, col='time_step') * \
                     frame_num
        return self.missing.get_value(index=seq_no, col='start_time') + \
               time_shift

    def get_image_from_seq_no_and_frame_num(self, seq_no, frame_num):
        """ Does something

        :param seq_no:
        :param frame_num:
        :return:
        """
        dt = self.get_obs_time_from_frame_num(seq_no, frame_num)
        key = (seq_no, dt)
        dir = self.images.get_value(key, 'directory')
        file = self.images.get_value(key, 'filename')
        return path.join(dir, file)

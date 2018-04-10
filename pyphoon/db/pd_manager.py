from os import path, listdir, stat
import pandas as pd
from os.path import isdir, join, exists
import numpy as np
from pyphoon.io.utils import folder2name, imagefilename2date
from pyphoon.io.h5 import read_source_image, get_h5_filenames

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
        self.missing = pd.DataFrame()  #: DataFrame for information about
        # missing images.
        self.corrected = pd.DataFrame()  #: DataFrame for corrected image data.
        self._compression = compression  #: Compression, default 'gzip'.

    ############################################################################
    # Original images
    ############################################################################
    def add_original_images(self, directory):
        """Adds information about original images to the class attribute
        **images**.

        :param directory: Path to image dataset.
        :type directory: str
        """
        appended_data = self._read_image_files_structure(directory)
        self.images = pd.concat(appended_data)
        self.images.set_index(['seq_no', 'obs_time'], inplace=True, drop=True,
                              verify_integrity=True
                              )
        self.images.index.name = 'seq_no_obs_time'

    def save_original_images(self, filename):
        """ Saves the class attribute **images** as a pickle file.

        :param filename: Path to the pickle file.
        :type filename: str
        """
        self.images.to_pickle(filename, compression=self._compression)

    def load_original_images(self, filename):
        """ Loads the image data from a pickle file as DataFrame storing
        it as the class attribute **images**.

        :param filename: Path to the pickle file.
        :type filename: str
        """
        self.images = pd.read_pickle(filename, self._compression)

    ############################################################################
    # Best data
    ############################################################################
    def add_besttrack(self, directory):
        """ Adds information from the best data to the class attribute
        **besttrack**.

        :param directory: Path where source files are stored
        :type directory: str
        """
        files = listdir(directory)
        appended_data = []
        for f in files:
            _id = int(path.splitext(f)[0])
            f = path.join(directory, f)
            frame = pd.read_csv(filepath_or_buffer=f, sep='\t', names=feature_names)
            frame['seq_no'] = _id
            appended_data.append(frame)
        self.besttrack = pd.concat(appended_data)
        self.besttrack['obs_time'] = pd.to_datetime(self.besttrack.loc[:,
                                                    'year':'hour'])
        self.besttrack.drop(self.besttrack.loc[:, 'year':'hour'], axis=1,
                            inplace=True
                            )
        self.besttrack.set_index(['seq_no', 'obs_time'], inplace=True,
                                 drop=True, verify_integrity=True
                                 )
        self.besttrack.index.name = 'seq_no_obs_time'

    def save_besttrack(self, filename):
        """ Saves the class attribute **besttrack** as a pickle file.

        :param filename: Path to the pickle file.
        :type filename: str
        """
        self.besttrack.to_pickle(filename, compression=self._compression)

    def load_besttrack(self, filename):
        """ Loads the best data from a pickle file as DataFrame storing
        it as the class attribute **besttrack**.

        :param filename: Path to the pickle file.
        :type filename: str
        """
        self.besttrack = pd.read_pickle(filename, self._compression)

    ############################################################################
    # Corrected
    ############################################################################
    def add_corrected_images(self, directory):
        """Adds information about the corrected images to the class attribute
        **corrected**.

        :param directory: Path to image dataset.
        :type directory: str
        """

        appended_data = self._read_image_files_structure(directory)
        self.corrected = pd.concat(appended_data)
        self.corrected.set_index(['seq_no', 'obs_time'], inplace=True,
                                 drop=True, verify_integrity=True)
        self.corrected.index.name = 'seq_no_obs_time'

    def save_corrected_images(self, filename):
        """Saves the class attribute **corrected** as a pickle file.

        :param filename: Path to the pickle file.
        :type filename: str
        """

        self.corrected.to_pickle(filename, compression=self._compression)

    def load_corrected_images(self, filename):
        """Loads the corrupted data from a pickle file as DataFrame storing
        it as the class attribute **corrected**.

        :param filename: Path to the pickle file.
        :type filename: str
        """

        self.corrected = pd.read_pickle(filename, self._compression)

    def add_corrected_info(self, orig_images_dir, corrected_dir):
        """
        Adds information about corrected images to the corrected dataset.

        :param orig_images_dir: original images folder.
        :type orig_images_dir: str
        :param corrected_dir: corrected images folder.
        :type corrected_dir: str

        :raises: Exception
        """

        if not exists(orig_images_dir) or not exists(corrected_dir):
            raise Exception('Original or Corrected images folder does not '
                            'exist')
        for key in self.corrected.index:
            subdir, filename = self.corrected.loc[key, ['directory',
                                                        'filename']]
            corrected_filename = join(corrected_dir, subdir, filename)
            try:
                src_data = read_source_image(join(orig_images_dir, subdir,
                                                  filename))
                corrected = read_source_image(corrected_filename)
                diff = src_data - corrected
                diff = np.abs(diff)
                # discard small corrections
                diff[diff < 1] = 0
                self.corrected.loc[key, 'corruption'] = np.count_nonzero(
                    diff) / (diff.shape[0] * diff.shape[1])
            except IOError as detail:
                print('Error occured while reading files: ', detail)

    ############################################################################
    # Missing frames
    ############################################################################
    def add_missing_images_info(self):
        """
        Creates a dataset with information about missing images.

        :raises: Exception
        """
        joined = pd.concat([self.images, self.besttrack], axis=1, join='inner')
        if len(joined) == 0:
            raise Exception('Both besttrack and original tables should be'
                            'loaded first')
        seqs = joined.groupby('seq_no')
        frame_deltas = pd.DataFrame(
            columns=['start_time', 'time_step', 'frames_num', 'missing_num',
                     'completeness', 'missing_frames',
                     'have_good_neighbours'])
        frame_deltas.index.name = 'seq_no'
        for name, group in seqs:
            diffs = pd.Series([(group.index[i + 1][1] - group.index[i][1]) for
                               i in range(0, len(group.index) - 1)])
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
            # store information about frames in images dataframe
            # frames = list(range(0, frame_deltas.loc[name, 'frames_num']))
            # frames = [frame for frame in frames if frame not in frame_
            # deltas.loc[name, 'missing_frames']]
            # self.images.loc[name, 'frame'] = frames
        # frame_deltas = frame_deltas[frame_deltas.missing_num > 0]
        self.missing = frame_deltas

    def save_missing_images(self, filename):
        """ Saves Missing DataFrame to a file.

        :param filename: Path to the pickle file.
        :type filename: str
        """
        self.missing.to_pickle(filename, compression=self._compression)

    def load_missing_images_info(self, filename):
        """ Loads Missing DataFrame from a file.

        :param filename: Path to the pickle file.
        :type filename: str
        """
        self.missing = pd.read_pickle(filename, self._compression)

    def add_frames(self):
        """ Adds frames numbers to the original images DataFrame. Both original
        images and missing DataFrames should be loaded.

        :raises: Exception
        """
        union = set(self.missing.index).union(
            self.images.index.get_level_values(0).unique())
        if len(union) == 0 or len(union) != len(
                self.images.index.get_level_values(0).unique()):
            raise Exception('Both original and missing dataframes should be '
                            'loaded first')
        for seq_no in self.missing.index:
            missing_frames = self.missing.loc[seq_no, 'missing_frames']
            frame_nums = len(self.images.loc[seq_no]) + len(missing_frames)
            frames = list(range(0, frame_nums))
            frames = [frame for frame in frames if frame not in missing_frames]
            self.images.loc[seq_no, 'frame'] = frames


    ############################################################################
    # Others
    ############################################################################
    def _read_image_files_structure(self, directory):
        folders = sorted([f for f in listdir(directory) if isdir(join(
            directory, f))])
        appended_data = []
        for folder in folders:
            path_images = join(directory, folder)
            seq_name = int(folder2name(path_images))
            # frame = pd.DataFrame(columns=['obs_time', 'seq_no', 'directory',
            # 'filename', 'size'])
            image_data = []
            for f in get_h5_filenames(path_images):
                date = imagefilename2date(f)
                fullname = join(directory, folder, f)
                data = {'obs_time': date, 'seq_no': seq_name, 'directory':
                    folder, 'filename': f, 'size': stat(fullname).st_size}
                image_data.append(data)
            frame = pd.DataFrame(image_data)
            appended_data.append(frame)
        return appended_data

    def get_obs_time_from_frame_num(self, seq_no, frame_num):
        """ Returns Timestamp object related to a missing frame (numeration
        starts from 0).

        :param seq_no: number of sequence.
        :type seq_no: str
        :param frame_num: number of image in sequence
        :type frame_num: int
        :return:
        """
        time_shift = self.missing.get_value(index=seq_no, col='time_step') * \
                     frame_num
        return self.missing.get_value(index=seq_no, col='start_time') + \
               time_shift

    def get_image_from_seq_no_and_frame_num(self, seq_no, frame_num):
        """

        :param seq_no: number of sequence.
        :type seq_no: str
        :param frame_num: number of image in sequence
        :type frame_num: int
        :return:
        """
        dt = self.get_obs_time_from_frame_num(seq_no, frame_num)
        key = (seq_no, dt)
        dir = self.images.get_value(key, 'directory')
        file = self.images.get_value(key, 'filename')
        return path.join(dir, file)

import os
from os import path, listdir
import pandas as pd
from os.path import isdir, join, exists

import time

from pyphoon.clean.correction import correct_corrupted_pixels_1
from pyphoon.clean.detection import detect_corrupted_pixels_1
from pyphoon.clean.fix import TyphoonListImageFixAlgorithm
from pyphoon.clean.fillgaps import generate_new_frames_1
from pyphoon.io.typhoonlist import create_typhoonlist_from_source
from pyphoon.io.utils import id2date, id2seqno
from pyphoon.io.h5 import write_image

feature_names = ["year", "month", "day", "hour", "class", "latitude",
                 "longitude", "pressure", "wind", "gust", "storm_direc",
                 "storm_radius_major", "storm_radius_minor", "gale_direc",
                 "gale_radius_major", "gale_radius_minor", "landfall",
                 "speed", "direction", "interpolated"]


class PDManager:
    def __init__(self, compression='gzip'):
        self.besttrack = pd.DataFrame()
        self.images = pd.DataFrame()
        self.missing = pd.DataFrame()
        self.corrupted = pd.DataFrame()
        self._compression = compression

    def add_besttrack(self, directory):
        """
        Add besttrack information to the database
        :param directory: Path where source files are stored
        :return:
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
        self.besttrack['obs_time'] = pd.to_datetime(self.besttrack.loc[:, 'year':'hour'])
        self.besttrack.drop(self.besttrack.loc[:, 'year':'hour'], axis=1, inplace=True)
        self.besttrack.set_index(['seq_no', 'obs_time'], inplace=True, drop=True, verify_integrity=True)
        self.besttrack.index.name = 'seq_no_obs_time'

    def save_besttrack(self, filename):
        """
        Saves Besttrack DataFrame to a file
        :param filename:
        :return:
        """
        self.besttrack.to_pickle(filename, compression=self._compression)

    def load_besttrack(self, filename):
        """
        Loads BestTrack DataFrame from a file
        :param filename:
        :return:
        """
        self.besttrack = pd.read_pickle(filename, self._compression)

    def add_orig_images(self, directory, file_refs_only=True):
        """
        Add information about original images to the DataFrame
        :param directory:
        :param file_refs_only: if set True, only links to the files will be stored
        :return:
        """
        from os import stat
        from pyphoon.io.h5 import get_h5_filenames
        from pyphoon.io.h5 import read_source_image
        from pyphoon.io.utils import folder_2_name, get_image_date
        folders = sorted([f for f in listdir(directory) if isdir(join(directory, f))])
        appended_data = []
        for folder in folders:
            path_images = join(directory, folder)
            seq_name = int(folder_2_name(path_images))
            # frame = pd.DataFrame(columns=['obs_time', 'seq_no', 'directory', 'filename', 'size'])
            image_data = []
            for f in get_h5_filenames(path_images):
                date = get_image_date(f)
                fullname = join(directory, folder, f)
                data = {'obs_time': date, 'seq_no': seq_name, 'directory': folder,
                        'filename': f, 'size': stat(fullname).st_size}
                if file_refs_only is False:
                    img = read_source_image(fullname)
                    data['image_data'] = img
                image_data.append(data)
            frame = pd.DataFrame(image_data)
            appended_data.append(frame)
        self.images = pd.concat(appended_data)
        self.images.set_index(['seq_no', 'obs_time'], inplace=True, drop=True, verify_integrity=True)
        self.images.index.name = 'seq_no_obs_time'

    def save_images(self, filename):
        """
        Saves Images DataFrame to a file
        :param filename:
        :return:
        """
        self.images.to_pickle(filename, compression=self._compression)

    def load_images(self, filename):
        """
        Loads Images DataFrame from a file
        :param filename:
        :return:
        """
        self.images = pd.read_pickle(filename, self._compression)

    def add_corrupted(self, images_dir, save_corrected_to=None):
        if save_corrected_to:
            if os.path.isabs(save_corrected_to) is False:
                save_corrected_to = path.join(os.getcwd(), save_corrected_to)
            if not exists(save_corrected_to):
                os.mkdir(save_corrected_to)

        folders = sorted([f for f in listdir(images_dir) if isdir(join(images_dir, f))])
        appended_data = []
        for folder in folders:
            # Create TyphoonList
            seq = create_typhoonlist_from_source(
                name=folder,
                images=join(images_dir, folder)
            )
            # Fix TyphoonList
            detect_fct = detect_corrupted_pixels_1  # Detection method
            correct_fct = correct_corrupted_pixels_1  # Correction method
            detect_params = {'min_th': 160, 'max_th': 310}  # Parameters for detection meth
            # Generation
            fillgaps_fct = generate_new_frames_1  # Fill gap method
            n_frames_th = 2  # Maximum number of frames to generate

            fix_algorithm = TyphoonListImageFixAlgorithm(
                detect_fct=detect_fct,
                correct_fct=correct_fct,
                fillgaps_fct=fillgaps_fct,
                detect_params=detect_params,
                n_frames_th=n_frames_th
            )

            seq_new = fix_algorithm.apply(seq)
            corrected = fix_algorithm.fixed_ids['corrected']
            seq = []
            for img in corrected:
                seqno = id2seqno(img)
                obstime = id2date(img)
                data = {'obs_time': obstime, 'seq_no': seqno, 'corrupted': img}
                seq.append(data)
                if save_corrected_to is not None:
                    key = (seqno, obstime)
                    filename, directory = self.images.loc[key, ['filename', 'directory']]
                    full_path = join(save_corrected_to, directory)
                    if not exists(full_path):
                        os.mkdir(full_path)
                    full_path = join(full_path, filename)
                    write_image(path_to_file=full_path, image=seq_new.get_data(key='images', id=img))
            frame = pd.DataFrame(seq)
            appended_data.append(frame)

        self.corrupted = pd.concat(appended_data)
        self.corrupted.set_index(['seq_no', 'obs_time'], inplace=True, drop=True, verify_integrity=True)
        self.corrupted.index.name = 'seq_no_obs_time'

    def save_corrupted(self, filename):
        self.corrupted.to_pickle(filename, compression=self._compression)

    def load_corrupted(self, filename):
        """
        Loads Corrupted DataFrame from a file
        :param filename:
        :return:
        """
        self.corrupted = pd.read_pickle(filename, self._compression)

    def add_missing_frames(self):
        # from pandas import groupby
        joined = pd.concat([self.images, self.besttrack], axis=1, join='inner')
        seqs = joined.groupby('seq_no')
        frame_deltas = pd.DataFrame(
            columns=['start_time', 'time_step', 'frames_num', 'missing_num', 'completeness', 'missing_frames',
                     'have_good_neighbours'])
        frame_deltas.index.name = 'seq_no'
        for name, group in seqs:
            diffs = pd.Series([(group.index[i + 1][1] - group.index[i][1]) for i in range(0, len(group.index) - 1)])
            min_diff = diffs.min()
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
                                      len(diffs) + 1,
                                      len(missing),
                                      (len(diffs) + 1 - len(missing)) / (len(diffs) + 1),
                                      missing,
                                      have_good_neighbours]
        # frame_deltas = frame_deltas[frame_deltas.missing_num > 0]
        self.missing = frame_deltas

    def save_missing(self, filename):
        """
        Saves Missing DataFrame to a file
        :param filename:
        :return:
        """
        self.missing.to_pickle(filename, compression=self._compression)

    def load_missing(self, filename):
        """
        Loads Missing DataFrame from a file
        :param filename:
        :return:
        """
        self.missing = pd.read_pickle(filename, self._compression)

    def get_obs_time_from_frame_num(self, seq_no, frame_num):
        """
        Returns Timestamp object related to a missing frame (numeration starts from 0)
        :param seq_no: number of sequence
        :param frame_num: number of image in sequence
        :return:
        """
        time_shift = self.missing.get_value(index=seq_no, col='time_step') * frame_num
        return self.missing.get_value(index=seq_no, col='start_time') + time_shift

    def get_image_from_seq_no_and_frame_num(self, seq_no, frame_num):
        dt = self.get_obs_time_from_frame_num(seq_no, frame_num)
        key = (seq_no, dt)
        dir = self.images.get_value(key, 'directory')
        file = self.images.get_value(key, 'filename')
        return path.join(dir, file)

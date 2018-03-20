import pandas as pd
from os.path import exists, isdir, join
import os
from pyphoon.io.h5 import read_source_image, write_h5_dataset_file
from pyphoon.db.pd_manager import PDManager
import time


class DataExtractor:
    """
    Data extractor. Operates with DataFrames, created by PDManager.
    """

    def __init__(self, original_images_dir, corrected_images_dir, pd_manager):
        """
        Constructor

        :param original_images_dir: Original images directory
        :param corrected_images_dir: Corrected images directory
        :param pd_manager: PDManager object
        :type pd_manager: pyphoon.db.PDManager
        """
        self.original_images_dir = original_images_dir
        self.corrected_images_dir = corrected_images_dir
        self.pd_man = pd_manager

    def get_good_triplets(self, seq_no, allow_corrected=True):
        """
        Gets triplets of frames (3 subsequent frames) from a given sequence, where non of frames is missing

        :param seq_no: Number of sequence (ID)
        :type seq_no: int
        :param allow_corrected: Allow including corrected images into triplets
        :type allow_corrected: bool
        """

    # TODO: read corrected/generated as optional
    def _read_seq(self, seq_no, preprocess_algorithm=None):
        """
        Disclaimer: Dont read this code

        :param seq_no:
        :param preprocess_algorithm:
        :return:
        """
        images = self.pd_man.images
        besttrack = self.pd_man.besttrack
        corrected = self.pd_man.corrected
        if images.empty or besttrack.empty:
            raise Exception('Images and Besttrack dataframes should be loaded')
        read_data = []
        size = 0
        seq = images.loc[seq_no]
        for obs_time, frame in seq.iterrows():
            index = (seq_no, obs_time)
            if corrected.index.contains(index):
                corrected_entry = corrected.loc[index]
                size += corrected_entry['size']
                data = read_source_image(join(self.corrected_images_dir, corrected_entry.directory, corrected_entry.filename))
                if preprocess_algorithm:
                    data = preprocess_algorithm(data.reshape(1, data.shape[0],
                                                             data.shape[1]))[0]
            else:
                size += frame['size']
                data = read_source_image(join(self.original_images_dir, frame.directory, frame.filename))
                if preprocess_algorithm:
                    data = preprocess_algorithm(data.reshape(1, data.shape[0],
                                                             data.shape[1]))[0]
            read_data.append([seq_no, obs_time, data])
        pd_read_data = pd.DataFrame(data=read_data, columns=['seq_no', 'obs_time', 'data'])
        pd_read_data.set_index(['seq_no', 'obs_time'], drop=True, inplace=True)
        pd_read_data = pd_read_data.join(besttrack)
        return pd_read_data, size

    def generate_images_shuffled_chunks(self, images_per_chunk, output_dir,
                                        seed=0, preprocess_algorithm=None,
                                        display=False):
        """
        Generates chunks of hdf5 files, containing shuffled images from different sequences and besttrack data

        :param images_per_chunk: number inages per chunk
        :param output_dir: Output dir
        :param seed: seed for random shuffle
        :param preprocess_algorithm: Algorithm for data preprocessing, which returns data of the same shape as an input
        :param display: flag for displaying output
        """
        pd_manager = self.pd_man
        images = pd_manager.images
        corrected = pd_manager.corrected
        besttrack = pd_manager.besttrack
        self._parameter_checking(corrected, images, output_dir)
        filenames = self.get_full_filenames_prefer_corrected()
        united_data = besttrack.join(filenames, how='inner')
        i = 0
        while len(united_data.index) > 0:
            shuffled = united_data.sample(n=min(images_per_chunk, len(united_data.index)), random_state=seed)
            shuffled['data'] = pd.Series()
            for index, row in shuffled.iterrows():
                data = read_source_image(row.full_filename)
                if preprocess_algorithm:
                    data = preprocess_algorithm(data.reshape(1, data.shape[0],
                                                             data.shape[1]))[0]
                row['data'] = data
            print("writing chunk {0}".format(i)) if display else 0
            self._write_chunk(join(output_dir, '{0}_chunk.h5'.format(i)), [shuffled])
            i += 1
            united_data.drop(shuffled.index, inplace=True)

    def get_full_filenames_prefer_corrected(self):
        """
        Get full_path series, preferring entries from the corrected df

        """
        original = self.pd_man.images
        corrected = self.pd_man.corrected

        original_full_paths = original.apply(lambda row: join(self.original_images_dir,
                                                                row['directory'], row['filename']), axis=1)
        corrected_full_paths = corrected.apply(lambda row: join(self.corrected_images_dir, row['directory'],
                                                                  row['filename']), axis=1)
        corrected_full_paths = corrected_full_paths.combine_first(original_full_paths)
        corrected_full_paths.name = 'full_filename'
        return corrected_full_paths

    def generate_images_besttrack_chunks(self, sequence_list, chunk_size, output_dir,
                                         preprocess_algorithm=None,
                                         display=False):
        """
        Generates chunks of hdf5 files, containing images and besttrack data

        :param sequence_list: List of tuples [(seq_no, prefix), ...]
        :type sequence_list: list
        :param chunk_size: Size of chunks in bytes
        :type chunk_size: int
        :param output_dir: Output dir
        :type output_dir: str
        :param preprocess_algorithm: Algorithm for data preprocessing, which returns data of the same shape as an input
        """
        # Parameters checking
        pd_manager = self.pd_man
        assert isinstance(pd_manager, PDManager)
        assert isinstance(sequence_list, list)
        assert isinstance(chunk_size, int)

        images = pd_manager.images
        corrected = pd_manager.corrected
        self._parameter_checking(corrected, images, output_dir)

        # group by prefix
        sequences = pd.DataFrame(sequence_list, columns=['seq_no', 'prefix'])
        chunk = []
        size = 0
        _filename = ''
        for prefix, data in sequences.groupby('prefix'):
            print(prefix)
            serial_num = 0
            for entry in data.iterrows():
                _seq_no = entry[1].seq_no
                print("",_seq_no) if display else 0
                data, seq_size = self._read_seq(seq_no=_seq_no,
                                                preprocess_algorithm=preprocess_algorithm)
                chunk.append(data)
                size += seq_size
                if size >= chunk_size:
                    # write chunk to disk
                    _filename = join(output_dir, '{0}_{1}.h5'.format(prefix, serial_num))
                    print(" --> storing", _filename) if display else 0
                    t0 = time.time()
                    self._write_chunk(filename=_filename, chunk=chunk)
                    print(" --> done in", time.time()-t0) if display else 0
                    serial_num += 1
                    size = 0
                    chunk = []
            if not len(chunk) == 0:
                # write leftovers
                _filename = join(output_dir, '{0}_{1}.h5'.format(prefix, serial_num))
                print(" --> storing", _filename) if display else 0
                t0 = time.time()
                self._write_chunk(filename=_filename, chunk=chunk)
                print(" --> done in", time.time() - t0) if display else 0

    def _parameter_checking(self, corrupted, images, output_dir):
        if images.empty:
            raise Exception('Images DataFrame should be created')
        if not isdir(self.original_images_dir):
            raise NotADirectoryError(self.original_images_dir + ' is not a directory')
        if not exists(output_dir):
            os.mkdir(output_dir)
        if self.corrected_images_dir is not None:
            if not isdir(self.corrected_images_dir):
                raise NotADirectoryError(self.corrected_images_dir + ' is not a directory')
            if corrupted.empty:
                raise Exception('Corrupted DataFrame should be created when corrected_dir is not None')

    def _write_chunk(self, filename, chunk):
        """
        Writing chunk of data to hdf5 file routine.

        :param filename: Output filename.
        :type filename: str
        :param chunk: Input chunk of data.
        :type chunk: list of pd.DataFrame
        """

        print(chunk)
        united = pd.concat(chunk, axis=0)
        united.reset_index(inplace=True)

        def get_id(dt, seq):
            return str(seq) + '_' + dt.strftime("%Y%m%d%H")

        united['idx'] = united.apply(lambda x: get_id(x['obs_time'], x['seq_no']), axis=1)
        # united.drop(['obs_time', 'seq_no'], inplace=True, axis=1)
        data = {}
        data['pressure'] = united['pressure'].tolist()
        data['data'] = united['data'].tolist()
        data['seq_no'] = united['seq_no']
        data['idx'] = united['idx'].tolist()
        data['class'] = united['class'].tolist()
        # for column in united.columns:
        #     dict[column] = united[column]
        # dict['seq_no'] = united['seq_no']
        # dict['data'] = united['data']

        write_h5_dataset_file(data, filename, compression='gzip')
        # store = pd.HDFStore(filename, mode='w')
        # for col in united.columns:
        #     store.put(col, united[col])
        # store.close()
        # don't know if i need to call flush() here or not

    def read_seq(self, seq_no, features, preprocess_algorithm=None):
        from pyphoon.io.utils import date2id

        if isinstance(seq_no, str):
            seq_no = int(seq_no)
        data, _ = self._read_seq(seq_no, preprocess_algorithm)
        images = data['data'].tolist()
        images_ids = [date2id(o[1], str(o[0])) for o in data.index.tolist()]

        features_data = {}
        for feature in features:
            features_data[feature] = data[feature].tolist()

        return images, images_ids, features_data
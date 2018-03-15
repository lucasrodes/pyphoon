import pandas as pd
from os.path import exists, isdir, join
import os
from pyphoon.io.h5 import read_source_image, write_h5_dataset_file
from pyphoon.db.pd_manager import PDManager


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

    def _read_seq(self, seq_no):
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
            else:
                size += frame['size']
                data = read_source_image(join(self.original_images_dir, frame.directory, frame.filename))
            read_data.append([seq_no, obs_time, data])
        pd_read_data = pd.DataFrame(data=read_data, columns=['seq_no', 'obs_time', 'data'])
        pd_read_data.set_index(['seq_no', 'obs_time'], drop=True, inplace=True)
        pd_read_data = pd_read_data.join(besttrack)
        return pd_read_data, size

    def generate_images_besttrack_chunks(self, sequence_list, chunk_size, output_dir,
                                         preprocess_algorithm=None):
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
        corrupted = pd_manager.corrected

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
        # group by prefix
        sequences = pd.DataFrame(sequence_list, columns=['seq_no', 'prefix'])
        chunk = []
        size = 0
        _filename = ''
        for prefix, data in sequences.groupby('prefix'):
            serial_num = 0
            for entry in data.iterrows():
                _seq_no = entry[1].seq_no
                data, seq_size = self._read_seq(seq_no=_seq_no)
                if preprocess_algorithm:
                    data = preprocess_algorithm(data)
                chunk.append(data)
                size += seq_size
                if size >= chunk_size:
                    # write chunk to disk
                    _filename = join(output_dir, '{0}_{1}.h5'.format(prefix, serial_num))
                    self._write_chunk(filename=_filename, chunk=chunk)
                    serial_num += 1
                    size = 0
                    chunk = []
            if not len(chunk) == 0:
                # write leftovers
                _filename = join(output_dir, '{0}_{1}.h5'.format(prefix, serial_num))
                self._write_chunk(filename=_filename, chunk=chunk)

    def _write_chunk(self, filename, chunk):
        """
        Writing chunk of data to hdf5 file routine.

        :param filename: Output filename.
        :type filename: str
        :param chunk: Input chunk of data.
        :type chunk: list of pd.DataFrame
        """

        united = pd.concat(chunk, axis=0)
        united.reset_index(inplace=True)

        def get_id(dt, seq):
            return str(seq) + '_' + dt.strftime("%Y%m%d%H")

        united['idx'] = united.apply(lambda x: get_id(x['obs_time'], x['seq_no']), axis=1)
        # united.drop(['obs_time', 'seq_no'], inplace=True, axis=1)
        dict = {}
        dict['pressure'] = united['pressure'].tolist()
        dict['data'] = united['data'].tolist()
        dict['seq_no'] = united['seq_no']
        dict['idx'] = united['idx'].tolist()
        # for column in united.columns:
        #     dict[column] = united[column]
        # dict['seq_no'] = united['seq_no']
        # dict['data'] = united['data']

        write_h5_dataset_file(dict, filename, compression='gzip')
        # store = pd.HDFStore(filename, mode='w')
        # for col in united.columns:
        #     store.put(col, united[col])
        # store.close()
        # don't know if i need to call flush() here or not



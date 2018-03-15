import unittest
from os.path import join, exists, isdir
import shutil
from os import rmdir
from pyphoon.db.data_extractor import DataExtractor
from pyphoon.db.pd_manager import PDManager
import numpy as np
import h5py

class TestDataExtractorMethods(unittest.TestCase):

    def setUp(self):
        sample_dir = '../../../sampledata/datasets/'
        self.images_dir = join(sample_dir, 'image')
        self.corrected_dir = join(sample_dir, 'corrected')
        self.best_dir = join(sample_dir, 'jma')
        self.db_dir = '../../../../../database/'

    def test_read_seq(self):
        pd_man = PDManager()
        pd_man.load_original_images(join(self.db_dir, 'images.pkl'))
        pd_man.load_besttrack(join(self.db_dir, 'besttrack.pkl'))
        de = DataExtractor(self.images_dir, self.corrected_dir, pd_man)
        seq_no = 198702
        data1, size1 = de._read_seq(seq_no=seq_no)
        pd_man.load_corrected_images(join(self.db_dir, 'corrected.pkl'))
        data2, size2 = de._read_seq(seq_no=seq_no)
        self.assertEqual(np.shape(data1), np.shape(data2))
        self.assertNotEqual(size1, size2)

    def test_generate_images_besttrack_chunks(self):
        pd_man = PDManager()
        pd_man.load_original_images(join(self.db_dir, 'images.pkl'))
        pd_man.load_besttrack(join(self.db_dir, 'besttrack.pkl'))
        pd_man.load_corrected_images(join(self.db_dir, 'corrected.pkl'))
        de = DataExtractor(self.images_dir, self.corrected_dir, pd_man)
        output_dir = 'output'
        seq_list = [(198702, 'train'), (200717, 'train'), (200718, 'test')]
        de.generate_images_besttrack_chunks(pd_man, seq_list, chunk_size=1024 ** 2,
                                            output_dir=output_dir)
        f = h5py.File(join(output_dir, 'test_0.h5'), 'r')
        keys = f.keys()
        self.assertTrue('seq_no' in keys)
        self.assertTrue('data' in keys)
        self.assertTrue('pressure' in keys)
        self.assertEqual(len(f.get('seq_no')), len(f.get('pressure')))
        if exists(output_dir):
            shutil.rmtree(output_dir, ignore_errors=True)

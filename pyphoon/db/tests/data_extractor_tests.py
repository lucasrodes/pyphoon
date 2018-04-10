import unittest
from os.path import join, exists, isdir
import shutil
from os import rmdir, mkdir, listdir, remove
from pyphoon.db.data_extractor import DataExtractor
from pyphoon.db.pd_manager import PDManager
import numpy as np
import pandas as pd
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
        # seq_list = []
        seq_list = [(198702, 'train'), (200717, 'train'), (200718, 'test')]
        de.generate_images_besttrack_chunks(seq_list, chunk_size=1024 ** 2,
                                            output_dir=output_dir)
        f = h5py.File(join(output_dir, 'test_0.h5'), 'r')
        keys = f.keys()
        self.assertTrue('seq_no' in keys)
        self.assertTrue('data' in keys)
        self.assertTrue('pressure' in keys)
        self.assertEqual(len(f.get('seq_no')), len(f.get('pressure')))
        if exists(output_dir):
            shutil.rmtree(output_dir, ignore_errors=True)

    def test_get_full_filenames(self):
        pd_man = PDManager()
        pd_man.load_original_images(join(self.db_dir, 'images.pkl'))
        pd_man.load_besttrack(join(self.db_dir, 'besttrack.pkl'))
        pd_man.load_corrected_images(join(self.db_dir, 'corrected.pkl'))
        de = DataExtractor(self.images_dir, self.corrected_dir, pd_man)
        full_paths = de.get_full_filenames(use_corrected=True)
        self.assertTrue(len(full_paths.loc[full_paths.str.contains(self.images_dir)]) > 0)
        self.assertTrue(len(full_paths.loc[full_paths.str.contains(self.corrected_dir)]) > 0)
        full_paths_only_not_corrected = de.get_full_filenames(use_corrected=False)
        self.assertGreater(len(full_paths), len(full_paths_only_not_corrected))
        self.assertTrue(len(full_paths_only_not_corrected.loc[
                                full_paths_only_not_corrected.str.contains(self.images_dir)]) > 0)
        self.assertTrue(len(full_paths_only_not_corrected.loc[
                                full_paths_only_not_corrected.str.contains(self.corrected_dir)]) == 0)

    def test_generate_images_shuffled_chunks(self):
        pd_man = PDManager()
        pd_man.add_original_images(self.images_dir)
        pd_man.load_besttrack(join(self.db_dir, 'besttrack.pkl'))
        pd_man.add_corrected_images(self.corrected_dir)
        de = DataExtractor(self.images_dir, self.corrected_dir, pd_man)
        output_dir = 'output'
        if not exists(output_dir):
            mkdir(output_dir)
        else:
            shutil.rmtree(output_dir, ignore_errors=True)
            mkdir(output_dir)
        self.assertFalse(listdir(output_dir))
        de.generate_images_shuffled_chunks(200, output_dir)
        generated_files = listdir(output_dir)
        self.assertTrue(generated_files)
        data_samples = 0
        for f in generated_files:
            read = h5py.File(join(output_dir, f), 'r')
            data = read.get('data')
            np_data = np.array(data)
            self.assertFalse(np.isnan(np_data).any())
            data_samples += len(data)
            read.close()
        # not including corrected
        shutil.rmtree(output_dir, ignore_errors=True)
        if not exists(output_dir):
            mkdir(output_dir)
        de.generate_images_shuffled_chunks(200, output_dir, use_corrected=False)
        generated_files = listdir(output_dir)
        self.assertTrue(generated_files)
        data_samples_only_not_corrected = 0
        for f in generated_files:
            read = h5py.File(join(output_dir, f), 'r')
            data = read.get('data')
            np_data = np.array(data)
            self.assertFalse(np.isnan(np_data).any())
            data_samples_only_not_corrected += len(data)
            read.close()
        self.assertGreater(data_samples, data_samples_only_not_corrected)
        not_corrected_num = len(pd_man.images.index) - len(pd_man.corrected.index)
        self.assertTrue(data_samples_only_not_corrected == not_corrected_num)
        shutil.rmtree(output_dir, ignore_errors=True)

    def test_get_good_triplets(self):
        pd_man = PDManager()
        pd_man.load_original_images(join(self.db_dir, 'images.pkl'))
        self.assertTrue(pd_man.images.columns.contains('frame'))
        de = DataExtractor(self.images_dir, self.corrected_dir, pd_man)
        seq_no = 198702
        # missing frames are [19, 21, 40, 149]
        triplets = de.get_good_triplets(seq_no=seq_no, dataframe=pd_man.images)
        total_triplets = len(pd_man.images.loc[seq_no])
        self.assertFalse(len(triplets.index) == total_triplets - 4 * 3)
        for item in triplets.iteritems():
            self.assertIn(item, pd_man.images.index)

    def test_read_triplet_data(self):
        pd_man = PDManager()
        pd_man.add_original_images(self.images_dir)
        pd_man.add_corrected_images(self.corrected_dir)
        pd_man.add_besttrack(self.best_dir)
        pd_man.add_missing_images_info()
        pd_man.add_frames()
        de = DataExtractor(self.images_dir, self.corrected_dir, pd_man)
        triplets_ds = de.get_good_triplets(pd_man.images)
        self.assertIsInstance(triplets_ds, pd.DataFrame)
        filenames = de.get_full_filenames(True)
        chunk = de._read_triplet_data(triplets=triplets_ds, full_filenames=filenames)
        self.assertEquals(len(chunk), len(triplets_ds.index))



if __name__ == '__main__':
    unittest.main()

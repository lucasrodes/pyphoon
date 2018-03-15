import unittest

from os.path import join, exists
import shutil
from pyphoon.db.pd_manager import PDManager
import os
from pyphoon.clean_satellite.correction import correct_corrupted_pixels_1
from pyphoon.clean_satellite.detection import detect_corrupted_pixels_1
from pyphoon.clean_satellite.generation import generate_new_frames_1
from pyphoon.clean_satellite.fix import TyphoonListImageFixAlgorithm


class TestPdManagerMethods(unittest.TestCase):

    def setUp(self):
        self.fix_algorithm = TyphoonListImageFixAlgorithm(
            detect_fct=detect_corrupted_pixels_1,
            correct_fct=correct_corrupted_pixels_1,
            generate_fct=generate_new_frames_1,
            detect_params={'min_th': 160, 'max_th': 310},
            n_frames_th=2
        )
        self.images_dir = '../../../sampledata/datasets/image'
        self.corrected_dir = '../../../sampledata/datasets/corrected'
        self.best_dir = '../../../sampledata/datasets/jma'


    def test_add_besttrack(self):
        temp_db = 'temp.pkl'
        if os.path.exists(temp_db):
            os.remove(temp_db)
        self.assertFalse(os.path.exists(temp_db), 'file should not exist before execution of the method')
        manager = PDManager()
        self.assertTrue(manager.besttrack.empty)
        manager.add_besttrack(self.best_dir)
        self.assertFalse(manager.besttrack.empty)
        self.assertEqual(manager.besttrack.index.name, 'seq_no_obs_time')

    def test_save_besttrack(self):
        temp_db = 'temp.pkl'
        if os.path.exists(temp_db):
            os.remove(temp_db)
        self.assertFalse(os.path.exists(temp_db), 'file should not exist before execution of the method')
        manager = PDManager()
        manager.add_besttrack(self.best_dir)
        manager.save_besttrack(temp_db)
        self.assertTrue(os.path.exists(temp_db))
        os.remove(temp_db)

    def test_add_orig_images(self):
        images_dir = self.images_dir
        manager = PDManager()
        self.assertTrue(manager.images.empty)
        manager.add_original_images(images_dir)
        self.assertFalse(manager.images.empty)
        self.assertEqual(manager.images.index.name, 'seq_no_obs_time')
        self.assertEqual(manager.images.shape[0], len(manager.images.index))
        self.assertEqual(manager.images.shape, (416, 3))

    def test_save_images(self):
        images_dir = self.images_dir
        manager = PDManager()
        manager.add_original_images(images_dir)
        temp_db = 'temp.pkl'
        if os.path.exists(temp_db):
            os.remove(temp_db)
        manager.save_original_images(temp_db)
        self.assertTrue(os.path.exists(temp_db))
        os.remove(temp_db)

    def test_load_images(self):
        images_dir = self.images_dir
        manager = PDManager()
        temp_db = 'temp.pkl'
        manager.add_original_images(images_dir)
        manager.save_original_images(temp_db)
        images_copy = manager.images.copy()
        manager.images = manager.images.iloc[0:0]
        self.assertTrue(manager.images.empty)
        self.assertFalse(manager.images.equals(images_copy))
        manager.load_original_images(temp_db)
        self.assertTrue(manager.images.equals(images_copy))
        os.remove(temp_db)

    def test_get_image_from_seq_no_and_frame_num(self, ):
        images_dir = self.images_dir
        jma_dir = self.best_dir
        manager = PDManager()
        manager.add_original_images(images_dir)
        manager.add_besttrack(jma_dir)
        manager.add_missing_images()
        f_name = manager.get_image_from_seq_no_and_frame_num(200717, 0)
        self.assertEqual(f_name, '200717/2007100300-200717-MTS1-1.h5')
        f_name = manager.get_image_from_seq_no_and_frame_num(200718, 120)
        self.assertEqual(f_name, '200718/2007101512-200718-MTS1-1.h5')

    def test_add_corrupted(self):
        images_dir = self.corrected_dir
        manager = PDManager()
        self.assertTrue(manager.corrected.empty)
        manager.add_corrected_images(images_dir)
        self.assertFalse(manager.corrected.empty)
        manager.add_original_images(images_dir)
        self.assertFalse(len(set(manager.corrected.keys()).intersection(set(manager.images.keys()))) == 0)


    def test_add_corrupted_info(self):
        images_dir = self.images_dir
        corrected_dir = self.corrected_dir
        pd_man = PDManager()
        pd_man.add_original_images(images_dir)
        pd_man.add_corrected_images(corrected_dir)
        self.assertFalse('corruption' in pd_man.corrected.columns)
        pd_man.add_corrected_info(images_dir, corrected_dir)
        self.assertTrue('corruption' in pd_man.corrected.columns)
        self.assertEqual(pd_man.corrected.loc[:, 'corruption'].isnull().sum(), 0)

    def test_add_missing_frames(self):
        pd_man = PDManager()
        pd_man.add_original_images(self.images_dir)
        pd_man.add_besttrack(self.best_dir)
        self.assertTrue(pd_man.missing.empty)
        pd_man.add_missing_images()
        self.assertFalse(pd_man.missing.empty)

    def test_add_missing_frames2(self):
        pd_man = PDManager()
        pd_man.add_original_images(self.images_dir)
        pd_man.add_besttrack(self.best_dir)
        pd_man.add_missing_images()
        missing = pd_man.missing.loc[198702, :]
        self.assertEqual(missing.frames_num, 160)
        self.assertEqual(missing.missing_num, 4)
        self.assertAlmostEqual(missing.completeness, 0.975)

    def test_add_missing_frames3(self):
        pd_man = PDManager()
        pd_man.add_original_images(self.images_dir)
        pd_man.add_besttrack(self.best_dir)
        self.assertFalse(pd_man.images.columns.contains('frame'))
        pd_man.add_missing_images()
        self.assertTrue(pd_man.images.columns.contains('frame'))
        self.assertTrue(pd_man.images.loc[198702, 'frame'].is_monotonic_increasing)
        self.assertTrue(len(set(pd_man.images.loc[198702, 'frame']).intersection([19, 21, 40, 149])) == 0)


if __name__ == '__main__':
    unittest.main()

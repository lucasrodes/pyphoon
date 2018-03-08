import unittest

from os.path import join, exists
import shutil
from pyphoon.db.db_manager import DBManager, BestTrack, Images
from pyphoon.db.pd_manager import PDManager
import os
from sqlalchemy import create_engine, select

class TestDbManagerMethods(unittest.TestCase):

    def test_add_besttrack(self):
        temp_db = 'temp.db'
        if os.path.exists(temp_db):
            os.remove(temp_db)
        self.assertFalse(os.path.exists(temp_db), 'file should not exist before execution of the method')
        manager = DBManager(temp_db)
        self.assertTrue(os.path.exists(temp_db), 'file should exist after initializing DBManager')
        engine = create_engine("sqlite:///"+temp_db)  # Access the DB Engine
        session = manager.session
        rows = session.query(BestTrack).count()
        self.assertEqual(0, rows, 'table should be empty')
        manager.add_besttrack('../../sampledata/datasets/jma')
        rows = session.query(BestTrack).count()
        self.assertNotEqual(0, rows, 'table should not be empty')
        os.remove(temp_db)


class TestPdManagerMethods(unittest.TestCase):

    def test_add_besttrack(self):
        temp_db = 'temp.pkl'
        if os.path.exists(temp_db):
            os.remove(temp_db)
        self.assertFalse(os.path.exists(temp_db), 'file should not exist before execution of the method')
        manager = PDManager()
        self.assertTrue(manager.besttrack.empty)
        manager.add_besttrack('../../sampledata/datasets/jma')
        self.assertFalse(manager.besttrack.empty)
        self.assertEqual(manager.besttrack.index.name, 'seq_no_obs_time')

    def test_save_besttrack(self):
        temp_db = 'temp.pkl'
        if os.path.exists(temp_db):
            os.remove(temp_db)
        self.assertFalse(os.path.exists(temp_db), 'file should not exist before execution of the method')
        manager = PDManager()
        manager.add_besttrack('../../sampledata/datasets/jma')
        manager.save_besttrack(temp_db)
        self.assertTrue(os.path.exists(temp_db))
        os.remove(temp_db)

    def test_add_orig_images(self):
        images_dir = '../../sampledata/datasets/image'
        manager = PDManager()
        self.assertTrue(manager.images.empty)
        manager.add_orig_images(images_dir)
        self.assertFalse(manager.images.empty)
        self.assertEqual(manager.images.index.name, 'seq_no_obs_time')
        self.assertEqual(manager.images.shape[0], len(manager.images.index))
        self.assertEqual(manager.images.shape, (260, 3))
        manager.add_orig_images(images_dir, file_refs_only=False)
        self.assertFalse(manager.images.image_data.empty)

    def test_save_images(self):
        images_dir = '../../sampledata/datasets/image'
        manager = PDManager()
        manager.add_orig_images(images_dir)
        temp_db = 'temp.pkl'
        if os.path.exists(temp_db):
            os.remove(temp_db)
        manager.save_images(temp_db)
        self.assertTrue(os.path.exists(temp_db))
        os.remove(temp_db)

    def test_load_images(self):
        images_dir = '../../sampledata/datasets/image'
        manager = PDManager()
        temp_db = 'temp.pkl'
        manager.add_orig_images(images_dir, file_refs_only=True)
        manager.save_images(temp_db)
        images_copy = manager.images.copy()
        manager.images = manager.images.iloc[0:0]
        self.assertTrue(manager.images.empty)
        self.assertFalse(manager.images.equals(images_copy))
        manager.load_images(temp_db)
        self.assertTrue(manager.images.equals(images_copy))
        os.remove(temp_db)

    def test_get_image_from_seq_no_and_frame_num(self, ):
        images_dir = '../../sampledata/datasets/image'
        jma_dir = '../../sampledata/datasets/jma'
        manager = PDManager()
        manager.add_orig_images(images_dir, file_refs_only=True)
        manager.add_besttrack(jma_dir)
        manager.add_missing_frames()
        f_name = manager.get_image_from_seq_no_and_frame_num(200717, 0)
        self.assertEqual(f_name, '200717/2007100300-200717-MTS1-1.h5')
        f_name = manager.get_image_from_seq_no_and_frame_num(200718, 120)
        self.assertEqual(f_name, '200718/2007101512-200718-MTS1-1.h5')

    def test_add_corrupted(self, ):
        images_dir = '../../sampledata/datasets/image'
        manager = PDManager()
        self.assertTrue(manager.corrupted.empty)
        manager.add_corrupted(images_dir)
        self.assertFalse(manager.corrupted.empty)
        manager.add_orig_images(images_dir)
        union = manager.images.join(manager.corrupted, how='inner')
        self.assertTrue(len(union) == 1)

    def test_add_corrupted2(self):
        from pyphoon.io.h5 import read_source_image
        images_dir = '../../sampledata/datasets/image'
        manager = PDManager()
        corrupted_dir = join(os.getcwd(), 'corrected')
        if exists(corrupted_dir):
            shutil.rmtree(corrupted_dir)
        manager.add_orig_images(images_dir)
        manager.add_corrupted(images_dir, corrupted_dir)
        self.assertTrue(exists(corrupted_dir))
        for root, dirs, files in os.walk(corrupted_dir):
            for f in files:
                read_img = read_source_image(join(root, f))
                self.assertEqual(read_img.shape, (512, 512))
        shutil.rmtree(corrupted_dir)

    def test_add_corrupted_info(self):
        images_dir = '../../sampledata/datasets/image'
        corrected_dir = '../../sampledata/corrected'
        pd_man = PDManager()
        with self.assertRaises(Exception) as context:
            pd_man.add_corrected_info(images_dir, corrected_dir)
        self.assertTrue('should be loaded' in str(context.exception))
        if exists(corrected_dir):
            shutil.rmtree(corrected_dir)
        os.mkdir(corrected_dir)
        pd_man.add_orig_images(images_dir)
        pd_man.add_corrupted(images_dir, corrected_dir)
        self.assertFalse('corruption' in pd_man.corrupted.columns)
        pd_man.add_corrected_info(images_dir, corrected_dir)
        self.assertTrue('corruption' in pd_man.corrupted.columns)
        self.assertEqual(pd_man.corrupted.loc[:, 'corruption'].isnull().sum(), 0)
        shutil.rmtree(corrected_dir)


if __name__ == '__main__':
    unittest.main()

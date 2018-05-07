import unittest
from pyphoon.interpolation.triplets_generator import TripletsGenerator, TripletsWithFlowGenerator
from pyphoon.db.pd_manager import PDManager
from pyphoon.db.data_extractor import DataExtractor
from os.path import join
from os import remove
import pandas as pd
import numpy as np

from pyphoon.app.preprocess import DefaultImagePreprocessor
from pyphoon.interpolation.data import read_chunk


class TestTripletsGeneratorMethods(unittest.TestCase):

    def setUp(self):
        sample_dir = '../../../sampledata/datasets/'
        self.images_dir = join(sample_dir, 'image')
        self.corrected_dir = join(sample_dir, 'corrected')
        self.best_dir = join(sample_dir, 'jma')
        self.db_dir = '../../../../../database/'
        pd_man = PDManager()
        pd_man.add_original_images(self.images_dir)
        pd_man.add_corrected_images(self.corrected_dir)
        pd_man.add_besttrack(self.best_dir)
        pd_man.add_missing_images_info()
        pd_man.add_frames()
        self.pd_man = pd_man
        self.csv_file = 'temp.csv'
        de = DataExtractor(self.images_dir, self.corrected_dir, self.pd_man)
        de.generate_triplets_csv(self.csv_file, True)
        df = pd.read_csv(self.csv_file)
        self.train = df.loc[df.test == False]
        self.test = df.loc[df.test == True]

    def tearDown(self):
        remove(self.csv_file)

    def test___len__(self):
        batch_size = 4
        gen = TripletsGenerator(self.train, batch_size=batch_size)
        self.assertTrue(len(gen), len(self.train.index) // batch_size)

    def test___getitem__(self):
        batch_size = 4
        gen = TripletsGenerator(self.train, batch_size=batch_size)
        x, y = gen[0]
        self.assertEquals(len(x), len(y))
        self.assertEquals(len(x), batch_size)
        x2, y2 = gen[1]
        self.assertEquals(len(x2), len(y2))
        self.assertEquals(len(x2), batch_size)
        self.assertFalse(np.array_equal(x, x2))

class TripletsWithFlowGeneratorMethods(unittest.TestCase):
    def test___getitem__(self):
        df = pd.read_csv('/root/fs9/grishin/database/triplets_training_set.csv')
        gen = TripletsWithFlowGenerator(df, flow_dir='/root/fs9/grishin/database/optical_flow')
        x, y = gen[0]
        self.assertEquals(len(x), len(y))
        self.assertEquals(len(x), 16)
        self.assertEquals(x.shape[3], 6)

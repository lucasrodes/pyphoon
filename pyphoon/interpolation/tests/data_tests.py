import unittest
import numpy as np

from pyphoon.app.preprocess import DefaultImagePreprocessor
from pyphoon.interpolation.data import read_chunk


class TestPdManagerMethods(unittest.TestCase):

    def setUp(self):
        self.preprocessor = DefaultImagePreprocessor(mean=269.15, std=24.14,
                                        resize_factor=2, reshape_mode='keras')


    def test_tead_chunk(self):
        input_file = '/fs9/grishin/datasets/triplets/train/0_chunk.h5'
        X, Y = read_chunk(input_file, self.preprocessor)
        self.assertEqual(X.shape[1], 256)
        self.assertEqual(X.shape[2], 256)
        self.assertEqual(X.shape[3], 2)
        self.assertEqual(Y.shape[1], 256)
        self.assertEqual(Y.shape[2], 256)
        self.assertEqual(Y.shape[3], 1)
        self.assertEquals(X.shape[0], Y.shape[0])

    def test_tead_chunk2(self):
        input_file = '/fs9/grishin/datasets/triplets/train/0_chunk.h5'
        X, Y = read_chunk(input_file, self.preprocessor, (0, 10))
        self.assertEqual(X.shape[1], 256)
        self.assertEqual(X.shape[2], 256)
        self.assertEqual(X.shape[3], 2)
        self.assertEqual(Y.shape[1], 256)
        self.assertEqual(Y.shape[2], 256)
        self.assertEqual(Y.shape[3], 1)
        self.assertEquals(X.shape[0], Y.shape[0], 10)
        self.assertEquals(X.shape, (10, 256, 256, 2))

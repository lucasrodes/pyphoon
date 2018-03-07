import unittest
from pyphoon.io.h5 import write_image, read_source_image
from os.path import exists
from os import remove

class TestH5Methods(unittest.TestCase):

    def test_write_image(self):
        image = read_source_image('../../../sampledata/datasets/image/200717/2007100300-200717-MTS1-1.h5')
        filename = 'temp_image.h5'
        if exists(filename):
            remove(filename)
        self.assertFalse(exists(filename))
        write_image(filename, image)
        self.assertTrue(exists(filename))
        image2 = read_source_image(filename)
        self.assertTrue((image == image2).all())
        remove(filename)

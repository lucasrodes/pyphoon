import unittest
from os.path import join, exists
import os
from os import listdir
import shutil
from pyphoon.db.data_convertor import convert2byte_per_pixel, convert_uint_to_float, process_folder
from pyphoon.io.h5 import read_source_image

class TestDataConverterMethods(unittest.TestCase):

    def setUp(self):
        self.test_dir = 'test_dir'
        self.src_images_dir = '../../../sampledata/datasets/image/'

    def test_convert2byte_per_pixel_test(self):
        if exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)
        os.mkdir(self.test_dir)
        f_name = '200718/2007101012-200718-MTS1-1.h5'
        src_file = join(self.src_images_dir, f_name)
        dst_file = join(self.test_dir, f_name)
        self.assertFalse(exists(dst_file))
        convert2byte_per_pixel(src_file, dst_file)
        self.assertTrue(exists(dst_file))
        src_img = read_source_image(src_file)
        uint_img = read_source_image(dst_file)
        self.assertEquals(src_img.shape, uint_img.shape)
        restored_img = convert_uint_to_float(uint_img)
        self.assertTrue(abs((src_img - restored_img)).min() < 0.5)

        if exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    # def process_folder(display, folder, input_dir, output_dir):

    def test_process_folder(self):
        src_dir = '/root/fs9/datasets/typhoon/wnp/image/'
        problem_dir = '197919'
        if exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)
        os.mkdir(self.test_dir)
        process_folder(True, input_dir=src_dir, folder=problem_dir, output_dir=self.test_dir)
        full_src_dir = join(src_dir, problem_dir)
        full_dst_dir = join(self.test_dir, problem_dir)
        files = listdir(full_src_dir)
        for f in files:
            src_img = read_source_image(join(full_src_dir, f))
            uint_img = read_source_image(join(full_dst_dir, f))
            restored_img = convert_uint_to_float(uint_img)
            self.assertTrue(abs((src_img - restored_img)).min() < 0.5)
        if exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

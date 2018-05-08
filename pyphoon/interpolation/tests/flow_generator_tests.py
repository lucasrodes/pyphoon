import unittest
from pyphoon.interpolation.flow_generator import FlowGenerator
from os.path import join, exists, isfile, isdir, abspath
from os import remove, makedirs, listdir
import numpy as np
import shutil


class TestFlowGeneratorMethods(unittest.TestCase):

    def setUp(self):
        self.flow_dir = './test_flow'
        self.image_dir = '../../../sampledata/datasets/image'
        if exists(self.flow_dir):
            shutil.rmtree(self.flow_dir, ignore_errors=True)
        makedirs(self.flow_dir, exist_ok=False)

    def tearDown(self):
        if exists(self.flow_dir):
            shutil.rmtree(self.flow_dir, ignore_errors=True)

    def test_generate_flow(self):
        resolution = (256, 256)
        flow_gen = FlowGenerator(self.image_dir, flow_dir=self.flow_dir, resolution=resolution)
        flow_gen.generate_flow(display=True)
        orig_dir_content = [x for x in listdir(self.image_dir) if isdir(join(self.image_dir, x))]
        flow_dir_content = listdir(self.flow_dir)
        self.assertListEqual(orig_dir_content, flow_dir_content)

    def test_generate_flow_files(self):
        resolution = (256, 256)
        flow_gen = FlowGenerator(self.image_dir, flow_dir=self.flow_dir, resolution=resolution)
        dirs = listdir(self.image_dir)
        d = dirs[0]
        flow_gen.generate_flow_files(d)
        original_full_path = join(self.image_dir, d)
        flow_full_path = join(self.flow_dir, d)
        original_files = listdir(original_full_path)
        flow_files = listdir(flow_full_path)
        self.assertEqual(len(original_files) - 2, len(flow_files))
        for f in flow_files:
            full_filename = abspath(join(flow_full_path, f))
            flow = flow_gen.read_flow(full_filename)
            self.assertEqual((*resolution, 2), np.shape(flow))



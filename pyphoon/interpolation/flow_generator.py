from pyphoon.interpolation.optical_flow import calc_flow
from os import listdir, makedirs
from os.path import exists, join, isdir, isfile, abspath
from skimage.transform import resize
import h5py
import numpy as np
import time


class FlowGenerator:
    """
    Optical flow generator. Utilizes model from https://github.com/sniklaus/pytorch-spynet project.
    """

    def __init__(self, image_dir, flow_dir, resolution, compression='gzip'):
        """
        Initialization

        :param image_dir: Source images top-level directory.
        :param flow_dir: Output directory for storing flow.
        :param resolution: Resolution of optical flow files.
        :param compression: Compression method for storing files.
        """
        self.image_dir = image_dir
        self.flow_dir = flow_dir
        self.resolution = resolution
        self.compression = compression

    def generate_flow(self, display=False):
        """
        Generated optical flow files

        :param display: Flag for performing output.
        """
        seq_dirs = listdir(self.image_dir)
        i = 0
        t_start = time.time()
        for seq in seq_dirs:
            if isdir(join(self.image_dir, seq)):
                i += 1
                t1 = time.time()
                self.generate_flow_files(seq)
                t2 = time.time()
                if display:
                    seq_time = (t2 - t1)
                    total_time = (t2 - t_start) / 60.0
                    print(
                        'Optical flow generated for {0} in {1:.2f} seconds, total time: {2:.2f} min, \
                        {3:.2f}% done.'.format(seq, seq_time, total_time, i / len(seq_dirs) * 100.0)
                    )

    def generate_flow_files(self, seq):
        """
        Generates optical flow files for a particular sequence of images

        :param seq: Name of sequence directory.
        :type seq: str
        """
        output_full_path = abspath(join(self.flow_dir, seq))
        input_full_path = abspath(join(self.image_dir, seq))
        makedirs(output_full_path, exist_ok=True)
        dir_content = sorted(listdir(input_full_path))
        files = [x for x in dir_content if isfile(join(input_full_path, x))]
        for i in range(1, len(files) - 1):
            # calculating input and output optical flow for a triplet of frames
            flow_in = calc_flow(join(input_full_path, files[i - 1]), join(input_full_path, files[i]))
            flow_out = calc_flow(join(input_full_path, files[i]), join(input_full_path, files[i + 1]))
            if flow_in.shape[0:2] != self.resolution:
                flow_in = resize(flow_in, (*self.resolution, 2), preserve_range=True)
                flow_out = resize(flow_out, (*self.resolution, 2), preserve_range=True)
            flow = (flow_in + flow_out) / 2.0
            error = self.save_flow(flow, join(output_full_path, files[i]))
            if error is not None:
                print("Error saving flow to file {}: {}".format(join(output_full_path, files[i]), error))

    def save_flow(self, flow, filename):
        """
        Saves optical flow to a file.

        :param flow: Optical flow data.
        :param filename: Output filename.
        :return: Error, if occures
        """

        with h5py.File(filename, "w") as f:
            f.create_dataset('flow', data=flow, compression=self.compression)

        # check integrity
        with h5py.File(filename, 'r') as f:
            read_flow = f['flow']
            if not np.array_equal(flow, read_flow):
                return 'Integrity test failed: {}'.format(filename)
            else:
                return None

    @staticmethod
    def read_flow(filename):
        """
        Reads optical flow data from a file.

        :param filename: File name.
        :return: Optical flow data.
        """
        f = h5py.File(filename, 'r')
        data = f['flow'].value
        f.close()
        return data

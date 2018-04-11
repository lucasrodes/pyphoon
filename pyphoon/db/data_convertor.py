from pyphoon.io.h5 import read_source_image, write_image, get_h5_filenames
import numpy as np
from os.path import exists, dirname, isdir, join
from os import makedirs, listdir
import time
from joblib import Parallel, delayed


def convert2byte_per_pixel(src_file, dst_file):
    dir_name = dirname(dst_file)
    if not exists(dir_name):
        makedirs(dir_name)
    src_imag = read_source_image(src_file)
    new_imag = convert_float_to_uint(src_imag)
    write_image(dst_file, new_imag, 'gzip')


def convert_float_to_uint(src_data):
    new_data = np.round((src_data - 160) / (310 - 160) * 255)
    assert new_data.all().min() >= 0
    assert new_data.all().max() <= 255
    new_data = new_data.astype(dtype='uint8')
    return new_data


def convert_uint_to_float(src_data):
    return src_data.astype(dtype='float32') / 255 * (310 - 160) + 160


def convert_dir(input_dir, output_dir, display=False):
    folders = sorted([f for f in listdir(input_dir) if isdir(join(input_dir, f))])
    Parallel(n_jobs=8)(delayed(process_folder)(display, folder, input_dir, output_dir) for folder in folders)


def process_folder(display, folder, input_dir, output_dir):
    input_dir_full = join(input_dir, folder)
    output_dir_full = join(output_dir, folder)
    t1 = time.time()
    print("Converting files from {0} dir...".format(folder)) if display is True else None
    files_count = 0
    for f in get_h5_filenames(input_dir_full):
        convert2byte_per_pixel(join(input_dir_full, f), join(output_dir_full, f))
        files_count += 1
    t2 = time.time()
    print("Converting {0} files done in {1} seconds.".format(files_count, t2 - t1)) if display is True else None


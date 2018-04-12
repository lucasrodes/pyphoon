"""
This script...

1) ... takes the source data provided by Digital Typhoon, together with
the data previously generated with script build_pdman_db.py. Hence, make sure
this script has been previously executed with success.

2) ... generates HDF5 chunk files containing all the dataset, suitable for
loading methods such as :func:´~pyphoon.app.utils.load_h5datachunks´.

3) ... does not preprocess the data, which is assume to take place during
training time. However, you may want to use a preprocessor object for
resizing purposes or even for normalising your data (not recommended). See an
example at the bottom of the script.

4) ... provides three dataset generation variants, according to how the data
is splitted among training/test/validation sets:
    A) RANDOM: Data is totally randomised and
    B) RANDOM_SEQUENCE: Data belonging to the same sequence only appears in
    one chunk file. Hence, typhoon sequence numbers are shuffled and
    distributed among the different chunks.
    C) YEAR_SEQUENCE: Data belonging to the same sequence only appears in
    one chunk file. Main difference with B) is that we keep the
    chronological order of the typhoons, so that recent typhoon imagery is
    used for testing and old imagery for training.


NOTE: Make sure to change directories in section PATHS according to your
environment.
"""
################################################################################
# ARGPARSE
################################################################################
import argparse

parser = argparse.ArgumentParser()
# Positional arguments
parser.add_argument(
    "split_mode",
    help="Choose mode of data split: 'y' for split by year, 's' to split by "
         "sequence randomly and 'r' to completly randomise samples",
    type=str
)

parser.add_argument(
    "folder",
    help="Choose folder name",
    type=str
)

parser.add_argument(
    "-r",
    "--resize",
    help="Size of resized images, i.e. 256",
    type=int
)

args = parser.parse_args()

################################################################################
# CHOOSE MODE
################################################################################
RANDOM = 1
RANDOM_SEQUENCE = 2
YEAR_SEQUENCE = 3

mode_mapping = {'y': YEAR_SEQUENCE, 's': RANDOM_SEQUENCE, 'r': RANDOM}
mode = mode_mapping[args.split_mode]

if args.resize:
    resize = args.resize
else:
    resize = False

################################################################################
# LIBRARIES
################################################################################
import sys
sys.path.insert(0, '..')
from os.path import join, exists
from os import mkdir, listdir
from random import shuffle, seed

from pyphoon.db.pd_manager import PDManager
from pyphoon.db.data_extractor import DataExtractor
from pyphoon.app.preprocess import DefaultImagePreprocessor

################################################################################
# PATHS
################################################################################
# Paths to source data (provided by Digital Typhoon)
orig_images_dir = '/root/fs9/grishin/database/uintimages/original'
besttrack_dir = '/root/fs9/datasets/typhoon/wnp/jma'

# Path where corrected images will be stored
corrected_dir = '/root/fs9/grishin/database/uintimages/corrected'

# Path to new database files (contain information for PDManager object)
db_dir = '/root/fs9/grishin/database'
# Pickle files (used to store dataframes)
images_pkl_path = join(db_dir, 'images.pkl')
corrected_pkl_path = join(db_dir, 'corrected.pkl')
besttrack_pkl_path = join(db_dir, 'besttrack.pkl')
missing_pkl_path = join(db_dir, 'missing.pkl')

# New dataset directory
output_dir = args.folder  #'/root/fs9/lucas/data/datasets/some_name'
if not exists(output_dir):
    mkdir(output_dir)

################################################################################
# PD_MAN
################################################################################
# Create pd_man
man = PDManager()
man.load_original_images(images_pkl_path)
man.load_besttrack(besttrack_pkl_path)
man.load_corrected_images(corrected_pkl_path)

################################################################################
# GENERATE DATASET
################################################################################
de = DataExtractor(orig_images_dir, corrected_dir, man)
import numpy as np

if mode == RANDOM:
    if resize:
        preprocessor = DefaultImagePreprocessor(mean=0, std=1,
                                                resize_factor=(resize, resize),
                                                type=np.uint8
                                                )
        de.generate_images_shuffled_chunks(3500, output_dir,
                                        preprocess_algorithm=preprocessor.apply,
                                        display=True)
    else:
        de.generate_images_shuffled_chunks(3500, output_dir,
                                           display=True)
if mode == RANDOM_SEQUENCE or mode == YEAR_SEQUENCE:

    seq_list = listdir(orig_images_dir)
    if mode == RANDOM_SEQUENCE:
        seed(1000)
        shuffle(seq_list)

    if resize:
        preprocessor = DefaultImagePreprocessor(mean=0, std=1,
                                                resize_factor=(resize, resize))
        de.generate_images_besttrack_chunks(seq_list, chunk_size=1 * 1024 ** 3,
                                        output_dir=output_dir,
                                        preprocess_algorithm=preprocessor.apply,
                                        display=True)
    else:
        de.generate_images_besttrack_chunks(seq_list, chunk_size=1 * 1024 ** 3,
                                            output_dir=output_dir,
                                            display=True)

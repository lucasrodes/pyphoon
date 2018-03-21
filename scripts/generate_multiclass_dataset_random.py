import sys
sys.path.insert(0, '..')
from os.path import join, exists
from os import listdir, mkdir

from pyphoon.db.pd_manager import PDManager
from pyphoon.db.data_extractor import DataExtractor
from random import shuffle, seed
from pyphoon.app.preprocess import DefaultImagePreprocessor

################################################################################
# PATHS
################################################################################
#  Paths to source data
orig_images_dir = '../../../fs9/datasets/typhoon/wnp/image/'
besttrack_dir = '../../../fs9/datasets/typhoon/wnp/jma'

# Path where corrected images are to be stored
corrected_dir = '../../../fs9/grishin/database/corrected'

# Path to new database files
db_dir = '../../../fs9/grishin/database'
# Pickle files (used to store dataframes)
images_pkl_path = join(db_dir, 'images.pkl')
corrected_pkl_path = join(db_dir, 'corrected.pkl')
besttrack_pkl_path = join(db_dir, 'besttrack.pkl')
missing_pkl_path = join(db_dir, 'missing.pkl')

# New dataset directory
output_dir = '../../../fs9/lucas/data/datasets/task_2b'

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
# PREPROCESSOR
################################################################################
preprocessor = DefaultImagePreprocessor(mean=0, std=1,
                                        resize_factor=2, reshape_mode='keras')

de = DataExtractor(orig_images_dir, corrected_dir, man)
de.generate_images_shuffled_chunks(3500, output_dir,
                                   preprocess_algorithm=preprocessor.apply,
                                   display=True)

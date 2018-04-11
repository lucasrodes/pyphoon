import sys
sys.path.insert(0, '..')
from os.path import join
from os import listdir
from random import shuffle, seed

from pyphoon.db.pd_manager import PDManager
from pyphoon.db.data_extractor import DataExtractor
from pyphoon.app.preprocess import DefaultImagePreprocessor

################################################################################
# PATHS
################################################################################
#  Paths to source data

orig_images_dir = '/fs9/datasets/typhoon/wnp/image/'

# Path where corrected images are to be stored
corrected_dir = '/fs9/grishin/database/corrected'

# Path to new database files
db_dir = '/fs9/grishin/database'
# Pickle files (used to store dataframes)
images_pkl_path = join(db_dir, 'images.pkl')
corrected_pkl_path = join(db_dir, 'corrected.pkl')
missing_pkl_path = join(db_dir, 'missing.pkl')

# New dataset directory
output_dir = '/fs9/grishin/datasets/triplets'

################################################################################
# TRAIN/TEST split
################################################################################
seed = 0
files = listdir(orig_images_dir)
shuffle(files)

ratio = 0.2

################################################################################
# PREPROCESSOR
################################################################################
preprocessor = DefaultImagePreprocessor(mean=269.15, std=24.14,
                                        resize_factor=2, reshape_mode='keras')

################################################################################
# PD_MAN
################################################################################
# Create pd_man
man = PDManager()
man.load_original_images(images_pkl_path)
man.load_corrected_images(corrected_pkl_path)
man.load_missing_images_info(missing_pkl_path)
assert 'frame' in man.images.columns

################################################################################
# GENERATE DATASET
################################################################################
de = DataExtractor(original_images_dir=orig_images_dir,
                   corrected_images_dir=corrected_dir, pd_manager=man)

de.generate_triplet_chunks(images_per_chunk=2000, output_dir=output_dir, seed=seed,
                           test_train_ratio=ratio, use_corrected=False, preprocess_algorithm=preprocessor.apply,
                           display=True)


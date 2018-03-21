import sys
sys.path.insert(0, '..')
from os.path import join
from os import listdir

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
output_dir = '../../../fs9/lucas/data/datasets/task_2'

################################################################################
# PD_MAN
################################################################################
# Create pd_man
man = PDManager()
man.load_original_images(images_pkl_path)
man.load_besttrack(besttrack_pkl_path)
man.load_corrected_images(corrected_pkl_path)

################################################################################
# TRAIN/TEST split
################################################################################
seed(1000)
files = listdir(orig_images_dir)
shuffle(files)

ratio = 0.2
pos_test = int(ratio * len(files))
ids_train = files[:-pos_test]
ids_test = files[-pos_test:]
seq_list = [(int(seq_no), 'train') for seq_no in ids_train] + \
           [(int(seq_no), 'test') for seq_no in ids_test]

################################################################################
# PREPROCESSOR
################################################################################
preprocessor = DefaultImagePreprocessor(mean=269.15, std=24.14,
                                        resize_factor=2, reshape_mode='keras')

################################################################################
# GENERATE DATASET
################################################################################
de = DataExtractor(original_images_dir=orig_images_dir,
                   corrected_images_dir=corrected_dir, pd_manager=man)

de.generate_images_besttrack_chunks(seq_list, chunk_size=1 * 1024 ** 3,
                                    output_dir=output_dir,
                                    preprocess_algorithm=preprocessor.apply,
                                    display=True)

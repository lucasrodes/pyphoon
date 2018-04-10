import sys
sys.path.insert(0, '..')
from os.path import exists, join
from os import makedirs
from pyphoon.db import pd_manager

################################################################################
# PATHS
################################################################################
# Paths to source data (provided by Digital Typhoon)
orig_images_dir = 'root/fs9/datasets/typhoon/wnp/image/'
besttrack_dir = 'root/fs9/datasets/typhoon/wnp/jma'

# Path to new database files
db_dir = 'root/fs9/grishin/data/database'

# Create database directory if does not exist
if not exists(db_dir):
    makedirs(db_dir)

# Path where corrected images are to be stored
corrected_dir = 'root/fs9/grishin/data/database/corrected'
# Path where generated images are to be stored
generated_dir = 'root/fs9/grishin/data/database/generated'
# Pickle files (used to store dataframes)
images_pkl_path = join(db_dir, 'images.pkl')
corrupted_pkl_path = join(db_dir, 'corrupted.pkl')
besttrack_pkl_path = join(db_dir, 'besttrack.pkl')
missing_pkl_path = join(db_dir, 'missing.pkl')

################################################################################
# PD_MAN
################################################################################
# Instance of PDManager
pd_man = pd_manager.PDManager()

# Load original image data
if not exists(images_pkl_path):
    print('Images database file not found, creating new...')
    pd_man.add_orig_images(orig_images_dir)
    pd_man.save_images(images_pkl_path)
    print('Done.')
else:
    pd_man.load_images(images_pkl_path)

if not exists(besttrack_pkl_path):
    print('Besttrack database file not found, creating new...')
    pd_man.add_besttrack(besttrack_dir)
    pd_man.save_besttrack(besttrack_pkl_path)
    print('Done.')
else:
    pd_man.load_besttrack(besttrack_pkl_path)

################################################################################
# FIXING ALGORITHM
################################################################################
from pyphoon.clean_satellite.correction import correct_corrupted_pixels_1
from pyphoon.clean_satellite.detection import detect_corrupted_pixels_1
from pyphoon.clean_satellite.generation import generate_new_frames_1
from pyphoon.clean_satellite.fix import TyphoonListImageFixAlgorithm

# Define Fixing algorithm
fix_algorithm = TyphoonListImageFixAlgorithm(
    detect_fct=detect_corrupted_pixels_1,
    correct_fct=correct_corrupted_pixels_1,
    generate_fct=generate_new_frames_1,
    detect_params={'min_th': 160, 'max_th': 310},
    n_frames_th=3
)

################################################################################
# GENERATE CORRECTED VERSIONS OF CORRUPTED SATELLITE IMAGES
################################################################################
from pyphoon.clean_satellite.fix import generate_new_image_dataset
generate_new_image_dataset(
    orig_images_dir,
    fix_algorithm,
    images_corrected_dir=corrected_dir,
    images_generated_dir=generated_dir,
    display=True
)
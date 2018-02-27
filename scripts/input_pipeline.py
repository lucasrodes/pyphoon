"""
Integrates the data from the original sources (image + JMA). Then, it applies
the correction methods in order to obtain a clean version of the data. The
ids of the frames that undergo some kind of correction/generation are printed.
"""

import sys
sys.path.insert(0, '..')

from os.path import join, isdir
from os import listdir
import time

from pyphoon.io.typhoonlist import create_typhoonlist_from_source
from pyphoon.clean.fix import TyphoonListImageFixAlgorithm
from pyphoon.clean.detection import detect_corrupted_pixels_1
from pyphoon.clean.correction import correct_corrupted_pixels_1
from pyphoon.clean.fillgaps import generate_new_frames_1

################################################################################
# INPUTS
#  Input 1: Directory with original satellite images
#  Input 2: Directory with original Best data
################################################################################
path_images = '../original_data/image/'
path_best = '../original_data/jma/'

################################################################################
# DEFINE
#  Directories for corrected and interpolated images
################################################################################
# Detection/Correction
detect_fct = detect_corrupted_pixels_1  # Detection method
correct_fct = correct_corrupted_pixels_1  # Correction method
detect_params = {'min_th': 160, 'max_th': 310}  # Parameters for detection meth
# Generation
fillgaps_fct = generate_new_frames_1  # Fill gap method
n_frames_th = 2  # Maximum number of frames to generate
# Algorithm
fix_algorithm = TyphoonListImageFixAlgorithm(
    detect_fct=detect_fct,
    correct_fct=correct_fct,
    fillgaps_fct=fillgaps_fct,
    detect_params=detect_params,
    n_frames_th=n_frames_th
)

################################################################################
# ACTION
################################################################################

# Get typhoon image sequence folders.
folders = sorted([f for f in listdir(path_images) if isdir(join(path_images,
                                                                f))])
# Sanity check
#  JMA data 1h-spaced

# Iterate over all folders
for folder in folders:

    print(folder)
    # Create TyphoonList
    t0 = time.time()
    seq = create_typhoonlist_from_source(
        name=folder,
        images=join(path_images, folder),
        best=join(path_best, folder)+'.tsv'
    )
    print(" TyphoonList created in", time.time() - t0, "sec")

    # Fix TyphoonList
    t0 = time.time()
    seq_new = fix_algorithm.apply(seq)
    print(" corrected in", time.time() - t0, "sec")

    # Information regarding frame ids that have been corrected/generated
    # List with ids from corrected frames: fix_algorithm.fixed_ids['corrected']
    # List with ids from generated frames: fix_algorithm.fixed_ids['generated']
    #
    # Trick:
    # Get an id of corrected frame: id = fix_algorithm.fixed_ids['corrected'][0]
    # Get corresponding frame: frame = seq_new.get_data('images', id=id)
    #
    # I believe you can build on top of this to store in the desired way.
    print(fix_algorithm.fixed_ids)

    # Clear fix ids info
    fix_algorithm.clear()

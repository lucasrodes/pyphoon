# TODO: Refactor & TEST
import sys
sys.path.insert(0, '..')
import matplotlib
matplotlib.use('agg')

from os.path import join, isdir
from os import listdir
from pyphoon.io.typhoonlist import create_typhoonlist_from_source
from pyphoon.clean.fix import TyphoonListImageFixAlgorithm
from pyphoon.clean.detection import detect_corrupted_pixels_1
from pyphoon.clean.correction import correct_corrupted_pixels_1
from pyphoon.clean.fillgaps import generate_new_frames_1
import time


# Directories
directory_images = "../original_data/image/"
directory_best = "../original_data/jma/"
# Path destination
path_normal = '../data/sequences/compressed_2/'
path_corrected = '../data/sequences/corrected_2/'
path_gapfilled = '../data/sequences/gapfilled_2/'

# Get typhoon image sequence folders.
folders = sorted([f for f in listdir(directory_images) if isdir(join(
    directory_images, f))])

# Define correction algorithm
correct_algorithm = TyphoonListImageFixAlgorithm(
    detect_fct=detect_corrupted_pixels_1,
    correct_fct=correct_corrupted_pixels_1,
    detect_params={'min_th': 170, 'max_th': 310},
)
# Define generating algorithm
generation_algorithm = TyphoonListImageFixAlgorithm(
    fillgaps_fct=generate_new_frames_1,
    n_frames_th=3
)
# Iterate over all folders
for folder in folders:
    # Get paths
    filename = folder+".h5"
    path_images = join(directory_images, folder)
    path_best = join(directory_best, folder+'.tsv')

    # User info
    print(folder)
    print(" source images:", path_images)
    print(" source metadata:", path_best)

    # Create and store TyphoonSequence
    t0 = time.time()
    sequence = create_typhoonlist_from_source(
        name=folder,
        images=path_images,
        best=path_best
    )
    print(" H5 file created in", time.time() - t0, "sec")

    # Save original
    t0 = time.time()
    sequence.save_as_h5(join(path_normal, filename), compression="gzip")
    print(" original stored in", time.time() - t0, "sec")

    # Save corrected
    t0 = time.time()
    sequence = correct_algorithm.apply(sequence)
    sequence.save_as_h5(join(path_corrected, filename), compression="gzip")
    print(" corrected stored in", time.time() - t0, "sec")

    # Save gapfilled
    t0 = time.time()
    sequence = generation_algorithm.apply(sequence)
    sequence.save_as_h5(join(path_gapfilled, filename), compression="gzip")
    print(" gap-filled stored in", time.time() - t0, "sec")

    # Clear ids info
    correct_algorithm.clear()
    generation_algorithm.clear()

import sys
sys.path.insert(0, '..')
import matplotlib
matplotlib.use('agg')
from os.path import join, isdir
from os import listdir
from pyphoon.io import create_typhoonlist_from_source
from pyphoon.clean import fix_sequence
import time


# Directories
directory_images = "../original_data/image/"
directory_best = "../original_data/jma/"
# Path destination
path_normal = '../data/sequences/compressed_1/'
path_corrected = '../data/sequences/corrected_1/'
path_gapfilled = '../data/sequences/gapfilled_1/'

# Get typhoon image sequence folders.
folders = sorted([f for f in listdir(directory_images) if isdir(join(
    directory_images, f))])


# Iterate over all folders
for folder in folders:
    # Get paths
    file = folder+".h5"
    path_images = join(directory_images, folder)
    path_best = join(directory_best, folder+'.tsv')

    # User info
    print(folder)
    print(file)
    print(" source images:", path_images)
    print(" source metadata:", path_best)

    # Create and store TyphoonSequence
    t0 = time.time()
    sequence = create_typhoonlist_from_source(
        path_images=path_images,
        path_best=path_best
    )
    print(" H5 file created in", time.time() - t0, "sec")

    # Save original
    t0 = time.time()
    sequence.save_as_h5(join(path_normal, file), compression="gzip")
    print(" compressed in", time.time() - t0, "sec")

    # Save corrected
    t0 = time.time()
    sequence = fix_sequence(sequence, gap_filling=False, display=False)
    sequence.save_as_h5(join(path_corrected, file), compression="gzip")
    print(" corrected in", time.time() - t0, "sec")

    # Save gapfilled
    t0 = time.time()
    sequence = fix_sequence(sequence, gap_filling=True, display=False)
    sequence.save_as_h5(join(path_gapfilled, file), compression="gzip")
    print(" gaps filled in", time.time() - t0, "sec")

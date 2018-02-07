import sys
sys.path.insert(0, '..')
from os.path import join, isdir
from os import listdir
from pyphoon.io import create_typhoonlist_from_source

# Directories
directory_images = "../original_data/image/"
directory_best = "../original_data/jma/"
directory_new_file = "../data/others/integration_3"

# Get typhoon image sequence folders.
folders = sorted([f for f in listdir(directory_images) if isdir(join(directory_images, f))])

# Iterate over all folders
for folder in folders:
    path_images = join(directory_images, folder)
    path_best = join(directory_best, folder+'.tsv')
    path_newfile = join(directory_new_file, folder + '.h5')

    # User info
    print(folder)
    print(" source images:", path_images)
    print(" source metadata:", path_best)
    print(" new H5 file:", path_newfile)

    # Create and store TyphoonSequence
    typhoon_sequence = create_typhoonlist_from_source(
        path_images=path_images,
        path_best=path_best
    )
    typhoon_sequence.save_as_h5(path_newfile, compression='gzip')

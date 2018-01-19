"""
The data is originally given in separate folders, one for the images and
another for the metadata:
    - Images: Each typhoon sequence has a folder, within which all the frames
    can be found in H5 format.
    - Metadata: Each typhoon sequence has a corresponding TSV file with all
    the features.
To this end, this script generates a H5 file per each typhoon sequence,
containing an array with all the sequence
frames and a list with all the metadata.
"""
import sys
sys.path.insert(0, '../')
from os.path import join, isdir
from os import listdir
from pyphoon.utils.io import create_TyphoonSequence, load_TyphoonSequence, \
    get_h5_filenames
#import matplotlib
#matplotlib.use('agg')
#import matplotlib.pyplot as plt

# TRAIN TEST VAL SPLIT
"""
from pyphoon.preprocessing.preprocessing import split
import numpy as np
np.random.seed(13)
files_train, files_valid, files_test = split(.8, .8, 
directory="../original_data/image/")
"""

# IMAGES
directory_images = "../original_data/image/"
folders = sorted([f for f in listdir(directory_images) if isdir(join(
    directory_images, f))])
# JMA
directory_best = "../original_data/jma/"
# H5 Files
directory_old = "../data/"
files_old = get_h5_filenames(directory_old)
# NEW DATA
directory_new1 = "../data/test1"
directory_new2 = "../data/final_0b"

# Select option. (1: new file, 2: update file)
option = 2
if option == 1:
    for folder in folders:
        path_images = join(directory_images, folder)
        path_best = join(directory_best, folder+'.tsv')
        path_newfile = join(directory_new1, folder + '.h5')
        # User info
        print(folder)
        print(" source images:", path_images)
        print(" source metadata:", path_best)
        print(" new H5 file:", path_newfile)
        # Do stuff
        create_TyphoonSequence(
            path_images=path_images,
            path_best=path_best
        ).save_as_h5(path_newfile)
elif option == 2:
    corrupted_frames = {}
    path_corrupted = "data/corrupted"
    for file_old in files_old:
        folder = file_old.split('.h5')[0]
        path_images = join(directory_images, folder)
        path_oldfile = join(directory_old, file_old)
        path_newfile = join(directory_new2, folder + '.h5')
        # User info
        print(file_old)
        print(" source images:", path_images)
        print(" source H5 file:", path_oldfile)
        print(" new H5 file:", path_newfile)
        # Do stuff
        sequence = load_TyphoonSequence(
            path_to_file=path_oldfile,
            path_images=path_images
        )
        """_corrupted_frames = sequence.find_corrupted_frames()
        corrupted_frames[sequence.name] = _corrupted_frames
        for frame in _corrupted_frames:
            plt.imshow(sequence.data['X'][frame])
            id = sequence.data['X_ids'][frame]
            plt.savefig(join(path_corrupted, id+'png'))
        """
        sequence.save_as_h5(path_newfile)

"""
id = "197906"
h5dt = load_H5DTFile(path_to_file=join("data/test1", id+".h5"), path_images=join("original_data/image", id))
summation = 0
max_values = 0
min_values = 0
n_samples = 0
if folder in files_train or folder in files_valid:
    print("\t train/val")
    n_samples += len(X)
    summation += np.sum(X, axis=0)
    max_values = np.maximum(np.max(X, axis=0), max_values)
    min_values = np.minimum(np.min(X, axis=0), min_values)
mu = summation/n_samples
h5f = h5py.File(join('../data/', 'global_params.h5'), 'w')
h5f.create_dataset("mean", data=mu)
h5f.create_dataset("max", data=max_values)
h5f.create_dataset("min", data=min_values)
"""
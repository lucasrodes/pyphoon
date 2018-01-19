"""
The data is originally given in separate folders, one for the images and another for the metadata:
    - Images: Each typhoon sequence has a folder, within which all the frames can be found in H5 format.
    - Metadata: Each typhoon sequence has a corresponding TSV file with all the features.
To this end, this script generates a H5 file per each typhoon sequence, containing an array with all the sequence
frames and a list with all the metadata.
"""
import sys
sys.path.insert(0, '../')
from os.path import join, isdir
from os import listdir
from utils import read_images, read_tsv
from preprocessing import split
import h5py
import numpy as np

# TRAIN TEST VAL SPLIT
np.random.seed(13)
files_train, files_valid, files_test = split(.8, .8, directory="../original_data/image/")

# IMAGES
directory_images = "../original_data/image/"
folders = [f for f in listdir(directory_images) if isdir(join(directory_images, f))]
# JMA
directory_jma = "../original_data/jma/"

summation = 0
max_values = 0
min_values = 0
n_samples = 0
for folder in folders:
    print(folder)
    X = read_images(join(directory_images, folder))
    if folder in files_train or folder in files_valid:
        print("\t train/val")
        n_samples += len(X)
        summation += np.sum(X, axis=0)
        max_values = np.maximum(np.max(X, axis=0), max_values)
        min_values = np.minimum(np.min(X, axis=0), min_values)
    Y = read_tsv(join(directory_jma, folder+'.tsv'))
    data = (X, Y)
    h5f = h5py.File(join('../data/', folder+'.h5'), 'w')
    h5f.create_dataset("X", data=X, dtype=np.float64)
    h5f.create_dataset("Y", data=Y)

mu = summation/n_samples
h5f = h5py.File(join('../data/', 'global_params.h5'), 'w')
h5f.create_dataset("mean", data=mu)
h5f.create_dataset("max", data=max_values)
h5f.create_dataset("min", data=min_values)

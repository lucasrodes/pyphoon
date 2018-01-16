from os.path import join, isdir
from os import listdir
from utils import read_images, read_tsv
import h5py
import numpy as np
from preprocessing import split

# TRAIN TEST VAL SPLIT
np.random.seed(13)
files_train, files_valid, files_test = split(.8, .8)

# IMAGES
directory_images = "original_data/image/"
folders = [f for f in listdir(directory_images) if isdir(join(directory_images, f))]
# JMA
directory_jma = "original_data/jma/"

summation = 0
max_values = 0
n_samples = 0
for folder in folders:
    print(folder)
    X = read_images(join(directory_images, folder), resize=256)
    if folder in files_train or folder in files_valid:
        print("\t train/val")
        n_samples += len(X)
        summation = np.sum(X, axis=0)/1000 + summation
        max_values = np.maximum(np.max(X, axis=0), max_values)
    Y = read_tsv(join(directory_jma, folder+'.tsv'))
    data = (X, Y)
    h5f = h5py.File(join('data/', folder+'.h5'), 'w')
    h5f.create_dataset("X", data=X, dtype=np.float64)
    h5f.create_dataset("Y", data=Y)

mu = summation*1000/n_samples
h5f = h5py.File(join('data/', 'global_params.h5'), 'w')
h5f.create_dataset("mean", data=mu)
h5f.create_dataset("max", data=max_values)
"""
Obtains the mean image, standard image, maximum and minimum values
"""
from os.path import join, isfile
from os import listdir
import sys
sys.path.insert(0, '../')
from utils import read_h5file
import h5py
import numpy as np

# IMAGES
directory_images = "../data"
files = [f for f in listdir(directory_images) if f.endswith('.h5') and isfile(join(directory_images, f))]

mu = 0
mu2 = 0
c = 0.5
maxv = 0
minv = 0

for file in files:
    print(file)
    data = read_h5file(join(directory_images, file))
    X = np.array(data['X'])
    mu = (1 - c) * mu + c * np.mean(X, axis=0)
    mu2 = (1 - c) * mu2 + c * np.mean(X**2, axis=0)
    maxv = np.maximum(np.max(X, axis=0), maxv)
    minv = np.minimum(np.min(X, axis=0), minv)

std = np.sqrt(mu2 - mu**2)
h5f = h5py.File(join('../data/preprocessing', 'global_params2.h5'), 'w')
h5f.create_dataset("mean", data=mu)
h5f.create_dataset("std", data=std)
h5f.create_dataset("max", data=maxv)
h5f.create_dataset("min", data=minv)

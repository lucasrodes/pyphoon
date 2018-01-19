"""
Obtains the mean image, standard image, maximum and minimum values
"""
from os.path import join, isfile
from os import listdir
import sys
sys.path.insert(0, '../')
from utils import read_h5file
import numpy as np
import h5py


# IMAGES
directory_images = "../data"
files = [f for f in listdir(directory_images) if f.endswith('.h5') and isfile(join(directory_images, f))]

mu = []
maxv = []
minv = []
names = []
for file in files:
    data = read_h5file(join(directory_images, file))
    X = np.array(data['X'])
    _mu = X.mean(axis=1).mean(axis=1)
    mu.extend(_mu)
    _maxv = X.max(axis=1).max(axis=1)
    maxv.extend(_maxv)
    _minv = X.min(axis=1).min(axis=1)
    minv.extend(_minv)
    names.extend([int(file.split('.')[0]+str(i)) for i in range(len(X))])
    # Plot info
    print(file)
    print(" mean:", np.max(_mu))
    print(" maxv:", np.max(_maxv))
    print(" minv:", np.max(_minv))

h5f = h5py.File(join('../data/preprocessing/', 'global_params.h5'), 'w')
h5f.create_dataset("mean", data=mu)
h5f.create_dataset("maxv", data=maxv)
h5f.create_dataset("minv", data=minv)
h5f.create_dataset("names", data=names)
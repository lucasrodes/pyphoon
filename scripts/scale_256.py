"""
Scales images from a dataset. Reducing the size of the images can decrease
the computational complexity.

It also obtains class distribution for each data blob
"""
import sys
sys.path.insert(0, '..')
import matplotlib
matplotlib.use('agg')

from os import listdir
from os.path import join
from pyphoon.io.h5 import read_h5file, write_h5file
from skimage.transform import downscale_local_mean
import numpy as np
import time

import pandas as pd
from collections import Counter

path_origin = '../data/datasets/task_1/original_512/'
path_destination = '../data/datasets/task_1/original_256/'
files = listdir(path_origin)

stats = dict()
iteration = 0
for file in files:
    iteration += 1
    print(file, "--", iteration, "/", len(files))
    t0 = time.time()

    # Get filename
    filename = file.split('.h5')[0]
    # Get data
    t1 = time.time()
    data = read_h5file(join(path_origin, file))
    print("  [!] resized in", time.time() - t1, "sec")

    # Resize data
    t1 = time.time()
    X = np.array([downscale_local_mean(x, (2, 2)) for x in data['X']])
    print("  [!] resized in", time.time() - t1, "sec")

    # Save resized data
    t1 = time.time()
    d = {
        'X': X,
        'Y': data['Y'],
        'ids': data['ids']
    }
    write_h5file(d, join(path_destination, file), compression='gzip')
    print("  [!] stored in", time.time() - t1, "sec")

    # Get statistics
    t1 = time.time()
    class_distrib = Counter(data['Y'][:, 0]).items()
    n_samples = len(data['Y'])
    stats[filename] = {int(k): v/n_samples for k, v in class_distrib}
    print("  [!] stats gotten in", time.time() - t1, "sec")

    print("\n ", time.time() - t0, "sec")
    print("-----------------------------\n")


# Create DataFrame and save statistics
df = pd.DataFrame.from_dict(stats, orient='index')
df = df.fillna(0)
df.to_csv('../data/datasets/task_1/stats.csv')
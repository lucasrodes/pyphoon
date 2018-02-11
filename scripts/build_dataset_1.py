"""
Script to build the dataset for task 1.

It takes 50/50 samples from TC class (categories 2,3,4,5) and Extra-TC class
(category 6). It ignores category 7.
"""

import sys
sys.path.insert(0, '..')
import matplotlib
matplotlib.use('agg')

from pyphoon.io import read_typhoonlist_h5
import time
import numpy as np
from os import listdir
from os.path import join
from pyphoon.io.h5 import write_h5file
from random import shuffle

path_to_folder = '../data/sequences/corrected_1/'
files = listdir(path_to_folder)
shuffle(files)


def get_data_model_1(seq):
    """ Obtains an array of imag

    :param seq: Typhoon sequence
    :type seq: TyphoonList
    :return: Array of images, array of class, array of ids.
    """

    # Resets parameters
    im = []
    bs = []
    ids = []

    # Find position samples for each class
    idx = {
        '2': seq.best[:, 4] == 2,
        '3': seq.best[:, 4] == 3,
        '4': seq.best[:, 4] == 4,
        '5': seq.best[:, 4] == 5,
        '6': seq.best[:, 4] == 6
    }
    n_6 = idx['6'].sum()

    # Get class-6 data
    im.extend(seq.images[idx['6']])
    bs.extend(np.ones(n_6).reshape(-1, 1))
    ids.extend(list(np.array(seq.images_ids)[idx['6']]))

    # Get not-6 class data
    _ratio = np.ceil(n_6 / 4)
    if _ratio == 0:
        _ratio = 1
    for i in ['2', '3', '4', '5']:
        available_samples = seq.images[idx[i]]
        n_samples = len(available_samples)
        if n_samples != 0:
            ratio = np.minimum(_ratio, n_samples)
            pos = np.random.choice(n_samples, int(ratio), replace=False)
            im.extend(available_samples[pos])
            bs.extend(np.zeros(int(ratio)).reshape(-1, 1))
            ids.extend(list(np.array(seq.images_ids)[pos]))

    return im, bs, ids


iteration = 0
file_id = 0
X = None
Y = None
ids = []
K = 1800
path_to_dataset = '../data/datasets/task_1/original_512'

for file in files:
    iteration += 1
    print(file, "--", iteration, "/", len(files))
    t0 = time.time()
    seq = read_typhoonlist_h5(join(path_to_folder, file), alignment=True)
    iim, bbs, iids = get_data_model_1(seq)

    # Update dataset blob
    ids.extend(iids)
    if X is None:
        X = np.array(iim)
        Y = np.array(bbs)
    else:
        X = np.vstack((X, iim))
        Y = np.vstack((Y, bbs))

    print("  > read", len(iim), "samples in", time.time() - t0, "sec\n")

    # Store dataset if size threshold exceeded
    if len(X) > K:
        t1 = time.time()
        d = {
            'X': X,
            'Y': Y,
            'ids': ids
        }
        file_name = str(file_id)+'.h5'
        file_id += 1
        write_h5file(d, join(path_to_dataset, file_name), compression='gzip')

        print("------------------------------------")
        print("  [!] storing...", file_name, "in", time.time() - t1, "sec")
        print("  [!] number of samples:", len(X))
        print("----------------------------------\n")

        # Restore values
        X = None
        Y = None
        ids = []

# Store remaining data
t1 = time.time()
d = {
    'X': X,
    'Y': Y,
    'ids': ids
}
file_name = str(file_id)+'.h5'
file_id += 1
write_h5file(d, join(path_to_dataset, file_name), compression='gzip')

print("------------------------------------")
print("  [!] storing...", file_name, "in", time.time() - t1, "sec")
print("  [!] number of samples:", len(X))
print("----------------------------------\n")

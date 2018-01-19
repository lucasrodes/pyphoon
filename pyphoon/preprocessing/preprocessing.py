from skimage import transform
from os.path import join, isfile
from os import listdir
import numpy as np


def resize_image(image, basewidth):
    return transform.resize(image, (basewidth, basewidth), order=0)


def _split(files, ratio):
    indices = np.random.choice(len(files), size=round(ratio * len(files)),
                               replace=False)
    count = 0
    files_1 = []
    files_2 = []
    for file in files:
        if count in indices:
            files_1.append(file)
        else:
            files_2.append(file)
        count += 1
    return files_1, files_2


def split(ratio_test, ratio_val, directory="../data/"):
    files = [f for f in listdir(directory) if f.endswith('.h5') and isfile(
        join(directory, f))]
    # Randomly select some files for training, validation and test
    _files_train, files_test = _split(files, ratio=ratio_test)
    files_train, files_valid = _split(_files_train, ratio=ratio_val)

    return files_train, files_valid, files_test


def interpolate(data, img_ids, best_ids, mode='linear'):
    for i in range(max(len(img_ids), len(best_ids))):
        # Check if missmatch in ids alignment
        if int(img_ids[i]) == int(img_ids[i]):
            pass
        elif int(img_ids[i]) > int(img_ids[i]):
            pass
        elif int(img_ids[i]) < int(img_ids[i]):
            pass
        # Check if image is corrupted

    return data
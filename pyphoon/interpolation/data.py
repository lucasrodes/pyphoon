from pyphoon.io.h5 import read_h5_dataset_file
import numpy as np

def read_chunk(filename, preprocessor, entries_num=None):
    chunk = read_h5_dataset_file(filename)
    if entries_num is None:
        start, end = 0, len(chunk['X'])
    else:
        start, end = entries_num
        start = max(start, 0)
        end = min(end, len(chunk['X']))
    X = chunk['X'][start:end]
    Y = chunk['Y'][start:end]
    prev = preprocessor.apply(X[:, :, :, 0])
    end = preprocessor.apply(X[:, :, :, 1])
    X = np.concatenate((prev, end), axis=3)
    Y = preprocessor.apply(Y[:, :, :, 0])
    return X, Y
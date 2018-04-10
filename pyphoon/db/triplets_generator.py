import threading
import numpy as np
from os.path import exists
import pandas as pd
import sys
from skimage.transform import resize

from pyphoon.io.h5 import read_source_image

bcolz_lock = threading.Lock()

class threadsafe_iter(object):
    """Takes an iterator/generator and makes it thread-safe by
    serializing call to the `next` method of given iterator/generator.
    https://github.com/fchollet/keras/issues/1638
    http://anandology.com/blog/using-iterators-and-generators/
    """

    def __init__(self, it):
        self.it = it
        self.lock = threading.Lock()
        assert self.lock is not bcolz_lock

    def __iter__(self):
        return self

    def next(self):
        with self.lock:
            return self.it.next()

def threadsafe_generator(f):
    """A decorator that takes a generator function and makes it thread-safe.
    https://github.com/fchollet/keras/issues/1638
    http://anandology.com/blog/using-iterators-and-generators/
    """
    def g(*a, **kw):
        return threadsafe_iter(f(*a, **kw))
    return g

def generator_from_df(df, batch_size, target_size, data):

    # Each epoch will only process an integral number of batch_size
    # but with the shuffling of df at the top of each epoch, we will
    # see all training samples eventually, but will skip an amount
    # less than batch_size during each epoch.
    nbatches, n_skipped_per_epoch = divmod(df.shape[0], batch_size)

    # At the start of *each* epoch, this next print statement will
    # appear once for *each* worker specified in the call to
    # model.fit_generator(...,workers=nworkers,...)!
    #     print("""
    # Initialize generator:
    #   batch_size = %d
    #   nbatches = %d
    #   df.shape = %s
    # """ % (batch_size, nbatches, str(df.shape)))

    count = 1
    epoch = 0
    read_from_disk = 0
    read_from_memory = 0
    # New epoch.
    while 1:

        # The advantage of the DataFrame holding the image file name
        # and the labels is that the entire df fits into memory and
        # can be easily shuffled at the start of each epoch.
        #
        # Shuffle each epoch using the tricky pandas .sample() way.
        df = df.sample(frac=1)  # frac=1 is same as shuffling df.

        epoch += 1
        i, j = 0, batch_size

        # Mini-batches within epoch.
        mini_batches_completed = 0
        for _ in range(nbatches):
            # Callbacks are more elegant but this print statement is
            # included to be explicit.
            # print("Top of generator for loop, epoch / count / i / j = "\
            #       "%d / %d / %d / %d" % (epoch, count, i, j))

            sub = df.iloc[i:j]
            filenames = pd.concat([sub['start'], sub['end'], sub['middle']], axis=0).unique()
            for f in filenames:
                if f not in data.keys():
                    read_from_disk += 1
                    im = read_source_image(f)
                    resized = np.round(resize(im, target_size, preserve_range=True)).astype(dtype='uint')
                    data[f] = resized
                    # print("{0} files are in memory, {1} read from disk, {2} read from memory"
                    #       .format(len(data.keys()), read_from_disk, read_from_memory))
                else:
                    read_from_memory += 1
            chunk_len = len(sub.index)
            # print('chunk len: ', chunk_len)
            im_size = np.shape(next(iter(data.values())))
            # print(im_size)
            x = np.zeros(shape=(chunk_len, im_size[0], im_size[1], 2), dtype=np.float32)
            y = np.zeros(shape=(chunk_len, im_size[0], im_size[1], 1), dtype=np.float32)
            for i in range(len(sub.index)):
                x[i, :, :, 0] = data[sub.loc[sub.index[i], 'start']]
                x[i, :, :, 1] = data[sub.loc[sub.index[i], 'end']]
                y[i, :, :, 0] = data[sub.loc[sub.index[i], 'middle']]

            mini_batches_completed += 1
            # rescale
            x = x/128 - 1.0
            y = y/128 - 1.0
            yield x, y

            i = j
            j += batch_size
            count += 1



import threading
import numpy as np
from os.path import exists, join
import keras
import pandas as pd
import sys
from skimage.transform import resize
from pyphoon.io.h5 import read_source_image
from pyphoon.interpolation.optical_flow import get_flow_filename
import h5py

class TripletsGenerator(keras.utils.Sequence):

    def __init__(self, df, batch_size=16, target_size=(256, 256), seed=0):
        # 'Initialization'
        self.cache = {}
        self.df = df
        self.seed = seed
        self.target_size = target_size
        self.batch_size = batch_size
        self.on_epoch_end()

    def __len__(self):
        # 'Denotes the number of batches per epoch'
        return len(self.df.index) // self.batch_size

    def __getitem__(self, index):
        # 'Generate one batch of data'
        sub = self.df.iloc[index:min(len(self.df.index), index+self.batch_size)]
        filenames = pd.concat([sub['start'], sub['end'], sub['middle']], axis=0).unique()
        for f in filenames:
            if f not in self.cache.keys():
                im = read_source_image(f)
                self.cache[f] = np.round(resize(im, self.target_size, preserve_range=True)).astype(dtype='uint')
        chunk_len = len(sub.index)
        im_size = np.shape(next(iter(self.cache.values())))
        x = np.zeros(shape=(chunk_len, im_size[0], im_size[1], 2), dtype=np.float32)
        y = np.zeros(shape=(chunk_len, im_size[0], im_size[1], 1), dtype=np.float32)
        for i in range(len(sub.index)):
            x[i, :, :, 0] = self.cache[sub.loc[sub.index[i], 'start']]
            x[i, :, :, 1] = self.cache[sub.loc[sub.index[i], 'end']]
            y[i, :, :, 0] = self.cache[sub.loc[sub.index[i], 'middle']]

        x = x / 128 - 1.0
        y = y / 128 - 1.0
        return x, y

    def on_epoch_end(self):
        # 'Updates indexes after each epoch'
        self.df = self.df.sample(frac=1, random_state=self.seed)
        self.seed += 1


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


class TripletsWithFlowGenerator(keras.utils.Sequence):

    def __init__(self, df, flow_dir, batch_size=16, target_size=(256, 256), seed=0):
        # 'Initialization'
        self.cache = {}
        self.df = df
        self.flow_dir = flow_dir
        self.seed = seed
        self.target_size = target_size
        self.batch_size = batch_size
        self.on_epoch_end()

    def __len__(self):
        # 'Denotes the number of batches per epoch'
        return len(self.df.index) // self.batch_size

    def __getitem__(self, index):
        # 'Generate one batch of data'
        sub = self.df.iloc[index:min(len(self.df.index), index+self.batch_size)]
        filenames = pd.concat([sub['start'], sub['end'], sub['middle']], axis=0).unique()
        for f in filenames:
            if f not in self.cache.keys():
                im = read_source_image(f)
                self.cache[f] = np.round(resize(im, self.target_size, preserve_range=True)).astype(dtype='uint')
        chunk_len = len(sub.index)
        im_size = np.shape(next(iter(self.cache.values())))
        # we have the shape of x of (width, height, 6) because 6 contains of 2 dimensions
        # for 2 images and 4 dimensions for forward and backward vertical and horizontal optical flow
        x = np.zeros(shape=(chunk_len, im_size[0], im_size[1], 6), dtype=np.float32)
        y = np.zeros(shape=(chunk_len, im_size[0], im_size[1], 1), dtype=np.float32)
        for i in range(len(sub.index)):
            start = sub.loc[sub.index[i], 'start']
            end = sub.loc[sub.index[i], 'end']
            middle = sub.loc[sub.index[i], 'middle']
            flow_fname = get_flow_filename(start, end)
            full_flow_path = join(self.flow_dir, flow_fname)
            assert exists(full_flow_path)
            with h5py.File(full_flow_path, "a") as f:
                forward_flow = f['forward_flow']
                reverse_flow = f['reverse_flow']
                x[i, :, :, 2] = resize(forward_flow[:, :, 0], self.target_size, preserve_range=True)
                x[i, :, :, 3] = resize(forward_flow[:, :, 1], self.target_size, preserve_range=True)
                x[i, :, :, 4] = resize(reverse_flow[:, :, 0], self.target_size, preserve_range=True)
                x[i, :, :, 5] = resize(reverse_flow[:, :, 1], self.target_size, preserve_range=True)
            x[i, :, :, 0] = (self.cache[start]) / 128 - 1.0
            x[i, :, :, 1] = (self.cache[end]) / 128 - 1.0
            y[i, :, :, 0] = (self.cache[middle]) / 128 - 1.0

        return x, y

    def on_epoch_end(self):
        # 'Updates indexes after each epoch'
        print('Randomizing sequence')
        self.df = self.df.sample(frac=1, random_state=self.seed)
        self.seed += 1


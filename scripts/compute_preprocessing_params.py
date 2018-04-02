"""
Obtains the parameters for preprocessing a specific dataset.
"""
import sys
sys.path.insert(0, '..')
from os import listdir
from pyphoon.io.h5 import write_h5_dataset_file
from pyphoon.app.utils import load_h5datachunks
from pyphoon.app.preprocess import get_max_min, get_mean_image, resize, \
    get_mean_pixel, get_std_pixel


################################################################################
# Load data
################################################################################
# Paths where data is stored (CHANGE)
dataset_dir = '/root/fs9/lucas/data/datasets/task_2_sequence/'
# List of HDF5 files used in TRAINING (CHANGE)
chunk_filenames = listdir(dataset_dir)
train_chunk_filenames = chunk_filenames[20:]

# Get training data
X_train = load_h5datachunks(dataset_dir,
                            train_chunk_filenames,
                            features=['data'],
                            ignore_classes=[6, 7],
                            display=True
                            )


################################################################################
# Obtain parameters for 256 x 256
################################################################################
# Compute image mean
mean_256 = get_mean_image(X_train)
# Find maximum/Minimum values
max_value_256, min_value_256 = get_max_min(X_train)
# Get pixel mean
pmean_256 = get_mean_pixel(X_train)
# Get pixel standard deviation
pstd_256 = get_std_pixel(X_train, pmean_256)


################################################################################
# Obtain parameters for 128 x 128
################################################################################
# Resize
print("Resizing")
X_train = resize(X_train, (128, 128))
# Compute mean image
mean_128 = get_mean_image(X_train)
# Find maximum/Minimum values
max_value_128, min_value_128 = get_max_min(X_train)
# Get pixel mean
pmean_128 = get_mean_pixel(X_train)
# Get pixel standard deviation
pstd_128 = get_std_pixel(X_train, pmean_128)


################################################################################
# Store
################################################################################
# Store
data = {
    'image_mean_256': mean_256[:, :, 0],
    'pixel_mean_256': pmean_256,
    'pixel_std_256': pstd_256,
    'max_value_256': max_value_256,
    'min_value_256': min_value_256,
    'image_mean_128': mean_128,
    'pixel_mean_128': pmean_128,
    'pixel_std_128': pstd_128,
    'max_value_128': max_value_128,
    'min_value_128': min_value_128
}
# Store
param_file = "set/path/to/new/file.h5"
write_h5_dataset_file(data, param_file, compression=None)

import sys
sys.path.insert(0, '..')
from os.path import join
from pyphoon.utils.io import load_TyphoonSequence, get_h5_filenames, write_h5file
import numpy as np

# Get filenames
directory_images = "../data/integration_0"
files = get_h5_filenames(directory_images)

# Parameters
mu = 0
mu2 = 0
c = 0.5
maxv = 0
minv = 0

# Iterate over all HDF files
for file in files:
    # Load sequence
    typhoon_sequence = load_TyphoonSequence(join(directory_images, file))
    X = np.array(typhoon_sequence.images)

    # Sequentially update mean image
    mu = (1 - c) * mu + c * np.mean(X, axis=0)
    mu2 = (1 - c) * mu2 + c * np.mean(X**2, axis=0)
    maxv = np.maximum(np.max(X, axis=0), maxv)
    minv = np.minimum(np.min(X, axis=0), minv)

# Compute deviation image
std = np.sqrt(mu2 - mu**2)

# Store images
write_h5file(
    data={"mean": mu, "std": std, "max": maxv, "min": minv},
    path_to_file='../data/preprocessing/params.h5',
    compression=None
)
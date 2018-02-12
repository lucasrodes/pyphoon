import sys
sys.path.insert(0, '..')

from os.path import join
from pyphoon.io import read_typhoonlist_h5
from pyphoon.io.h5 import get_h5_filenames
from pyphoon.clean import find_corrupted_frames
import matplotlib.pyplot as plt

# Directories
directory_files_0 = "../data/sequences/compressed_1"
directory_corrupted_0 = "../data/corrupted/iter_2"

# Get H5 file names
files_0 = get_h5_filenames(directory_files_0)

# Iterate over all files in dataset
corrupted_frames = {}
for file_0 in files_0:

    # Load sequence
    path_file_0 = join(directory_files_0, file_0)
    sequence = read_typhoonlist_h5(
        path_to_file=path_file_0
    )

    print("\n", file_0)

    # Get corrupted frame indices
    _corrupted_frames, _corrupted_info = find_corrupted_frames(sequence)
    corrupted_frames[sequence.name] = _corrupted_frames

    #  Save corrupted image frames as images
    count = 0
    for corrupted_frame, frame_info in zip(_corrupted_frames, _corrupted_info):
        _info = ' / '.join([key + ": " + str(value) for key, value in frame_info.items()])
        frame_id = sequence.images_ids[corrupted_frame]
        # Clean plot
        plt.clf()
        plt.imshow(sequence.images[corrupted_frame], cmap='Greys')
        plt.title(frame_id)
        plt.xlabel(_info)
        #  Save image
        plt.savefig(join(directory_corrupted_0, frame_id))
        # User info
        print("   [X] " + frame_id + " corrupted -", _info)
        count += 1

    print("\n", count, "files corrupted")
    print("---------------")

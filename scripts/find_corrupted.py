"""
The data is originally given in separate folders, one for the images and
another for the metadata:
    - Images: Each typhoon sequence has a folder, within which all the frames
    can be found in H5 format.
    - Metadata: Each typhoon sequence has a corresponding TSV file with all
    the features.
To this end, this script generates a H5 file per each typhoon sequence,
containing an array with all the sequence
frames and a list with all the metadata.
"""
import sys
sys.path.insert(0, '../')
from os.path import join, isdir
from os import listdir
from pyphoon.utils.io import  load_TyphoonSequence, get_h5_filenames
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import time


# TRAIN TEST VAL SPLIT
"""
from pyphoon.preprocessing.preprocessing import split
import numpy as np
np.random.seed(13)
files_train, files_valid, files_test = split(.8, .8, 
directory="../original_data/image/")
"""

# IMAGES
directory_images = "../original_data/image/"
folders = sorted([f for f in listdir(directory_images) if isdir(join(
    directory_images, f))])
# H5 Files
directory_old = "../data/"
files_old = get_h5_filenames(directory_old)
# NEW DATA
directory_new1 = "../data/test1"
directory_new2 = "../data/final_0b"

corrupted_frames = {}
path_corrupted = "../data/corrupted"
for file_old in files_old:
    folder = file_old.split('.h5')[0]
    path_images = join(directory_images, folder)
    path_oldfile = join(directory_old, file_old)
    path_newfile = join(directory_new2, folder + '.h5')
    # User info
    print("----------------------------")
    print(file_old)
    print(" source images:", path_images)
    print(" source H5 file:", path_oldfile)
    print(" new H5 file:", path_newfile)
    # Load sequence
    sequence = load_TyphoonSequence(
        path_to_file=path_oldfile,
        path_images=path_images
    )
    # Get corrupted indices
    _corrupted_frames, _corrupted_info = sequence.find_corrupted_frames()
    corrupted_frames[sequence.name] = _corrupted_frames
    count = 0
    for frame, info in zip(_corrupted_frames, _corrupted_info):
        plt.clf()
        count += 1
        ident = str(sequence.get_frame_id(frame))
        t0 = time.time()
        plt.imshow(sequence.data['X'][frame], cmap='Greys')
        _info = [key+": "+str(value) for key, value in info.items()]
        plt.title(file_old[:-3]+"_"+ident)
        plt.xlabel(' / '.join(_info))
        id = sequence.data['X_ids'][frame]
        plt.savefig(join(path_corrupted, file_old[:-3]+"_"+ident))
        delta = time.time()-t0
        print("   [X] " + ident + " corrupted -", _info, "- ("+str(delta)+
              "sec)")

    print("\n", count, "files corrupted")
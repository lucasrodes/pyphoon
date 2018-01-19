import matplotlib

matplotlib.use('agg')
import matplotlib.pyplot as plt
import sys

sys.path.insert(0, '../')
from pyphoon.utils.io import load_TyphoonSequence
import numpy as np


option = 3
if option == 1:
    path = "../data/final_0/201503.h5"
    frame_0 = 210
    frame_1 = 217
elif option == 2:
    path = "../data/final_0/199512.h5"
    frame_0 = 136
    frame_1 = 140
elif option == 3:
    path = "../data/final_0/199218.h5"
    frame_0 = 269
    frame_1 = 273
elif option == 4:
    path = "../data/final_0/200408.h5"
    frame_0 = 405
    frame_1 = 413

typhoon_sequence = load_TyphoonSequence(path)
frames = np.arange(frame_0, frame_1)
for frame in frames:
    plt.imshow(typhoon_sequence.data['X'][frame], cmap='Greys')
    plt.savefig('minv_highv/'+typhoon_sequence.name + "_" +str(
        typhoon_sequence.get_frame_id(frame)))

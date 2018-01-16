import numpy as np
from eda_metadata import plot_hist, plot_2feature_heatmap
from utils import read_tsvs

# PARAMS
use_only_raw = True  # True: Use non-interpolated samples. False: Use all data samples
generate_lat_lng_file = False  # True: Generate latitude-longitude file (useful to plot data as heatmap in a world map)
shall_plot_hist = False  # True: Plot histogram of data according to certain feature
shall_plot_heatmap = True  # True: Plot heatmap between two features


# Read tsv data and convert to numpy array
f = read_tsvs()
data = np.array(f)
# Only consider data since 1978
data = data[data[:, 0] > 1977]
# Number of recorded typhoons and features
N, D = data.shape
# Number of interpolated data
N_interp = int(N - data[:, -1].sum())

# Histogram
if shall_plot_hist:
    plot_hist(data, index=0, bins=-1)

# raw vs all data
if use_only_raw:
    index = data[:, -1] == 0
    data = data[index]

# Latitude/Longitude file
if generate_lat_lng_file:
    lat, lng = data[:, 5], data[:, 6]
    s = [{'lat': latt, 'lng': lngg, 'count': 1} for latt, lngg in zip(lat, lng)]
    thefile = open('test.txt', 'w')
    for item in s:
      thefile.write("%s,\n" % item)

# Heatmap
if shall_plot_heatmap:
    plot_2feature_heatmap(data, index1=7, index2=4)

data_extra = data[data[:, 4] == 6]
data_tc = data[data[:, 4] != 6]
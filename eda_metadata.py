import numpy as np
from os import listdir
from os.path import isfile, join
import matplotlib
#matplotlib.use('agg')
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


feature_names = ["year", "month", "day", "hour", "class", "latitude", "longitude", "pressure", "wind", "gust",
                 "storm_direc", "storm_radius_major", "storm_radius_minor", "gale_direc", "gale_radius_major",
                 "gale_radius_minor", "landfall", "speed", "direction", "interpolated"]


def read_(path='original_data/jma/'):
    """
    Reads all the files from the jma directory and returns a list of N elements, each being a list of typhoon features
    :param path: Path of the JMA metadata
    :return: List with the metadata of the N images
    """
    files = listdir(path)
    metadata = []
    for f in files:
        f = join(path, f)
        if isfile(f):
            ff = open(f, 'r').readlines()
            for fff in ff:
                _metadata = fff.split('\t')
                _metadata[-1] = _metadata[-1].split('\n')[0]
                __metadata = list(map(float, _metadata))
                index = [0, 1, 2, 3, 4, ]
                for i in index:
                    __metadata[i] = int(__metadata[i])
                __metadata[-1] = bool(__metadata[-1])
                metadata.append(__metadata)
    return metadata


def plot_hist(data, index, bins=100, show_fig=False, save_fig=False, fig_name="untitled"):
    """ Plots a histogram of the data samples according to value that feature *index* takes
    :param data:
    :param index: Index of the feature to analyze
    :param bins: Number of bins to use to plot the histogram
    :param show_fig: (default False.) Set to true if image should be plotted.
    :param save_fig: (default False.) Set to true if image should be saved.
    :param fig_name: Filename of stored imaged.
    :return:
    """
    data = np.array(data)
    if bins == -1:
        # bins = np.sort(list(set(raw_data[:, index])))
        bins = len(set(data[:, index]))
    plt.hist(data[:, index], bins=bins)
    if show_fig:
        plt.show()
    if save_fig:
        plt.savefig(fig_name)


def plot_2feature_heatmap(data, index1, index2=4):
    """ Plots heatmap of the data based on the values they take on two given features
    :param data: Data samples as a numpy.array.
    :param index1: Index of the feature 1 in the heatmap
    :param index2: Index of the feature 2 in the heatmap
    :return:
    """
    feature1 = np.sort(list(set(data[:, index1])))
    feature2 = np.sort(list(set(data[:, index2])))

    table = {}
    for _class in feature2:
        _data = data[data[:, index2] == _class]
        v, k = np.histogram(_data[:, index1], bins=feature1)
        table[_class] = {kk: vv for kk, vv in zip(k, v)}

    df = pd.DataFrame(table)

    sns.heatmap(df, cmap='RdYlGn_r', linewidths=0.5, annot=True, fmt='g')
    plt.yticks(rotation=0)
    plt.xlabel(feature_names[index2])
    plt.ylabel(feature_names[index1])
    plt.show()
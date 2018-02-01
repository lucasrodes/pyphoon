# -*- coding: utf-8 -*-

import numpy as np
from os import listdir
from os.path import isfile, join
import matplotlib
# matplotlib.use('agg')
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


feature_names = ["year", "month", "day", "hour", "class", "latitude",
                 "longitude", "pressure", "wind", "gust", "storm_direc",
                 "storm_radius_major", "storm_radius_minor", "gale_direc",
                 "gale_radius_major", "gale_radius_minor", "landfall",
                 "speed", "direction", "interpolated"]


def plot_hist(data, feature_index, bins=100, show_fig=False, save_fig=False,
              fig_name="untitled"):
    """ Generates a histogram of a certain feature from the samples in data.
        This image may be stored or just displayed.

    :param data: Dataframe with best track data. Details on all features can
                    be found at the `JMA RSMC Tokyo-Typhoon Center`_ website.
    :type data: pandas.DataFrame
    :param feature_index: Index of the feature from data to analyze.
    :type feature_index: int
    :param bins: Number of bins to use to plot the histogram of a certain
                    feature. Set to -1 if there should be as many bins as
                    values takes the feature.
    :type bins: int, default 100
    :param show_fig: Flag to plot the histogram.
    :type show_fig: bool, default False
    :param save_fig: Set to true if image should be saved.
    :type save_fig: bool, default False
    :param fig_name: Filename of stored imaged.
    :type fig_name: bool, default "untitled"

    .. _JMA RSMC Tokyo-Typhoon Center:
        http://www.jma.go.jp/jma/jma-eng/jma-center/rsmc-hp-pub-eg/Besttracks/e_format_bst.html

    :Example: In the following example we load the best track data. Note that we
                only consider data starting from 1978. We take the forth
                feature, which is the class index. Hence, we aim to visualize
                the distribution of samples depending on the class they belong
                to.

    >>> from pyphoon.utils.io import read_tsvs
    >>> from pyphoon.utils.eda_jma import plot_hist
    >>> # Load data
    >>> data = np.array(read_tsvs())
    >>> # Only consider data since 1978
    >>> data = data[data[:, 0] > 1977]
    >>> plot_hist(data, show_fig=True, feature_index=4, bins=-1)
    """
    data = np.array(data)
    if bins == -1:
        # bins = np.sort(list(set(raw_data[:, index])))
        bins = len(set(data[:, feature_index]))
    plt.hist(data[:, feature_index], bins=bins)
    if show_fig:
        plt.show()
    if save_fig:
        plt.savefig(fig_name)


def plot_2feature_heatmap(data, index1, index2=4, annotation=True,
                          linewidths=.5, show_fig=False, save_fig=False,
                          fig_name="untitled"):
    """ Plots heatmap of the data based on the values they take on two given
    features.

    :param data: Data samples as a numpy.array.
    :type data: pandas.DataFrame
    :param index1: Index of the feature 1 in the heatmap
    :type index1: int
    :param index2: Index of the feature 2 in the heatmap
    :type index2: int
    :param annotation: Set to true if heatmap cell value is to be displayed.
    :type annotation: boold, default True
    :param linewidths: Width of the separation line between of the cells in
                        the heatmap
    :type linewidths: float
    :param show_fig: Flag to plot the histogram.
    :type show_fig: bool, default False
    :param save_fig: Set to true if image should be saved.
    :type save_fig: bool, default False
    :param fig_name: Filename of stored imaged.
    :type fig_name: bool, default "untitled"

    :Example: In the following example we load the best track data. Note that we
                only consider data starting from 1978. We take the seventh and
                forth features, which represent the pressure and the class
                identifier, respectively. Hence, we aim to visualize
                the distribution of the pressure values depending on the class
                they belong to.

    >>> from pyphoon.utils.io import read_tsvs
    >>> from pyphoon.utils.eda_jma import plot_2feature_heatmap
    >>> # Load data
    >>> data = np.array(read_tsvs())
    >>> # Only consider data since 1978
    >>> data = data[data[:, 0] > 1977]
    >>> plot_2feature_heatmap(data, index1=7, index2=4, linewidths=0, annot=False)
    """
    feature1 = np.sort(list(set(data[:, index1])))
    feature2 = np.sort(list(set(data[:, index2])))

    table = {}
    for _class in feature2:
        _data = data[data[:, index2] == _class]
        v, k = np.histogram(_data[:, index1], bins=feature1)
        table[_class] = {kk: vv for kk, vv in zip(k, v)}

    df = pd.DataFrame(table)

    sns.heatmap(df, cmap='RdYlGn_r', linewidths=linewidths, annot=annotation,
                fmt='g')
    plt.yticks(rotation=0)
    plt.xlabel(feature_names[index2])
    plt.ylabel(feature_names[index1])
    if show_fig:
        plt.show()
    if save_fig:
        plt.savefig(fig_name)

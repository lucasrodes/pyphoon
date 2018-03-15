Best Track data Exploratory Data Analysis
=========================================

In this notebook we attempt to have a first glance at the best data, to help
us better understand the nature of Digital Typhoon data. We will only
consider the data starting from 1978, which is the year that satellite
imagery started to be collected. Make sure to replace ``path_best`` with
the path to the directory containing the TSV files with best track data.


Load all the best data
----------------------

>>> # Read tsv data and convert to numpy array
>>> from pyphoon.io.tsv import read_tsvs
>>> all_data = np.array(read_tsvs(path_best))
>>> # Only consider data since 1978
>>> all_data = all_data[all_data[:, 0] > 1978]
>>> # Number of recorded typhoons and features
>>> N, D = all_data.shape
>>> # Print shape of best table
>>> print("Number of samples:", N)
>>> print("Number of features:", D)
Number of samples: 208953
Number of samples: 20

To get information about the features in ``all_data`` you can check the
variable ``feature_names`` from pyphoon.eda_jma.

>>> import pyphoon.eda_jma as eda
>>> eda.feature_names
['year',
 'month',
 'day',
 'hour',
 'class',
 'latitude',
 'longitude',
 'pressure',
 'wind',
 'gust',
 'storm_direc',
 'storm_radius_major',
 'storm_radius_minor',
 'gale_direc',
 'gale_radius_major',
 'gale_radius_minor',
 'landfall',
 'speed',
 'direction',
 'interpolated']

Consider only real data
-----------------------

As aforementioned, only 17% of all best data is real while the rest has been
generated via interpolation to catch up with the image observation frequency.
Luckily, the 20th feature in ``all_data`` tells us which data is original (i
.e. '0' if original, '1' if synthetic).

>>> # Discard synthetic samples
>>> index = all_data[:, -1] == 0
>>> data = all_data[index]

Plot histogram of classes
-------------------------

Method :func:`~pyphoon.eda_jma.plot_hist` provides the necessary tools to
obtain the histogram of any feature. The 4th feature in ``all_data`` tells us
the class of the sample.

>>> plot_hist(all_data, show_fig=True, feature_index=4, bins=[2,3,4,5,6,7,8],
... normed=True, centre=True, title="Class histogram", xlabel="Class")

Use arguments ``save_fig`` and ``fig_name`` to store the generated plot.

Plot histogram of pressure
--------------------------

The 7th feature conveys the pressure values. Let's find the minimum and
maximum values of the pressure.

>>> minimum = min(all_data[:, 7])
>>> maximum = max(all_data[:, 7])
>>> print("minimum:", minimum, "\nmaximum:", maximum)
minimum: 870.0
maximum: 1018.0

Now, we want to plot the histogram. We will use bins of resolution of 7 hPa.

>>> bins = np.arange(870, 1018, 7)
>>> plot_hist(data, show_fig=True, feature_index=7, bins=bins, normed=True,
... title="Pressure histogram", xlabel="Class")

Wind speed time analysis
------------------------

Let us now provide a simple example of time analysis. In particular we will
explore the wind speed values along time. The 8th feature is the responsible
for the wind-speed data. First, we obtain the wind speeds of all samples per
year and store them in an array, accessible via its year using the dictionary
``wind_sp``.

>>> # Get wind speeds from all samples per year
>>> wind_sp = {}
>>> for idx in range(N):
>>>     year = int(data[idx, 0])
>>>     if year not in wind_sp:
>>>         wind_sp[year] = []
>>>     wind_sp[year].append(data[idx, 8])

Next, we can easily iterate over all dictionary values and compute the mean.
This way, we obtain the wind speed mean per year.

>>> # Get the mean
>>> mean_wind_sp = {}
>>> for key in wind_sp.keys():
>>>     mean_wind_sp[key] = np.mean(wind_sp[key])

Finally, we plot the mean wind speed over time.

>>> plt.plot(list(mean_wind_sp.keys()), list(mean_wind_sp.values()), 'k')
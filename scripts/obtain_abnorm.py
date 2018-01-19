from pyphoon.utils.io import read_h5file
import numpy as np
import plotly.plotly as py
import plotly.graph_objs as go


"""
1) Compute the following parameters for each image:
- Mean, max value and min value 
2) Next, we plot the distribution of this values
3) Finally, we set thresholds for what we consider to be acceptable values. 
Images that fall outside the acceptable range are considered to be corrupted.
"""

# Load params
path = "data/preprocessing/global_params.h5"
params = read_h5file(path)

# Remove heavily corrupted images
pos = np.argsort(params['minv'])[::1][:3]

for p in pos:
    params['minv'][p] = 160
    params['maxv'][p] = 300
    params['mean'][p] = 270

data = [go.Histogram(x=params['mean'])]
py.plot(data, filename='mean')

data = [go.Histogram(x=params['maxv'])]
py.plot(data, filename='max')

data = [go.Histogram(x=params['minv'])]
py.plot(data, filename='min')

"""
# Get indices of images with most positive and most negative means.

n_p = 10
pos_p = np.argsort(params['maxv'])[n_p:][::-1]
n_n = 10
pos_n = np.argsort(params['minv'])[-n_n:][::-1]
"""
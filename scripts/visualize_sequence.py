import sys
sys.path.insert(0, '..')
#import matplotlib
#matplotlib.use('agg')

from pyphoon.io import read_typhoonlist_h5
from pyphoon.utils import DisplaySequence

# Load sequence
sequence = read_typhoonlist_h5('../sampledata/201725.h5')

# Create DisplaySequence instance and run
DisplaySequence(
    typhoon_sequence=sequence,
    name="201725",
    interval=100
).run()

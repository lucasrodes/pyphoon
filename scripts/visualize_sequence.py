import sys
sys.path.insert(0, '..')
from pyphoon.io import read_typhoonlist_h5
from pyphoon.utils import DisplaySequence

# Load sequence
sequence = read_typhoonlist_h5('../sampledata/197906.h5')

# Create DisplaySequence instance and run
DisplaySequence(
    typhoon_sequence=sequence,
    name="201626",
    interval=100,
).run()

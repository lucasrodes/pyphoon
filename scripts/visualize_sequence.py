import sys
sys.path.insert(0, '..')
from pyphoon.utils.io import load_TyphoonSequence
from pyphoon.utils.utils import DisplaySequence

# Load sequence
sequence = load_TyphoonSequence('../sampledata/197906.h5')

# Create DisplaySequence instance and run
DisplaySequence(
    typhoon_sequence=sequence,
    name="197906",
    interval=100,
).run()

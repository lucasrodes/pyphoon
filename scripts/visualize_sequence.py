import sys
sys.path.insert(0, '..')
from pyphoon.utils.io import load_TyphoonSequence
from pyphoon.utils.utils import DisplaySequence


sequence = load_TyphoonSequence('../sampledata/197906.h5')

DisplaySequence(
    typhoon_sequence=sequence,
    name="197906",
    interval=100,
).run()

# pyphoon
This project developed as part of the [Digital Typhoon](http://digital-typhoon.org) project from [Kitamoto-sensei](http://www.nii.ac.jp/en/faculty/digital_content/kitamoto_asanobu/). 

**pyphoon** provides a set of tools to enable easy and pythonic interaction 
the Digital Typhoon dataset.

For details, refer to the full documentation of the project at [http://lcsrg.me/pyphoon](http://lcsrg.me/pyphoon).

## Contents

| **Section**              | **Description**                                                 |
|--------------------------|-----------------------------------------------------------------|
| [pyphoon](pyphooon)      | Library for Digital Typhoon project                             |
| [docs](docs)             | Documentation of the library                                    |
| [scripts](scripts)       | Some example scripts using library tools                        |
| [notebooks](notebooks)   | Notebooks with example code using library tools                 |
| [sampledata](sampledata) | Sample data from Digital Typhoon, used in scripts and notebooks |
| [comments](comments)     | Comments from the authors as they worked in the project         |


## Installation

Refer to the instructions [here](http://lcsrg.me/pyphoon/build/html/env_setup.html)
 
## Getting started

Easily visualize an animation of a sequence:

```python
from pyphoon.utils.io import load_TyphoonSequence
from pyphoon.utils.utils import DisplaySequence

# Load a sequence
sequence = load_TyphoonSequence('../sampledata/197906.h5')

# Visualize sequence
DisplaySequence(
    typhoon_sequence=sequence,
    name="197906",
    interval=300,
).run()
```



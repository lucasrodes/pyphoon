# [pyphoon](http://lcsrg.me/pyphoon)
Developed as part of the [Digital Typhoon](http://digital-typhoon.org) project from [Kitamoto-sensei](http://www.nii.ac.jp/en/faculty/digital_content/kitamoto_asanobu/). 
Provides a set of tools to enable easy and pythonic interaction the Digital Typhoon dataset.

**Full documentation: [http://lcsrg.me/pyphoon](http://lcsrg.me/pyphoon)**


![Alt Text](assets/201725.gif)  |  ![](assets/201725.gif)





## Contents

| **Section**              | **Description**                                                 |
|--------------------------|-----------------------------------------------------------------|
| [pyphoon](pyphooon)      | Library for Digital Typhoon project                             |
| [docs](docs)             | Documentation of the library                                    |
| [scripts](scripts)       | Some example scripts using library tools                        |
| [notebooks](notebooks)   | Notebooks with example code using library tools                 |
| [sampledata](sampledata) | Sample data from Digital Typhoon, used in scripts and notebooks |


## Installation

Refer to the instructions [here](http://lcsrg.me/pyphoon/build/html/env_setup.html)
 
## Getting started

Easily visualize an animation of a sequence:

```python
from pyphoon.io import read_typhoonlist_h5
from pyphoon.utils import DisplaySequence

# Load a sequence
sequence = read_typhoonlist_h5('../sampledata/197906.h5')

# Visualize sequence
DisplaySequence(
    typhoon_sequence=sequence,
    name="197906",
    interval=300,
).run()
```



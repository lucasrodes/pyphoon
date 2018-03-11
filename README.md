# [pyphoon](http://lcsrg.me/pyphoon)
Developed as part of the [Digital Typhoon](http://digital-typhoon.org) project from [Kitamoto-sensei](http://www.nii.ac.jp/en/faculty/digital_content/kitamoto_asanobu/). 
Provides a set of tools to enable easy and pythonic interaction the Digital Typhoon dataset.

**Full documentation [here](http://lcsrg.me/pyphoon)**


## Contents

| **Section**              | **Description**                                                    |
|--------------------------|--------------------------------------------------------------------|
| [pyphoon](pyphooon)      | Library for Digital Typhoon project                                |
| [docs](docs)             | Library documentation files                                        |
| [notebooks](notebooks)   | Example code snippets                                              |
| [scripts](scripts)       | Some example scripts using library tools                           |
| [sampledata](sampledata) | Sample data from Digital Typhoon, used in scripts and notebooks    |


## Installation

Refer to the instructions [here](http://lcsrg.me/pyphoon/build/html/env_setup.html).
 
## Getting started

### Load and visualize sequence

```python
from pyphoon.io.typhoonlist import create_typhoonlist_from_source
from pyphoon.visualize import DisplaySequence

# Load a sequence
sequence = create_typhoonlist_from_source(
    name='201725',
    images='sampledata/datasets/image/200717',
    best='sampledata/datasets/jma/200717.tsv'
)

# Visualize sequence
DisplaySequence(
    typhoon_sequence=sequence,
    interval=100,
).run()
```

![](assets/201725.gif)


## More

**pyphoon** is being used as a baseline for multiple projects at NII. These, 
once matured, might be added to the main library. For now, they are available
 in their respective repositories.

* [**tcxtc-deep-classifier**](http://github.com/lucasrodes/tcxtc-deep-classifier): Deep Learning for classification of 
typhoon satellite imagery in two categories: Tropical Cyclone and 
Extra-Tropical Cyclone 


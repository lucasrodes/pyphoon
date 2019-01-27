# pyphoon

![](docs/source/_static/banner_small.png)

---

Developed as part of the [Digital Typhoon](http://digital-typhoon.org) project from [Kitamoto-sensei](http://www.nii.ac.jp/en/faculty/digital_content/kitamoto_asanobu/). 
Provides a set of tools to enable easy and pythonic interaction the Digital Typhoon dataset.


**Full documentation [here](http://lcsrg.me/pyphoon)**.


## Contents

| **Section**                | **Description**                                                                            |
|----------------------------|--------------------------------------------------------------------------------------------|
| [pyphoon](pyphooon)        | Library for Digital Typhoon project                                                        |
| [docs](docs)               | Library documentation files                                                                |
| [notebooks](notebooks)     | Basic code examples. (will be removed in near future)                                      |
| [scripts](scripts)         | Some example scripts using library tools                                                   |
| [sampledata](sampledata)   | Sample data from Digital Typhoon, used in                                                  |
| [experiments](experiments) | Data and files related to specific applications of pyphoon library (includes notebooks).   |


## Installation

Refer to the instructions [here](http://lcsrg.me/pyphoon/build/html/environment.html).
 
## Getting started

### Load and visualize sequence

```python

# Load a sequence
from pyphoon.io.h5 import read_source_images
from pyphoon.io.utils import get_image_ids
images = read_source_images('sampledata/datasets/image/200717')
images_ids = get_image_ids('sampledata/datasets/image/200717')

# Display sequence
from pyphoon.visualise import DisplaySequence
DisplaySequence(
    images=images,
    images_ids=images_ids,
    name='200717',
    interval=100
).run()
```

![](assets/201725.gif)


### [Experiments](experiments)

**pyphoon** was mainly conceived to assist researchers in Machine Learning/Deep 
Learning experiments. To this end, this repository provides examples of 
experiments carried by Kitamoto-lab interns:
 
| **Section**                                             | **Description**                                                                            |
|---------------------------------------------------------|--------------------------------------------------------------------------------------------|
| [tcxtc](experiments/tcxtc)                              | *Tropical cyclone* vs *Extratropical cyclone* binary classifier.  |
| [multiclass](experiments/multiclass)                    | Classification of *Topical cyclone* intensity in four categories. |
| [pressure regression](experiments/pressure_regression)  | Regression of the centre pressure in *Tropical cyclones*          |
 
**Note**: All models have been implemented using [keras](http://keras.io).

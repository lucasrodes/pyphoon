# pyPhoon
Tools for Digital Typhoon DL/ML Project. You can find the documentation of 
this library is hosted at [http://lcsrg.me/pyphoon](http://lcsrg.me/pyphoon).

## Contents

| **Section**              | **Description**                                                 |
|--------------------------|-----------------------------------------------------------------|
| [pyphoon](pyphooon)      | Library for Digital Typhoon project                             |
| [docs](docs)             | Documentation of the library                                    |
| [scripts](scripts)       | Some example scripts using library tools                        |
| [notebooks](notebooks)   | Notebooks with example code using library tools                 |
| [sampledata](sampledata) | Sample data from Digital Typhoon, used in scripts and notebooks |
| [comments](comments)     | Comments from the authors as they worked in the project         |


## Set up

This project has been developed using a docker image. To install docker visit
 [](). Once installed follow the steps below to set up the environment:
 
 
### Jupyter and Docker

## Example

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



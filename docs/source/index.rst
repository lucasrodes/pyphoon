.. pyphoon documentation master file, created by
   sphinx-quickstart on Fri Jan 26 18:25:31 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

pyphoon
=======

`pyphoon <http://github.com/lucasrodes/pyphoon>`_ is a python library developed since 2018 by interns at `Kitamoto Lab
<http://agora.ex.nii.ac.jp/~kitamoto/index.html.en>`_ to
provide simple, easy and a pythonic interaction with the *Digital Typhoon*
dataset. It contains a wide set of tools to assist in the exploration of the
data and detection of possible corrupted files. You can find the GitHub
repository `here <http://github.com/lucasrodes/pyphoon>`_.


**Get Familiar:** Set up the required environment and test some of the code
provided examples.

    -   :doc:`Setting up the environment <env_setup>`
    -   :doc:`Code examples <examples>`


**Available Projects:** List of projects developed using **pyphoon**.

    -   `Tropical Cyclone vs. Extra-Tropical Cyclone classifier
        <http://github.com/lucasrodes/tcxtc-deep-classifier>`_

Documentation
-------------

For further details on any of the modules of this library check the
corresponding link below.

..  toctree::
    :maxdepth: 2

    pyphoon.io <pyphoon.io>
    pyphoon.clean <pyphoon.clean>
    pyphoon.visualize <pyphoon.visualize>
    pyphoon.eda_jma <pyphoon.eda_jma>



Known Issues
------------


*   **Importing the library**

    As of now, to correctly import the library, please make use of `sys.path`
    specifying the directory of the library. In the future, however, we plan on
    pushing this library to PyPI repository.

    >>> import sys
    >>> sys.path.insert(0, 'path/to/pyphoon')


*   **Using matplotlib in the server**
    Trying to generate plots in the server without graphical interface can
    lead to an error when trying to import the library `matplotlib`. To avoid
    this, make sure to use a non-interactive backend such as `agg`.

    >>> import matplotlib
    >>> matplotlib.use('agg')


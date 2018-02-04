.. pyphoon documentation master file, created by
   sphinx-quickstart on Fri Jan 26 18:25:31 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

pyphoon
===================================

pyphoon is a python tool developed in 2018 by interns at Kitamoto Lab to
support simple and easy interaction with *Digital Typhoon* dataset. It began
as a set of tools meant to assist in the exploration of the data and possible
detection of corrupted files. However, new features, such as actual models
might be added as time passes.


Get familiar:

* :doc:`Setting up the environment <env_setup>`
* :doc:`Examples <examples>`


Documentation
=============

For further details on any of the modules of this library check the
corresponding link below.

..  toctree::
    :maxdepth: 2

    pyphoon.preprocessing <pyphoon.preprocessing>
    pyphoon.utils <pyphoon.utils>


Known Issues
============


*   **Importing the library**
    As of now, to correctly import the library, please make use of `sys.path` specifying the directory of the library.

    >>> import sys
    >>> sys.path.insert(0, 'path/to/pyphoon')


*   **Using matplotlib in the server**
    If you want to generate plots in the server make sure
    If you are trying to generate plots in the server note that there might not
    graphic interface. This can lead to an error when trying to import the
    library `matplotlib`.

    To avoid this, make sure to use a non-interactive backend such as `agg`.

    >>> import matplotlib
    >>> matplotlib.use('agg')


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

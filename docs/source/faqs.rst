FAQs
====

*   `How can I cite this project?`_
*   `Can I run Jupyter from inside the docker container?`_
*   `Where do I get the Digital Typhoon data?`_

How can I cite this project?
----------------------------

Please cite pyphoon in your publications if it helped you out. BibTeX entry:

..  code-block:: latex

    @misc{pyphoon2017,
      title={pyphoon: Python interface for Digital Typhoon},
      author={Kitamoto Lab (NII)},
      year={2017},
      publisher={GitHub},
      howpublished={\url{https://github.com/lucasrodes/pyphoon}},
    }

-----

Can I run Jupyter from inside the docker container?
---------------------------------------------------

The short answer is yes. Longer answer is that you basically need to forward
a port when creating a docker image instance. The long answer can be found
`here <https://medium.com/@lucasrg/using-jupyter-notebook-running-on-a-remote-docker-container-via-ssh-ea2c3ebb9055>`_.

-----

Where do I get the Digital Typhoon data?
----------------------------------------

The dataset has not been openly released, but we may make it accessible upon
request. Try contacting the current `project responsible <home
.html#support>`_ or `Kitamoto-sensei`_ directly.

..  _Kitamoto-sensei:
    https://www.nii.ac.jp/en/faculty/digital_content/kitamoto_asanobu/

-----

I cannot import the library
---------------------------

This might occur due to several reasons. Below we list some of the known errors.

*   ``ModuleNotFoundError: No module named 'pyphoon'``

    Make sure that the folder with all the modules, i.e. **pyphoon**, is at the
    same level as the code you are trying to execute. If that is not possible,
    you can let python know where this folder is by using `sys.path.insert` and
    passing the directory path containing the library folder.

    >>> import sys
    >>> sys.path.insert(0, path_to_pyphoon)

*   ``ImportError: No module named '_tkinter', please install the python3-tk
    package``

    This may occur when trying to generate plots in the server without a graphical
    interface. This leads to an error when trying to import the module
    `matplotlib.pyplot`. To avoid this, make sure to use a non-interactive
    backend such as `agg`. In short, add the following lines to your script
    before importing pyphoon.

    >>> import matplotlib
    >>> matplotlib.use('agg')

..  todo::

    Create a pyphoon method that does this internally, e.g.

    >>> import pyphoon
    >>> pyphoon.use('agg')

-----

What is Jupyter?
----------------
Jupyter is an web environment that provides an interactive python
sort-of-terminal. We use it throughout the whole project to provide some
example usages of the code (found on the `project github repo`_. Info may be
found
`here`_

..  _project github repo:
    https://github.com/lucasrodes/pyphoon/tree/master/notebooks

..  _here:
    http://jupyter.org/

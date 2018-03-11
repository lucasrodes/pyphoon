pyphoon: Python interface for Digital Typhoon
=============================================

.. image:: _static/banner2.png


You just found pyphoon
----------------------

`pyphoon`_ is a python library developed
since 2017 by interns at `Kitamoto Lab`_ to provide simple, easy and, more
importantly, a pythonic interaction with the `Digital Typhoon`_ dataset. It
contains a wide set of tools to assist in the exploration and management of 
the building components of the dataset. More details on the
`GitHub repository`_.

.. _pyphoon: http://github.com/lucasrodes/pyphoon
.. _Kitamoto Lab: http://agora.ex.nii.ac.jp/~kitamoto/index.html.en
.. _GitHub repository: http://github.com/lucasrodes/pyphoon

-----

What is Digital Typhoon?
------------------------

The `Digital Typhoon`_ project is an open project started by `Prof. Kitamoto`_,
which integrates different typhoon data sources. It provides more than 200,
000 typhoon satellite images since 1979 and typhoon best tracks since 1951. 
By doing so, the Digital Typhoon project project attempts to assist the 
scientific community in its  attempts to use data-driven and data-mining 
techniques on typhoon data.

.. _Digital Typhoon: http://agora.ex.nii.ac.jp/digital-typhoon/
.. _Prof. Kitamoto: http://www.nii.ac.jp/en/faculty/digital_content/kitamoto_asanobu/

-----

Where do I get the data?
------------------------

This project only makes sense if you have access to the Digital Typhoon
dataset. Before installing the library make sure you have the data.

..  todo::

    Add guideline for dataset inquiries.

-----

Installation
------------

Clone the repository

.. code-block:: bash

   # Create project folder
   mkdir ~/projects
   # Clone pyphoon
   git clone https://github.com/lucasrodes/pyphoon.git

Pull the project's docker image

.. code-block:: bash

   docker pull lucasrodesg/deepo


To re-create the optimal working environment, refer to `Environment <environment>`_.

-----

Development
-----------

The development of the project occurs on `Github`_.

.. _GitHub: http://github.com/lucasrodes/pyphoon

-----

Support
-------

You can post any bug reports and feature requests in `Github issues`_. Upon
demand other communication platforms may be opened.

As for now, `lucasrodes`_ and `alex2gk`_ are the responsible of the project
development.

.. _Github issues: http://github.com/lucasrodes/pyphoon/issues
.. _lucasrodes: http://github.com/lucasrodes
.. _alex2gk: http://github.com/alex2gk

-----

Why name pyphoon?
-----------------

Well, we think the name explains for itself. We had some doubts, either
**pyphoon** or **pythoon**, but finally went for **pyphoon**. For the record 
and in our defense, we leave this video `here`_.

.. _here: https://www.youtube.com/watch?v=Gtlm9sJFVEk

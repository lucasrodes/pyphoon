Examples
========

1. Integrating the data
---------------------------

The Digital Typhoon data is build from two main sources:

- **Satellite imagery:** Images of typhoons taken from several geostationary satellites since 1978.
- **Best Track:** Several parameters of typhoons.

Both components originally come in two different formats. All images
belonging to the a certain typhoon sequence are stored as HDF files under
the same folder. The best track data comes as TSV files (one per sequence also).
Therefore, the number of folders of images and TSV files should be the equal
to the number of considered typhoon sequences.


1.1 Generate a TyphoonSequence HDF File
***************************************

This library provides a set of tools to integrate both sources into
single HDF files.

.. literalinclude:: _static/examples/generate_hdf_files.py
    :linenos:
    :language: python

2. Dataset overview
-------------------

Having a high-level overview of the dataset may provide interesting insights.

2.1 Image distribution
**********************

2.1 Mean image
**************
It is interesting to obtain the mean image of the image dataset. In large
datasets, like Digital Typhoon's, loading all the data is not possible.
Hence, the mean image has to be sequentially obtained.

We can easily obtain the deviation image, the maximum value image and minimum
value image as they do not require much more additional power.

.. literalinclude:: _static/examples/mean_image.py
    :linenos:
    :language: python

3. Corrupted files
------------------

Digital Typhoon is a project that aims to tackle a real-world issue. Hence,
it contains real-world data, which often contains some errors. Finding and
correcting those errors becomes essential so as to be able to rely on the
given data.

3.1 Corrupted images
********************

The following example finds the corrupted frames in all sequences under the
directory ``data/integration_0`` and stores them as images under
``data/corrupted_0``.

.. literalinclude:: _static/examples/corrupted_images.py
    :linenos:
    :language: python

O
Examples
========

Here we present some examples using the tools from the library. You can find
these examples `here`_.

.. _here:
    https://github.com/lucasrodes/pyphoon/tree/master/scripts

**Contents:**

| :ref:`integrating-the-data`
|   :ref:`generate-a-typhoonsequence-hdf-file`
| :ref:`dataset-overview`
|   :ref:`mean-image`
|   :ref:`visualize-a-typhoonsequence`
| :ref:`corrupted_files`
|   :ref:`corrupted-images`


.. _integrating-the-data:

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


.. _generate-a-typhoonsequence-hdf-file:

1.1 Generate a TyphoonSequence HDF File
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This library provides a set of tools to integrate both sources into
single HDF files. For this example, we suppose have the satellite images at
`../original_data/image/` and the best track data at `../original_data/jma/`
and that we want to create the integrated dataset at `../data/integration_0`.

.. literalinclude:: ../../scripts/generate_hdf_files.py
    :linenos:
    :language: python

We note that :func:`~pyphoon.utils.io.TyphoonSequence.save_as_h5` has an
option to save the data in a compressed format.

.. note::
    `script <https://github
    .com/lucasrodes/pyphoon/tree/master/scripts/generate_hdf_files.py>`_

.. _dataset-overview:

2. Dataset overview
-------------------

Having a high-level overview of the dataset may provide interesting insights.

.. _mean-image:

2.1 Mean image
^^^^^^^^^^^^^^
It is interesting to obtain the mean image of the image dataset. In large
datasets, like Digital Typhoon's, loading all the data is not possible.
Hence, the mean image has to be sequentially obtained.

We can easily obtain the deviation image, the maximum value image and minimum
value image as they do not require much more additional power.

For this example, we use the already generated TyphoonSequence HDF files
stored in `../data/integration_0` and store the results in `../data/`.

.. literalinclude:: ../../scripts/mean_image.py
    :linenos:
    :language: python

.. note::
    `script <https://github
    .com/lucasrodes/pyphoon/tree/master/scripts/mean_image.py>`_

.. _visualize-a-typhoonsequence:

2.2 Visualize a TyphoonList
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Visualizing a sequence can be sometimes helpful. In the following example we
visualize the sequence **197906** stored at `../sampledata/197906.h5`.
However, note that this can be extended to any other typhoon sequence.

.. literalinclude:: ../../scripts/visualize_sequence.py
    :linenos:
    :language: python

.. note::
    `script <https://github
    .com/lucasrodes/pyphoon/tree/master/scripts/visualize_sequence.py>`_,
    `notebook <https://github
    .com/lucasrodes/pyphoon/tree/master/notebooks/Getting_Started.ipynb>`_

.. _corrupted_files:

3. Corrupted files
------------------

Digital Typhoon is a project that aims to tackle a real-world issue. Hence,
it contains real-world data, which often contains some errors. Finding and
correcting those errors becomes essential so as to be able to rely on the
given data.

.. _corrupted-images:

3.1 Corrupted images
^^^^^^^^^^^^^^^^^^^^

The following example finds the corrupted frames in all sequences under the
directory ``data/integration_0`` and stores them as images under
``data/corrupted_0``.

.. literalinclude:: ../../scripts/corrupted_images.py
    :linenos:
    :language: python

.. note::
    `script <https://github
    .com/lucasrodes/pyphoon/tree/master/scripts/corrupted_images.py>`_
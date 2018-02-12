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
single HDF files. For this example, we assume the following paths for the
respective data sources.

*   **Satellite images:** Directory with all satellite imagery folders (one
per sequence), ``../original_data/image/``
*   **Best track data:** Directory with a TSV file per sequence, ``../original_data/jma/``

In the code example below, we generate three different datasets:

*   **Original data:** Sequences stored as single H5 files. Placed at ``../data/sequences/compressed_1/``
*   **Corrected data:** Sequences stored as single H5 files with corrected
    satellite imagery. Placed at ``../data/sequences/corrected_1/``
*   **Gapfilled data:** Sequences stored as single H5 files with corrected
    satellite imagery and image temporal gaps filled with synthetic frames.
    Placed at ``../data/sequences/gapfilled_1/``

We note that we store all the HDF generated files using compression.

.. literalinclude:: ../../scripts/generate_hdf_files.py
    :linenos:
    :language: python

We note that :func:`~pyphoon.io.__init__.TyphoonList.save_as_h5` has an
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
Hence, the mean image has to be sequentially obtained. We can easily obtain
the deviation image, the maximum value image and minimum value image as they
do not require much more additional computation.

For this example, we use the already generated datasets. In particular we
will use the corrected version, stored at ``../data/sequences/corrected_1/``.
 The resulting images wil be stored at ``../data/params/params_1``.

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
visualize the sequence **197906** stored at ``../sampledata/197906.h5``.
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

To find the corrupted files in our dataset, we employ the method
:func:`~pyphoon.clean.__init__.find_corrupted_frames_1`, which implements a
very simple approach for detecting possible corrupted pixels. For this
example, we use the data in ``../data/sequences/compressed_1`` as dataset and
store the images considered as *corrupted* at ``../data/iter_n``.

.. literalinclude:: ../../scripts/find_corrupted_images.py
    :linenos:
    :language: python

.. note::
    `script <https://github
    .com/lucasrodes/pyphoon/tree/master/scripts/find_corrupted_images.py>`_
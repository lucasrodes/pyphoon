Building the Dataset
====================

In this project, we use *Digital Typhoon* data for different tasks. Below we
describe how we build the respective datasets for each task.


1. Tropical Cyclone vs. Extra-Tropical Cyclone
----------------------------------------------

Typhoons are categorised in 5 different categories. On the one hand,
categories 2, 3, 4 and 5 refer to different intensity levels of Typhoons
(Tropical Cyclones). On the other hand, category 6 stands for another natural
phenomenon known as *Extra-Tropical Cyclone*. Details on the diferences
between both phenomena can be found `here <http://www.aoml.noaa
.gov/hrd/tcfaq/A7.html>`_ and `here <http://www.hko.gov
.hk/education/edu01met/01met_tropical_cyclones/ele_typhoon3_e.htm>`_.

1.1 Generating the dataset
^^^^^^^^^^^^^^^^^^^^^^^^^^

For this task, we label tropical cyclones as 0 and extra-tropical
cyclones as 1. We note that from the original dataset, only 12% of the
data is extra-topical. Hence, using all the dataset would lead to a high
imbalance in the class category. To overcome this, we consider all
extra-TC samples but only a subset of TC samples, so as to have a 50/50
dataset.

The following script builds the dataset, assuming the typhoon sequences are
located at ``../data/sequences/corrected_1/`` it places the newly generated
dataset at ``../data/datasets/task_1/original_512``. The new dataset
contains, roughly, 37,000 samples and stores them in chunks of 5% of the
data (i.e. one chunk contains approximately 37,000/20 samples).


.. literalinclude:: ../../scripts/build_dataset_1.py
:linenos:
:language: python

.. note::
    `script <https://github.com/lucasrodes/pyphoon/tree/master/scripts/build_dataset_1.py>`_

1.2 Scaling dataset
^^^^^^^^^^^^^^^^^^^

To reduce the computational complexity of this task, we scale the images
from 512x512 to 256x256. As input it uses the files stored at ``.
./data/datasets/task_1/original_512`` and places the new scaled versions
at ``../data/datasets/task_1/original_256``

.. literalinclude:: ../../scripts/scale_256.py
    :linenos:
    :language: python

.. note::
    `script <https://github.com/lucasrodes/pyphoon/tree/master/scripts/scale_256.py>`_


1.3 Spliting dataset
^^^^^^^^^^^^^^^^^^^^

As already explained before, the dataset is stored in chunks of 5% of
data. Hence, we just need to select some chunks for training and some for
test. Each chunk contains all images from certain typhoon sequences, thus
ensuring that the dataset is splitted at sequence-level. After verifying
that each chunk contains 50/50 of both categories, we proceed to randomly
select 4 chunks for testing (20% of data) and rest for training (80%).

*       **Training**: Chunks 1 - 13
*       **Validation**: Chunks 14, 15
*       **Test**: Chunks 16 - 19

1.4 Normalizing dataset
^^^^^^^^^^^^^^^^^^^^^^^

With the dataset built, we can proceed to compute the mean of the pixel
values to correctly normalise the dataset using training-only information.

We obtain **mean = 269.159150451** and **std = 24.1441119965**, more details
`here <https://github.com/lucasrodes/pyphoon/tree/master/notebooks/notebooks/EDA_task1.ipynb>`_.

We perform standard normalization: *(X - mean)/std*.



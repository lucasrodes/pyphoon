Create database
===============

For our needs, we created a batch of tools to generate an easy interaction
with the Digital Typhoon data. In particular, we exploited the functionality
of pandas.DataFrame objects to track which images have been corrected and
other relevant image features. The core interface here is :class:`~pyphoon.db.pd_manager.PDManager`.

>>> from pyphoon.db import pd_manager
>>> pd_man = pd_manager.PDManager()

Original image data
-------------------

Assuming that ``orig_images_dir`` is a string containing the path to the
original source images (as explained in section `Data <data.html>`_), you can
load them using the method :func:`~pyphoon.db.pd_manager.PDManager.add_orig_images`.

>>> pd_man.add_original_images(orig_images_dir)

This method creates an internal DataFrame representation of the original
image data. You may have a look at as

>>> pd_man.original_images.head()

Furthermore, you may want to save this table as a pickle file in
``images_pkl_path`` using

>>> pd_man.pkl_save_original_images(images_pkl_path)

In subsequent executions, you can load this table by using

>>> pd_man.pkl_load_original_images(images_pkl_path)

Best track data
---------------

Assuming that ``besttrack_dir`` is a string containing the path to the
best track data (as explained in section `Data <data.html>`_), you can
load this data using the method :func:`~pyphoon.db.pd_manager.PDManager.add_besttrack`.

>>> pd_man.add_besttrack(besttrack_dir)

This method creates an internal DataFrame representation of the best track
data. You may have a look at as

>>> pd_man.besttrack.head()

Furthermore, you may want to save this table as a pickle file in
``besttrack_pkl_path`` using

>>> pd_man.pkl_save_besttrack(besttrack_pkl_path)

In subsequent executions, you can load this table by using

>>> pd_man.pkl_load_besttrack(besttrack_pkl_path)

Corrected image data
--------------------

To include corrupted image data in :class:`~pyphoon.db.pd_manager.PDManager`
you need to first generate the dataset of the corrected versions of the
originally corrupted images. To do so, you need to refer to method
:func:`~pyphoon.clean_datellite.fix.generate_new_image_dataset`.

Define Fix Algorithm
********************

As pointed out in `Data <data.html>`_, we first need to define the fixing
algorithm

>>> from pyphoon.clean_satellite.correction import correct_corrupted_pixels_1
>>> from pyphoon.clean_satellite.detection import detect_corrupted_pixels_1
>>> from pyphoon.clean_satellite.generation import generate_new_frames_1
>>> from pyphoon.clean_satellite.fix import TyphoonListImageFixAlgorithm
>>> # Define Fixing algorithm
>>> fix_algorithm = TyphoonListImageFixAlgorithm(
...    detect_fct=detect_corrupted_pixels_1,
...    correct_fct=correct_corrupted_pixels_1,
...    detect_params={'min_th': 160, 'max_th': 310},
...    n_frames_th=2
...)


Generate new dataset
********************

Once the algorithm is defined, let us apply generate the new dataset using
method :func:`~pyphoon.clean_satellite.fix.generate_new_image_dataset`. Replace
``images_orig_dir`` with the directory of original images and
``images_corrected_dir`` with the directory for the new corrected data.

>>> from pyphoon.clean_satellite.fix import generate_corrected_image_dataset
>>> generate_new_image_dataset(images_orig_dir=images_orig_dir,
...                            fix_algorithm=fix_algorithm,
...                            images_corrected_dir=images_corrected_dir,
...                            display=True
...                            )

Add new dataset info to PDManager
*********************************

Once the dataset is created, its information can be easily imported to
``pd_man`` as

>>> pd_man.add_corrupted_images(images_dir=corrected_dir)

Like other table fields, you can save the table using

>>> pkl_save_corrupted_images(corrupted_pkl_path)

and load

>>> pkl_load_corrupted_images(corrupted_pkl_path)
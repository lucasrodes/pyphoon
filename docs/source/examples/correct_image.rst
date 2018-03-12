Correcting image data
=====================

Image data may come with some corrupted pixel values, probably due to some
technical failure in the data sources (i.e. the satellites). Such data can
contaminate later applied statistical methods and thus should either be
removed or corrected. To this end, this library attempts to provide a set of
tools to fix such problems.

..  note::

    In the future we plan to add methods to correct other sorts of data types.

In this example we assume we have a sequence loaded. To learn how to, check
this `example <typhoon_sequence.html#load-a-typhoon-sequence-data>`_.


Define and apply fixing algorithm
----------------------------------

There can be up to three main steps when fixing a sequence:

*   **detection**: Detect image frames with corrupted pixel values.
*   **correction**: Correct the corrupted pixel values in detected image frames.
*   **fillgaps**: Generate synthetic images to fill temporal gaps. For
    instance, if two images are 3 hour apart, it means that there are two frames
    missing in between, since the observation frequency is supposed to be of 1h.
    Hence, with some methods, we can artificially generate the images that
    should occupy this temporal space.

Each of the above techniques may be implemented using different algorithms.
These can be found in the modules :mod:`pyphoon.clean.detection`,
:mod:`pyphoon.clean.correction` and :mod:`pyphoon.clean.fillgaps`,
respectively. A fixing algorithm is defined using the class
:class:`~pyphoon.clean.fix.TyphoonListImageFixAlgorithm`. This class, accepts
as arguments methods for **detection**, **correction** and **fillgap**. There
is no need to use all of them, so one might decide to only perform, for
instance, detection and correction.

>>> from pyphoon.clean.fix import TyphoonListImageFixAlgorithm
>>> from pyphoon.clean.detection import detect_corrupted_pixels_1
>>> from pyphoon.clean.correction import correct_corrupted_pixels_1
>>> from pyphoon.clean.fillgaps import generate_new_frames_1
>>> # Define algorithm
>>> fix_algorithm = TyphoonListImageFixAlgorithm(
...    detect_fct=detect_corrupted_pixels_1,
...    correct_fct=correct_corrupted_pixels_1,
...    fillgaps_fct=generate_new_frames_1,
...    detect_params={'min_th': 160, 'max_th': 310},
...    n_frames_th=2
...)

To apply the algorithm simply use method :func:`~pyphoon.clean.fix.TyphoonListImageFixAlgorithm.apply`.

>>> sequence_corrected = fix_algorithm.apply(sequence)
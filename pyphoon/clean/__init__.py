"""
Typhoon sequences might come with some corrupted images, mainly due to
technical failures in the sensors collecting the data. Such data can
contaminate later applied statistical methods and thus should either be
removed or corrected. To this end, this library attempts to provide a set of
tools to fix such problems.

.. note:: In the future, this library should provide tools to, not only
    correct corrupted images but other sorts of data

**Getting started**


In this example we will fix a sequence by using method
:func:`~pyphoon.clean.detection.detect_corrupted_pixels_1` to detect
corrupted frames,
:func:`~pyphoon.clean.correction.correct_corrupted_pixels_1` to correct
those and :func:`~pyphoon.clean.fillgaps.generate_new_frames_1` to
generate new frames in order to fill some temporal gaps.

>>> from pyphoon.clean.fix import TyphoonListImageFixAlgorithm
>>> from pyphoon.clean.detection import detect_corrupted_pixels_1
>>> from pyphoon.clean.correction import correct_corrupted_pixels_1
>>> from pyphoon.clean.fillgaps import generate_new_frames_1

Once the aforementioned methods are loaded, we can define an instance of
``TyphoonListFixAlgorithm``. Note the parameter ``params``,
which contains information related to the detection and fillgaps
methods.

>>> fix_algorithm = TyphoonListImageFixAlgorithm(
    detect_fct=detect_corrupted_pixels_1,
    correct_fct=correct_corrupted_pixels_1,
    fillgaps_fct=generate_new_frames_1,
    detect_params={'min_th': 160, 'max_th': 310},
    n_frames_th=2
)

Finally, we load the typhoon images from
``../original_data/image/199607`` as a
:class:`~pyphoon.io.typhoonlist.TyphoonList` instance and apply the fix
algorithm to it.

>>> from pyphoon.io.typhoonlist import create_typhoonlist_from_source
>>> seq = create_typhoonlist_from_source('../original_data/image/199607')
>>> seq_fixed = fix_algorithm.apply(seq)

**Modules**

+-------------------------------------------+-----------------------------------------------------------+
| module                                    | Description                                               |
+===========================================+===========================================================+
| :mod:`pyphoon.clean.fix`                  | Used to define the Fixing algorithm                       |
+-------------------------------------------+-----------------------------------------------------------+
| :mod:`pyphoon.clean.detection`            | Provides set of algorithms to detect corrupted frames     |
+-------------------------------------------+-----------------------------------------------------------+
| :mod:`pyphoon.clean.correction`           | Provides set of algorithms to correct corrupted frames    |
+-------------------------------------------+-----------------------------------------------------------+
| :mod:`pyphoon.clean.fillgaps`             | Provides set of algorithms to fill the temporal gaps      |
+-------------------------------------------+-----------------------------------------------------------+

"""
Typhoon sequence
================

This library provides the class :class:`~pyphoon.io.typhoonlist.TyphoonList`,
which makes it really easy to integrate different data sources and generate a
single object for a given sequence. Make sure to replace ``path_image`` with
the path of the directory containing all sequence image folders,
``typhoon_id`` with the typhoon sequence id (e.g. 201725) and ``path_best``
with the directory path containing all sequence's TSV best data files.


Load a typhoon sequence data
----------------------------

Loading typhoon data from a specific sequence is done with the method
:func:`~pyphoon.io.typhoonlist.create_typhoonlist_from_source`. You
can read only image data

>>> from pyphoon.io.typhoonlist import create_typhoonlist_from_source
>>> from os.path import join
>>> sequence = create_typhoonlist_from_source(
...    name=typhoon_id,
...    images=join(path_image, typhoon_id)
...)

or also include best data

>>> from pyphoon.io.typhoonlist import create_typhoonlist_from_source
>>> from os.path import join
>>> sequence = create_typhoonlist_from_source(
...    name=typhoon_id,
...    images=join(path_image, typhoon_id),
...    best=join(path_best, typhoon_id, '.tsv')
...)

-----

Visualise a typhoon sequence
----------------------------

Plotting one specific image frame from the sequence is rather easy. Just use
the method :func:`~pyphoon.io.typhoonlist.TyphoonList.get_data` from
:class:`~pyphoon.io.typhoonlist.TyphoonList`.

>>> import matplotlib.pyplot as plt
>>> plt.imshow(sequence.get_data('images')[10], cmap="Greys")
>>> plt.show()

You can easily display all the image frames in a typhoon sequence using the
class :class:`~pyphoon.visualize.DisplaySequence`.

>>> from pyphoon.visualize import DisplaySequence
>>> DisplaySequence(
...    typhoon_sequence=sequence,
...    interval=100
...).run

If you want to display the sequence in a Jupyter notebook use the method
:func:`~pyphoon.visualize.DisplaySequence.run_html` instead as

>>> from pyphoon.visualize import DisplaySequence
>>> from IPython.display import HTML
>>> HTML(DisplaySequence(
...    typhoon_sequence=sequence,
...    interval=100
...).run_html())

-----

Export typhoon sequence
-----------------------

A :class:`~pyphoon.io.typhoonlist.TyphoonList` instance can be stored as a
single HDF file using its method :func:`~pyphoon.io.typhoonlist.TyphoonList.save_as_h5`.

>>> sequence.save_as_h5(join(path_new_data, typhoon_id, '.h5'), compression='gzip')

Likewise, we can load the stored h5 file using the method
:func:`~pyphoon.io.typhoonlist.load_typhoonlist_h5`.

>>> from pyphoon.io.typhoonlist import load_typhoonlist_h5
>>> sequence = load_typhoonlist_h5(join(path_new_data, typhoon_id, '.h5'))


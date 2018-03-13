Typhoon sequence
================

Sometimes it may be interesting to visualise a single typhoon sequence.
Luckily, this can be easily done with the module :mod:`pyphoon.visualise`. In
this example we will show first how to load the data related to a typhoon
sequence and next we will show how to animate the list of images!

Make sure to replace ``path_image`` with the path of the directory containing
all sequence image folders, ``sequence_no`` with the typhoon sequence
identifier (e.g. 201725) and ``path_best`` with the directory path containing
all sequence's TSV best data files.


Load typhoon sequence data
----------------------------

In this example we use the library methods to load the data, which assume
that you follow the same data structure presented in section `Data <data>`_.
If that is not the case, feel free to implement your own loading functions.
Note that the data, once loaded, should be of type ``list``.


On the one hand, to load the typhoon image data we use methods
:func:`~pyphoon.io.h5.read_source_images` and :func:`~pyphoon.io.utils.get_image_ids`,
which load the images and get their correspoding sample ids, respectively.
Each sample is identified by a unique **ids**, which is constructed using the
sequence identifier of the sequence that frame belongs to and the date the
sample data was registered.


>>> from pyphoon.io.h5 import read_source_images
>>> from pyphoon.io.utils import get_image_ids
>>> images = read_source_images(join(path_image, sequence_no))
>>> images_ids = get_image_ids(join(path_image, sequence_no))

Above, ``images`` is a list containing the images of the sequence as arrays and
``image_ids`` is a list with the corresponding image sample ids.

On the other hand, we load best data is done similarly, using methods
:func:`~pyphoon.io.tsv.read_tsv` and :func:`~pyphoon.io.utils.get_best_ids`.

>>> from pyphoon.io.tsv import read_tsv
>>> from pyphoon.io.utils import get_best_ids
>>> best = read_tsv(join(path_best, sequence_no))
>>> best_ids = get_best_ids(image)

Above, ``best`` is a list containing the best data of each sample in the
typhoon sequence. Likewise, ``best_ids`` contains the corresponding sample ids.


-----

Visualise a typhoon sequence
----------------------------

Plotting one specific image frame from the sequence is rather easy.

>>> import matplotlib.pyplot as plt
>>> plt.imshow(images[10], cmap="Greys")
>>> plt.title(images_ids[10])
>>> plt.show()

You can easily display all the image frames in a typhoon sequence using the
class :class:`~pyphoon.visualize.DisplaySequence`.

>>> from pyphoon.visualize import DisplaySequence
>>> DisplaySequence(
...    images=images,
...    images_ids=images_ids,
...    name=sequence_no,
...    interval=100
...).run

If you want to display the sequence in a Jupyter notebook use the method
:func:`~pyphoon.visualize.DisplaySequence.run_html` instead as

>>> from pyphoon.visualize import DisplaySequence
>>> from IPython.display import HTML
>>> HTML(DisplaySequence(
...    images=images,
...    images_ids=images_ids,
...    name=sequence_no,
...    interval=100
...).run_html())

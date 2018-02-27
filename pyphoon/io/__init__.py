"""
Digital Typhoon data comes, at the moment, from two sources:

*   **Satellite images**: 512x512 infrared images, with the typhoon eye at the
    image centre. Each typhoon sequence's images come as folders with their
    respective images as H5 files.
*   **Best Track data**: Provided by `JMA
    <http://www.jma.go.jp/jma/indexe.html>`_, it contains data characterizing
    the state of a certain typhoon. There is data since 1951. Each typhoon
    sequence's data comes in a TSV file.

To this end, this module provides a set of tools to integrate the different
sources and ease the interaction with those.

+-------------------------------------------+-------------------------------------------------------------------------------+
| module                                    | Description                                                                   |
+===========================================+===============================================================================+
| :mod:`pyphoon.io.typhoonlist`             | Methods and classes related to :class:`~pyphoon.io.typhoonlist.TyphoonList`   |
+-------------------------------------------+-------------------------------------------------------------------------------+
| :mod:`pyphoon.io.h5`                      | Reading and writing operations on H5 files.                                   |
+-------------------------------------------+-------------------------------------------------------------------------------+
| :mod:`pyphoon.io.tsv`                     | Reading and writing operations                                                |
+-------------------------------------------+-------------------------------------------------------------------------------+
| :mod:`pyphoon.io.utils`                   | Other tools                                                                   |
+-------------------------------------------+-------------------------------------------------------------------------------+
"""
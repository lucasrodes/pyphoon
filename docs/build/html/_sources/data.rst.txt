Data
====

The original data we are provided with is arranged in a very specific fashion.
There are two main sources of data: (i) satellite imagery and (ii) best track
data, which we briefly describe below. Details on the data sources can be
found in the `official Digital Typhoon website`_.

..   _official Digital Typhoon website:
    http://agora.ex.nii.ac.jp/digital-typhoon/about-data.html.en

Satellite imagery
-----------------

Satellite images are stored individually as HDF5 files with the following
naming convention:

    ..  code::
        YYYYMMDDHH-<typhoon id>-<satellite model>.h5

An example of this is ``1998091906-199808-GMS5-1.h5``, which is an image
taken the 19th of September 1998 at 6AM with GMS5 satellite and belonging to
sequence `199808`_.

..  _199808:
    http://agora.ex.nii.ac.jp/digital-typhoon/summary/wnp/s/199808.html.en


In addition, they are arranged in folders according to the typhoon sequence
they belong to. Below we illustrate this hierarchy.

    ..  code::

        path/to/image/data
        |-  197801/
        |   |-  image1.h5
            |-  image2.h5
            :
        |-  197901/
            :
        |-  197902/
        |   :
        :

Consecutive images in a sequence are usually 1 hour apart, but some
exceptions may arise. The images are of shape 512x512 and the pixel value
encodes the temperature (K).

----

Best Track data
---------------

Best Track data contains different parameters from typhoon sequences. A
direct match between this data and satellite images can be established
provided that sample dates coincide. Some of the parameters included in this
dataset are the wind speed, centre pressure, latitude and longitude (full
list can be found `here`_).

..  _here:
    http://www.jma.go.jp/jma/jma-eng/jma-center/rsmc-hp-pub-eg/Besttracks/e_format_bst.html

**Note**: This data is obtained every 6h, hence there is an observation
frequency miss-match with satellite imagery data. Therefore, spline
interpolation has been used `[1]`_ to align this data with the image
counterparts. As a consequence, only 16.6% of Best Track data is actual real
data.

..  _[1]:
    https://pdfs.semanticscholar.org/21c9/707d0a9dd362dacf99c49f7c2e5d92a1fadf.pdf

The data comes in .TSV format per typhoon sequence with name convention
``<typhoon_seq_no>.tsv``, e.g.

    ..  code::

        path/to/best/data
        |-  197801.tsv
        |-  197901.tsv
        |-  197902.tsv
        :

----

How to get the data
-------------------

Please address to `Kitamoto-sensei`_

..  _Kitamoto-sensei:
    https://www.nii.ac.jp/en/faculty/digital_content/kitamoto_asanobu/
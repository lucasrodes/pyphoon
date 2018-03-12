Data
====

..  todo::

    develop information

Satellite imagery
-----------------

*   Folder for each typhoon sequence with images in hdf format:

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

*   Usually 1h observation frequency (may change).
*   512x512, pixel intesity = temperature (K).

-----

Best Track data
---------------

*   some: wind speed, centre pressure, geo-location, class...
*   6h observation frequency: interpolation to catch up with images:
    We note that only 16.6% of Best Track data is real data, since the rest
    has been previously artificially generated through spline interpolation
    so that it can be aligned  with satellite imagery frequency observation.
*   come as one tsv file for each typhoon sequence:

    ..  code::

        path/to/best/data
        |-  197801.tsv
        |-  197901.tsv
        |-  197902.tsv
        :

How to get the data
-------------------

TODO
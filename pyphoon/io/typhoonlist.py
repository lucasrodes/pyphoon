"""
This module contains one of the most important and essential components of the
library, namely the class :class:`~pyphoon.io.typhoonlist.TyphoonList`,
which enables easy analysis and integration of data (e.g. HDF and TSV files)
related to a specific typhoon sequence.

Getting Started
^^^^^
Creating a TyphoonList object is very easy. It can be generated using only
the image data.
>>> from pyphoon.io.typhoonlist import create_typhoonlist_from_source
>>> typhoon_sequence = create_typhoonlist_from_source(
    images='../original_data/image/199607/'
    )

Additionally, if best data is available, the object can be created using it.

>>> typhoon_sequence = create_typhoonlist_from_source(
    images='../original_data/image/199607/',
    best='../original_data/jma/199607/'
    )

A TyphoonList object can be easily exported as a H5 file.

>>> typhoon_sequence.save_as_h5("../data/199607.h5")

Such new generated H5 file can be loaded again as a :class:`TyphoonList`.

>>> from pyphoon.io.typhoonlist import load_typhoonlist_h5
>>> typhoon_sequence = load_typhoonlist_h5(path_to_file="../data/199607.h5")

Once a sequence is loaded, you may want to plot a specific frame. it is very
simple. Only need to set a start and end frames and an interval (time between
frames) value.

>>> import matplotlib.pyplot as plt
>>> plt.imshow(typhoon_sequence.images[10])
>>> plt.show()

Contents
^^^^^
+-------------------------------------------+---------------------------------------------------------------------------------------------------+
| method/class name                         | Description                                                                                       |
+===========================================+===================================================================================================+
| :class:`TyphoonList`                      | Class encapsulating images and best track data of a certain typhoon sequence                      |
+-------------------------------------------+---------------------------------------------------------------------------------------------------+
| :func:`create_typhoonlist_from_source`    | Creation of a :class:`TyphoonList` instance using best track and satellite image data sources     |
+-------------------------------------------+---------------------------------------------------------------------------------------------------+
| :func:`read_typhoonlist_h5`               | Load previously stored (as H5) typhoon sequence data as a :class:`TyphoonList` instance           |
+-------------------------------------------+---------------------------------------------------------------------------------------------------+

Methods and classes
^^^^^
"""

from pyphoon.io.h5 import write_h5groupfile, read_h5groupfile, \
    read_source_images
from pyphoon.io.tsv import read_tsv
from pyphoon.io.utils import id2date, date2id
from pyphoon.io.utils import get_best_ids, get_image_ids, h5file_2_name, \
    folder_2_name
import numpy as np
import warnings
import collections, ast, h5py


class TyphoonList(object):
    """ Object encapsulating the images and, optionally, other data sources,
    (e.g. best track data) of a certain typhoon sequence.

    :var data: Dictionary-shape data. The details on the shape of the
        dictionary are according to the output format of :func:`read_h5file`.
    :var name: Name of the sequence (str).
    """

    def __init__(self, data, name):
        self.data = data
        self.name = name

    ############################################################################
    #  DATA ACCESS
    ############################################################################
    def fields(self):
        """ A TyphoonList instance can have several fields available. These
        include:

            * images: Array with the sequence image data.
            * best: Array with the sequence best track data.

        :return: List with the keys of the available fields. These keys can
            then be used as the key argument in function :func:`get`.
        :rtype: list
        """
        return list(self.data.keys())

    # TODO: datetime type
    def get_data(self, key, date=None, id=None):
        """ Returns the data from the specified field. If a date or id is
        specified, only a specific element is returned.

        :param key: Field name of the data to be returned.
        :type key: str
        :param date: Set to a date to retrieve the typhoon happening by then.
            This field prevails in case argument ``id`` is also used.
        :type date: datetime.datetime
        :param id: Set to an id to retrieve the typhoon with that id.
        :type id: str
        :return: Data corresponding to ``key``. Single sample if ``date`` or
            ``id`` are used.
        """
        # Return all data
        if not date and not id:
            return self.data[key]['data']
        # Return data from specified date
        elif date:
            id = date2id(date, self.name)
            idx = self.data[key]['ids'][id]
            return self.data[key]['data'][idx]
        # Return data from specified id
        elif id:
            idx = self.data[key]['ids'][id]
            return self.data[key]['data'][idx]

    def get_id(self, key):
        """ Similarly to :func:`get_data`, this method returns the list of ids
        corresponding to a specific data field specified by ``key``.

        :param key: Field to retrieve ids from.
        :type key: str
        :return: List with ids.
        :rtype: list
        """
        return list(self.data[key]['ids'].keys())

    def get_date(self, key):
        """ Similarly to :func:`get_data` and :func:`get_id`, this method
        returns the list of dates corresponding to a specific data field
        specified by ``key``.

        :param key: Field to retrieve dates from.
        :type key: str
        :return: List with dates.
        :rtype: list
        """
        return [id2date(id) for id in self.get_id(key)]

    def get_sample_distance(self, key, idx_0, idx_1):
        """ Obtains the distance between samples idx_0 and idx_1 from data
        field specified by ``key``. Distance is measured in slots of 1h,
        i.e. a distance of 2 means that both sampels are two hours apart. By
        default, distance of 1 is expected since the maximum observation
        frequency is of 1 hour.

        :param key: Frame distance can be obtained from different sources. To
            this end, you can specify the which field to look at using ``key``.
        :type key: str
        :param idx_0: Index of first frame.
        :type idx_0: int
        :param idx_1: Index of second frame.
        :type idx_1: int
        :return: Time distance between frames in hours.
        :rtype: int
        """
        date_frame_0 = self.get_date(key)[idx_0]
        date_frame_1 = self.get_date(key)[idx_1]
        # Get time distance between identifiers
        return int((date_frame_1 - date_frame_0).total_seconds() // 3600)

    def insert_samples(self, key, new_samples, idx):
        """ Insert a batch of new samples  at a certain position from a
        certain data field (specified by ``key``).

        :param key: Key of the field to introduce the new data in.
        :type key: str
        :param new_samples: List of new samples to be inserted.
        :type new_samples: list
        :param idx: Position at which samples are to be inserted.
        :type idx: int
        """
        # TODO: Insert in image array is very slow!
        # Insert frames
        #self.data[key]['data'] = np.insert(self.data[key]['data'], idx,
        #                                   new_samples, axis=0)
        self.data[key]['data'][idx:idx] = new_samples
        #self.data[key]['data'] = np.append(self.data[key]['data'],
        #                                   new_samples, axis=0)
        # Insert ids
        #keys = list(self.data[key]['ids'].keys())
        #values = list(self.data[key]['ids'].values())
        #original_length = len(keys)

        #keys[idx:idx] = new_ids
        #values[idx:] = range(values[idx-1], len(new_ids) + original_length)

        #self.data[key]['ids'] = dict(zip(keys, values))

    def insert_ids(self, key, new_ids):
        """ Insert new ids. Exploits the fact that they can easily be sorted,
        since they follow a numerical order (date based).

        :param key: Key of the field to introduce the new data in.
        :type key: str
        :param new_ids: List of new ids corresponding to the new samples.
        :type new_ids: list
        :return:
        """
        keys = sorted(list(self.data[key]['ids'].keys()) + new_ids)
        self.data[key]['ids'] = dict(zip(keys, range(len(keys))))


    ############################################################################
    #  STORING
    ############################################################################
    def save_as_h5(self, path_to_file, compression=None):
        """ Stores the data as an HDF file.

        :param path_to_file: Path to the directory where typhoon sequence data
            will be stored.
        :type path_to_file: str
        :param compression: Set to a compression format. Find more details at
            the `h5py documentation`_
        :type compression: str, default None
        .. _h5py documentation:
            http://docs.h5py.org/en/latest/high/dataset.html
        """

        write_h5groupfile(self.data, path_to_file, compression=compression)

    ############################################################################
    #  OBJECT properties
    ############################################################################
    # TODO: revise (generalization to new features)
    @property
    def shape(self, key=None):
        """ Returns shape of typhoonlist as a dictionary, where each key
        stands for a data field and its corresponding value comes as a tuple:
        (shape_of_data, shape_of_ids).

        :return: Shape of typhoonlist
        :rtype: dict
        """
        shape = {}
        if key is None:
            for key, value in self.data.items():
                shape[key] = np.shape(value['data'])
        else:
            shape[key] = np.shape(self.data[key]['data'])
        return shape


#######################################
#        READ/WRITE TYPHOONLIST       #
#######################################
# TODO: Generalize input paths (for new features)
def create_typhoonlist_from_source(name, alignment=False, **kwargs):
    """ Groups the images and best track data from a certain typhoon and
    generates a `TyphoonList` instance. As input it requires an HDF
    file containing the images from a certain typhoon sequence an,
    optionally, a TSV file with best track data of the same typhoon
    sequence.
    This function is very relevant when it comes to merging the two main data
    components of this dataset: Images (folder with h5 files) and Best
    Track (TSV file).

    :param name: Name of the typhoon sequence
    :type name: str
    :param kwargs: Use the keys to define the available data sources paths.
        This include:

        * images: Path to image dataset.
        * best: Path to best track data.
    :param alignment: Set to True if all fields should contain same data (id
        based).
    :type alignment: bool
    :return: Object containing images and bes track data
    of a
    typhoon sequence.
    :rtype: TyphoonList
    .. seealso:: :class:`TyphoonList`
    """
    data = {}

    for key, value in kwargs.items():
        if key == 'images':
            # Get the images from the HDF file and their corresponding IDs.
            _data = read_source_images(value)
            data['images'] = {
                'data': _data,
                'ids': dict(zip(get_image_ids(value), range(len(_data)))),
            }

        elif key == 'best':
            # Get the best track data from the TSV file and their
            # corresponding IDs. Also, detect samples in best data belonging
            # to existing image frames in the sequence
            Y = np.array(read_tsv(value))
            ids = get_best_ids(Y, name)

            # Alignment
            if alignment and data['images']:
                indices = []
                for i in range(len(ids)):
                    if ids[i] in data['images']['ids']:
                        indices.append(i)
                Y = Y[indices]
                ids = np.array(ids)[indices].tolist()

            data['best'] = {
                'data': Y,
                'ids': dict(zip(ids, range(len(Y))))
            }

    return TyphoonList(data, name=name)


# TODO: Preserve name of typhoon!
def load_typhoonlist_h5(path_to_file, alignment=False):
    """ Loads a typhoon sequence stored as an H5 file as an instance of
    TyphoonList.

    :param path_to_file: Path to the HDF file to load.
    :type path_to_file: str
    :param alignment: Set to True if frames and best data are to be
    aligned.
    :type alignment: bool
    :return: Object containing images and bes track data of a typhoon sequence.
    :rtype: TyphoonList instance

    .. seealso:: :class:`TyphoonList`
    """
    # Read H5 file
    data = collections.defaultdict(dict)

    with h5py.File(path_to_file, 'r') as hf:
        for key, value in hf.items():
            data[key]['data'] = value.get('data').value
            data[key]['ids'] = ast.literal_eval(value.get('ids').value)
    data = dict(data)

    # Align data
    # TODO: Extend to other features
    if alignment:
        pass

    # Obtain Sequence name
    name = h5file_2_name(path_to_file)

    # Create object
    sequence = TyphoonList(data, name=name)

    return sequence


################################################################################
# DEPRACATED
################################################################################
# Johny M. Reggae artist
# TODO: Refactor completely!
def read_typhoonlist_h5(path_to_file, path_images=None, overwrite_ids=False,
                        overwrite_flags=False, alignment=False):
    """ Loads a typhoon sequence stored as an HDF file as an instance of
    TyphoonList. The loaded data is assumed to have, at least,
    one field corresponding to the images (X) and another to the
    corresponding best track metadata (Y). Additionally, it may have ids.

    :param path_to_file: Path to the HDF file to load.
    :type path_to_file: str
    :param path_images: Path to the original image folder (i.e. folder
        containing image H5 files). This path is relevant if the IDs or dates of
        any of the data (images or best data) are to be set. Otherwise ignore.
    :type path_images: str, optional
    :param overwrite_ids: Set to True if the loaded typhoon sequence does
    have IDs already but you want to overwrite them.
    :type overwrite_ids: bool
    :param overwrite_flags:
    :type overwrite_flags:
    :param alignment: Set to True if frames and best data are to be
    aligned.
    :type alignment: bool
    :return: Object containing images and bes track data of a typhoon sequence.
    :rtype: TyphoonList instance

    .. seealso:: Depracated for :func:`load_typhoonlist_h5`
    """
    warnings.warn("deprecated, use write_h5groupfile() instead",
                  DeprecationWarning)
    # Read HDF file
    data = read_h5groupfile(path_to_file)

    # Get typhoon sequence name
    if path_images:
        seq_name = folder_2_name(path_images)
    else:
        seq_name = ""

    # Only consider best data referring to existing image frames in the sequence
    # IDs
    if overwrite_ids:
        data['images_ids'] = get_image_ids(path_images)
        data['best_ids'] = get_best_ids(data['Y'], seq_name)
    else:
        if 'images_ids' not in data and path_images:
            data['images_ids'] = get_image_ids(path_images)
        if 'best_ids' not in data:
            data['best_ids'] = get_best_ids(data['Y'], seq_name)

    # FLAGs (Add/Overwrite flag-columns to best data array)
    if data['best'].shape[1] == 20:
        data['best'] = np.append(data['Y'], np.zeros((data['Y'].shape[0],
                                                      2)), axis=1)
        data['best'][:, -2] = [best_id in data['images_ids'] for best_id in
                               data['best_ids']]
    if overwrite_flags and data['Y'].shape[1] == 22:
        data['best'][:, -2] = [best_id in data['images_ids'] for best_id in
                               data['best_ids']]
        data['best'][:, -1] = np.zeros((data['best'].shape[0], 1))

    if alignment:
        pos = [flag == 1 for flag in data['best'][:, -2]]
        data['best'] = data['Y'][pos]
        data['best_ids'] = list(np.array(data['best_ids'])[pos])

        # Ensure that all image have associated best data!
        data['images'] = \
            np.array([data['images'][i] for i in range(len(data['images']))
                      if data['images_ids'][i] in data['best_ids']])
        data['images_ids'] = [image_id for image_id in data['images_ids'] if
                              image_id in data['best_ids']]
    # Obtain Sequence name
    name = h5file_2_name(path_to_file)
    return TyphoonList(data, name=name)
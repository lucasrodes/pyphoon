from pyphoon.io.utils import id2date


def get_sample_distance(id_0, id_1):
    """ Obtains the distance between samples idx_0 and idx_1 from data
    field specified by ``key``. Distance is measured in slots of 1h,
    i.e. a distance of 2 means that both sampels are two hours apart. By
    default, distance of 1 is expected since the maximum observation
    frequency is of 1 hour.

    :param ids: Frame distance can be obtained from different sources. To
        this end, you can specify the which field to look at using ``key``.
    :type ids: str
    :param id_0: Id of first frame.
    :type id_0: str
    :param id_1: Id of second frame.
    :type id_1: str
    :return: Time distance between frames in hours.
    :rtype: int
    """
    date_frame_0 = id2date(id_0)
    date_frame_1 = id2date(id_1)
    # Get time distance between identifiers
    return int((date_frame_1 - date_frame_0).total_seconds() // 3600)


# TODO: get_date <-> get_id
def generate_image_ids(id_0, id_1, n_frames=1):
    """ Generates ids of n_frames in between positions ``frame_idx_0`` and
    ``frame_idx_1``. This is useful when new image frames have been generated
    through interpolation and require an id.

    :param image_ids: List of image ids
    :type image_ids: list
    :param frame_idx_0: Index of first frame
    :type frame_idx_0: int
    :param frame_idx_1: Index of second frame
    :type frame_idx_1: int
    :param n_frames: Number of frames for which an id has to be generated.
    :return: List of newly generated ids.
    :rtype: list
    """
    dif = id2date(id_1) - id2date(id_0)

    name = id_0.split('_')[0]
    ids_new = [
        name + "_" + (
            id2date(id_0) + (n + 1) / (n_frames + 1) *
            dif).strftime("%Y%m%d%H") for n in
        range(n_frames)
    ]

    return ids_new
"""
This script generates an animation of a stream of frames. Useful to see the evolution of a typhoon sequence or a single
typhoon image
"""


from pyphoon.utils.io import read_h5file, load_TyphoonSequence, \
    create_TyphoonSequence, TyphoonSequence

# PARSER
"""
parser = argparse.ArgumentParser()
parser.add_argument("directory", help="Add directory containing the hdf5 files")
args = parser.parse_args()
directory_path = args.directory
"""
option = 2

if option == 1:
    # FOLDER
    path = 'original_data/image/201626/'
    typhoon_sequence = create_TyphoonSequence(path)
    typhoon_sequence.visualize()
elif option == 2:
    # H5 FILE
    path = "data/199114.h5"
    typhoon_sequence = load_TyphoonSequence(path)
    typhoon_sequence.visualize(start_frame=40, end_frame=50, interval=1000)
"""
elif option == 3:
    # DATA ARRAY
    path = "data/201626.h5"
    data = read_h5file(path)
    typhoon_sequence = TyphoonSequence(data=data)
    DisplaySequence(typhoon_sequence).generate_gif()
elif option == 4:
    # Global params
    path = "data/201626.h5"
    data = read_h5file(path)
    DisplaySequence(TyphoonSequence(data=data)).run()
"""
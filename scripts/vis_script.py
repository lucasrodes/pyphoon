"""
This script generates an animation of a stream of frames. Useful to see the evolution of a typhoon sequence or a single
typhoon image
"""


from vis import DisplayImage
from utils import read_h5file

# PARSER
"""
parser = argparse.ArgumentParser()
parser.add_argument("directory", help="Add directory containing the hdf5 files")
args = parser.parse_args()
directory_path = args.directory
"""
option = 2

if option == 1:
    # OPTION 1
    directory_path = 'data/image/201626/'
    visualization = DisplayImage(directory=directory_path)
    visualization.run()
elif option == 2:
    # OPTION 2
    X, Y = read_h5file("197901.h5")
    visualization = DisplayImage(data=X)
    visualization.run()

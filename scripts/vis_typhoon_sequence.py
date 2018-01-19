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
    # FOLDER
    path = 'original_data/image/201626/'
    visualization = DisplayImage(folder_path=path)
    visualization.run()
elif option == 2:
    # H5 FILE
    path = "data/201626.h5"
    visualization = DisplayImage(h5file_path=path)
    visualization.run()
elif option == 3:
    # DATA ARRAY
    path = "data/201626.h5"
    data = read_h5file(path)
    visualization = DisplayImage(data=data['X'], id=data['name'])
    visualization.generate_gif()
elif option==4:
    # Global params
    path = "data/global_params.h5"
    data = read_h5file(path)
    visualization = DisplayImage(data=np.array(data['mean']), id=data['name'])
    visualization.run()

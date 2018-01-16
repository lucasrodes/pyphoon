"""
This script generates an animation of a stream of frames. Useful to see the evolution of a typhoon
"""


from vis import DisplayImage
import argparse

# PARSER
"""
parser = argparse.ArgumentParser()
parser.add_argument("directory", help="Add directory containing the hdf5 files")
args = parser.parse_args()
directory_path = args.directory
"""
# CREATE OBJECT
directory_path = '../data/201626/'
visualization = DisplayImage(directory_path)
visualization.run()

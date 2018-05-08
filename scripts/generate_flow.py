import sys
sys.path.insert(0, '..')

from pyphoon.interpolation.flow_generator import FlowGenerator

input_dir = '/root/fs9/grishin/database/uintimages/original'
flow_dir = '/root/fs9/grishin/database/flow_per_image_256x256'

if __name__ == '__main__':
    flow_gen = FlowGenerator(input_dir, flow_dir, (256, 256))
    flow_gen.generate_flow(display=True)

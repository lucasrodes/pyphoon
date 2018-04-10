from pyphoon.db.data_convertor import convert_dir

src_dir1 = '/root/fs9/datasets/typhoon/wnp/image/'
dst_dir1 = '/root/fs9/grishin/database/uintimages/original/'
src_dir2 = '/root/fs9/grishin/database/corrected/'
dst_dir2 = '/root/fs9/grishin/database/uintimages/corrected/'

convert_dir(src_dir1, dst_dir1, True)
convert_dir(src_dir2, dst_dir2, True)

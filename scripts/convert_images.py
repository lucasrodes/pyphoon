from pyphoon.db.data_convertor import convert_dir, process_folder

src_dir1 = '/root/fs9/datasets/typhoon/wnp/image/'
dst_dir1 = '/root/fs9/grishin/database/uintimages/original/'
src_dir2 = '/root/fs9/grishin/database/corrected/'
dst_dir2 = '/root/fs9/grishin/database/uintimages/corrected/'

print('Start')
process_folder(True, '199709', src_dir1, dst_dir1)
process_folder(True, '199709', src_dir2, dst_dir2)
# convert_dir(src_dir1, dst_dir1, False)
# convert_dir(src_dir2, dst_dir2, False)
print('Done')


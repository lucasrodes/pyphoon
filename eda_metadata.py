import numpy as np
from os import listdir
from os.path import isfile, join


def read_metadata(path='../typhoon-data/jma/'):
	files = listdir(path)
	metadata = []
	for f in files:
		f = join(path, f)
		if isfile(f):
			ff = open(f, 'r').readlines()
			for fff in ff:
				_metadata = fff.split('\t')
				_metadata[-1] = _metadata[-1].split('\n')[0]
				__metadata = list(map(float, _metadata))
				index = [0, 1, 2, 3, 4]
				for i in index:
					__metadata[i] = int(__metadata[i])
				__metadata[-1] = bool(__metadata[-1])	
				metadata.append(__metadata)
	return metadata	

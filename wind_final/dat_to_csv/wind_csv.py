import csv, glob, os, tarfile
import numpy as np
from tqdm import tqdm

def readfile(fname):
	f = "<f"
	dt = np.dtype([("u",f), ("v",f), ("slp",f)])
	fd = open(fname,"r")
	result = np.fromfile(fd, dtype=dt, count=145*145)
	return result


#read each file in 'input_binary' and save the csv file to './output_csv'
files = [os.path.basename(r) for r in glob.glob('input_binary/*')]
for f in tqdm(files):
	fname = './input_binary/' + f
	result = readfile(fname)
	sname = './output_csv/' + f[0:9] + '.csv'
	np.savetxt(sname, result, delimiter=',')
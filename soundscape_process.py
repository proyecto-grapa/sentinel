#!/usr/bin/env python3
import sys
import os
import yaml
import requests
import argparse
import numpy as np
from datetime import datetime, timedelta

sys.path.append('/home/pi/')
import acoustic_field.soundscape as sc

now = datetime.now()
hostname = os.uname().nodename
parser = argparse.ArgumentParser()

parser.add_argument('--date', dest='date',type=str, default='now', help="use date from filename or datetime now (default)")
args = parser.parse_args()

with open('/home/pi/sentinel/configs/options.yaml') as file:
	opt = yaml.load(file, Loader=yaml.FullLoader)

if (args.date == 'now'):
	tlast = now
else:
	dn=[int(s) for s in args.date.split('/')[-1].split('.')[0].split('_')]
	tlast = datetime(dn[0],dn[1],dn[2],dn[3],dn[4],dn[5])

dump = np.frombuffer(sys.stdin.buffer.read(), dtype='u1', count=-1)
nsamples=dump.shape[0]//(opt['nchan']*opt['nbytes'])
nmax = 2**(opt['nbytes']*8-1)
if opt['nbytes']==4:
	data=np.reshape(dump.view(np.int32)/nmax,(nsamples,opt['nchan'])).astype('float64') 
elif opt['nbytes']==2:
	data=np.reshape(dump.view(np.int16)/nmax,(nsamples,opt['nchan'])).astype('float32')
elif opt['nbytes']==1:
    data=np.reshape(dump.view(np.int8)/nmax,(nsamples,opt['nchan'])).astype('float32')
else:
	raise Exception("Only 4,2 or 1 bytes allowed")

with open('/home/pi/acoustic_field/config/defaults.yaml') as file:
    par = yaml.load(file, Loader=yaml.FullLoader)

if par['hipass']:
	data[:,0] = soundscape.hipass_filter(data[:,0],**par['Filtering'])

spec = sc.spectrogram(data[:,0],**par['Spectrogram'])
# recalculate values of windows based on the number of samples 
HW = int(np.floor(par['Indices']['window']*par['sr']/(par['windowSize'])))
par['Indices']['half_window'] = HW
NOWF = int(np.floor(spec['nsamples'] / par['windowSize']))
par['Indices']['number_of_windows'] = int(np.floor((NOWF-HW)/HW))

# compute time intervals
ind = sc.indices(spec,**par['Indices'])
dur = ind['nsamples']/par['sr']
indt = dur - ind['t']
tlist = [tlast - timedelta(seconds=t.item()) for t in indt]
# write to stdout
par_str = 'time=' + ",".join([t.strftime("%Y-%m-%dT%H:%M:%SZ") for t in tlist])
for k in opt['pkeys']:
	par_str += '&' + k.upper() + '=' + ",".join([str(np.around(s,decimals=3)) for s in ind[k][0,:]]) 
print(par_str)
with open(opt['GSM']['queue'], "a") as fp:
    fp.write(par_str + '\n')

#write to logfile
logfile_name = opt['logfile'] + hostname + '_' + opt['sesion'] + '.csv'
with open(logfile_name, "a") as fp:
	for n,t in enumerate(tlist):
		csvline = t.strftime("%Y-%m-%dT%H:%M:%SZ") + ","
		csvline += ",".join([str(np.around(ind[k][0,n],decimals=3)) for k in opt['pkeys']]) + "\n"
		fp.write(csvline)	

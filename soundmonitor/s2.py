#!/usr/bin/python
 
print "also hello there!"
import time
 
import numpy as np
import seaborn as sns
import pandas as pd
print "importing matplotlib"
import matplotlib
print "finished importing matplotlib"
print "importing pylab"
import pylab
print "finished importing pylab"
from os import listdir as listdir
from datetime import datetime
from datetime import timedelta
from dateutil.parser import parse
import glob
import os
import ftplib
 
def myFormatter(x,pos):
return pd.to_datetime(x)
 
current_time = datetime.now()
 
#combined_dataframe = pd.DataFrame(columns=np.arange(60).tolist())
combined_dataframe = pd.DataFrame()
x_index = []
list_of_filenames = []
print combined_dataframe
 
sns.set(color_codes=True)
 
list_of_filenames.append(glob.glob('/home/pi/Documents/sound_level_records/' + time.strftime("%Y_%m_%d",current_time.timetuple()) + '*'))
list_of_filenames.append(glob.glob('/home/pi/Documents/sound_level_records/' + time.strftime("%Y_%m_%d",(current_time-timedelta(days=1)).timetuple()) + '*'))
list_of_filenames = [item for sublist in list_of_filenames for item in sublist]
 
print len(list_of_filenames)
 
#import data from each minute
for filename in list_of_filenames:
x_ordered_title = datetime.strptime(os.path.basename(filename), '%Y_%m_%d_%H_%M')
time_difference = current_time-x_ordered_title
if time_difference.days*86400+time_difference.seconds&amp;amp;lt;86400: #24 hours
x = pd.read_csv(filename, header=None, names=['timestamp','dB'])
x_ordered = x.sort('dB')
x_ordered_data = x_ordered['dB'].tolist()
if len(x_ordered_data) == 60:
x_dataframe = pd.DataFrame(np.reshape(x_ordered['dB'].tolist(),(1,60)))
x_index.append(x_ordered_title)
combined_dataframe = combined_dataframe.append(x_dataframe)
combined_dataframe.index = x_index
combined_dataframe = combined_dataframe.sort()
combined_dataframe.sort_index(inplace = True)
 
fig = matplotlib.pyplot.figure(dpi = 200, figsize = (10,10))
jet = matplotlib.pyplot.get_cmap('jet')
cNorm = matplotlib.colors.Normalize(vmin=1, vmax=60)
scalarMap = matplotlib.cm.ScalarMappable(norm=cNorm, cmap=jet)
 
for count in range(2,58):
colorVal = scalarMap.to_rgba(count)
fig = matplotlib.pyplot.plot(combined_dataframe.index,combined_dataframe.xs(count,axis=1), linewidth = 0.5, color=colorVal)
 
pylab.savefig('/home/pi/Documents/Sound_meter_graphs/test.png')
try:
ftp = ftplib.FTP("davidjohnhewlett.co.uk","user","password")
ftp.set_pasv = False
ftp.cwd("/public_html/sound_levels/")
f_file = open('/home/pi/Documents/Sound_meter_graphs/test.png','rb')
ftp.storbinary('STOR test.png', f_file)
ftp.close()
except:
print "oh dear"
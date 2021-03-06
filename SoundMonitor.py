#! /usr/bin/env python3 amir2
import serial
import os, sys
import threading
import queue
import datetime
import time
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)

if os.path.exists('/run/shm/example.txt'): # note log currently saved to RAM if log = 1
   os.remove('/run/shm/example.txt')       # gets deleted as you restart the script

ser = serial.Serial(port='/dev/ttyAMA0',baudrate = 9600,parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=1)

# set variables
global xs,y1,y2,y3,y4,y5,max_count,count,list_lock,start
max_count = 360
count = 0
log = 1 # set log to 1 to save a log in RAM.
xs = []
y1 = []
y2 = []
y3 = []
y4 = []
y5 = []
start = 1
list_lock = 0

def onclick(x):
   global start
   start = 0

#kill the toolbar
plt.rcParams['toolbar'] = 'None'

# beautify
plt.style.use('seaborn-darkgrid')
plt.rc('figure', facecolor='darkgrey')
plt.rc('figure.subplot', left=0.05, right=0.98, top=0.98, bottom=0.1)
plt.rc('xtick', labelsize=7)     
plt.rc('ytick', labelsize=7)
plt.rc('lines', linewidth=1)
plt.rc('legend', frameon=True, loc='upper left', facecolor='white', framealpha=0.5, fontsize=7)
plt.rc('font', size=7)
plt.ioff()
      
def thread_plot():
    global fig,animate, ax1
    fig = plt.figure()
    ax1 = fig.add_subplot(1,1,1)
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    ani = animation.FuncAnimation(fig, animate, interval=10000)
    plt.show()
   
def animate(i):
    global xs,y1,y2,y3,y4,y5,max_count,count,list_lock,start
    if count > 0 and start == 1:
        ax1.clear()
        plt.xlabel('Time') 
        plt.ylabel('dB')
        ax1.xaxis.set_major_locator(MultipleLocator(30))
        ax1.xaxis.set_minor_locator(MultipleLocator(10))
        while list_lock == 1:
            time.sleep(0.01)
        list_lock = 1
        ax1.plot(xs, y1, '-.b', label='Avg')
        ax1.plot(xs, y2, '-r', label='A0')
        ax1.plot(xs, y3, '-g', label='A0Slow')
        ax1.plot(xs, y4, ':c', label='Min')
        ax1.plot(xs, y5, ':y', label='Max')
        ax1.legend(loc='upper left')
        plt.gcf().autofmt_xdate()
        list_lock = 0
    if count > 0 and start == 0:
       plt.close('all')

if __name__ == '__main__':
   
  plot_thread = threading.Thread(target=thread_plot)
  plot_thread.start()

  while start == 1:
    #read data from arduino
    Ard_data = ser.readline()
    Ard_data = Ard_data.decode("utf-8","ignore")
    counter1 = Ard_data.count(' ')
    counter2 = Ard_data.count('.')
    # check for 4 spaces  and 5 data vaules
    if counter1 == 4 and counter2 == 5:
      now = datetime.datetime.now()
      t = str(now)[11:19]
      b,c,d,e,f= Ard_data.split(" ")
      # save to log file
      if log == 1:
          timestamp = now.strftime("%y/%m/%d-%H:%M:%S")
          with open('/run/shm/example.txt', 'a') as g:
              g.write(timestamp + "," + str(count)+"," + Ard_data)
      # write to lists
      while list_lock == 1:
          time.sleep(0.01)
      list_lock = 1
      xs.append(t)
      y1.append(float(b))
      y2.append(float(c))
      y3.append(float(d))
      y4.append(float(e))
      y5.append(float(f))
      # delete old list values
      if len(xs) > max_count:
            del xs[0]
            del y1[0]
            del y2[0]
            del y3[0]
            del y4[0]
            del y5[0]
      list_lock = 0
      count +=1
    else:
       print("error")
       if log == 1:
          now = datetime.datetime.now()
          timestamp = now.strftime("%y/%m/%d-%H:%M:%S")
          with open('/run/shm/example.txt', 'a') as g:
              g.write("error " + timestamp + "," + str(count)+"," + Ard_data + "\n")
  
  ser.close()
  sys.exit()
  
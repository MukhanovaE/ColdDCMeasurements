import numpy as np

from sys import exit, argv
import time
from datetime import datetime
import pandas as pd
import os
import threading

from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import LinearSegmentedColormap

from Drivers.LakeShore370 import *
from Lib.lm_utils import *

device_id = int(sys.argv[1])

LakeShore = LakeShore370(device_num=device_id, mode='passive')


# behavior on program exit - save data
f_exit = threading.Event()


pw = plotWindow("Temperature control", color_buttons=False)

channels = [6, 2, 3, 5]
tabs = []
times_arrays = []
temps_arrays = []
ts = []


def onChange():
    tab_now = pw.CurrentTab
    LakeShore.temp_channel = channels[tab_now]


for ch in channels:
    tabTemp = pw.addLine2D(f'Channel {ch}', 'Time', 'T, K')
    tabs.append(tabTemp)
    times_arrays.append([])
    temps_arrays.append([])
    ts.append(0)
pw.addOnChange(onChange)
LakeShore.temp_channel = channels[0]


def UpdateRealtimeThermometer():
    global times_arrays, temps_arrays, ts, LakeShore, pw
    tab_now = pw.CurrentTab
    
    T_curr = LakeShore.GetTemperature()
    times_arrays[tab_now].append(ts[tab_now])
    ts[tab_now] += 1
    temps_arrays[tab_now].append(T_curr)
    
    if ts[tab_now] > 1000:
        temps_arrays[tab_now] = temps_arrays[tab_now][-1000:]  # keep memory and make plot to move left
        times_arrays[tab_now] = times_arrays[tab_now][-1000:]

    axT = pw.Axes[tab_now]
    axT.clear()
    axT.plot(times_arrays[tab_now], temps_arrays[tab_now])
    axT.set_title(f'T={T_curr}')
    pw.canvases[tab_now].draw()


def TemperatureThreadProc():
    while not f_exit.is_set():
        UpdateRealtimeThermometer()
        time.sleep(1.5)


thermometer_thread = threading.Thread(target=TemperatureThreadProc)
thermometer_thread.start()

pw.show()  # show main tabbed window

f_exit.set()

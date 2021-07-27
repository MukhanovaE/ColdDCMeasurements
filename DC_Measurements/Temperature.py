import numpy as np
import time
import threading
import argparse
from matplotlib import pyplot as plt

from Drivers.LakeShore370 import *
from Drivers.LakeShore335 import *
from Lib.lm_utils import *

parser = argparse.ArgumentParser()
parser.add_argument('-LT', action='store', required=False, default=LAKESHORE_MODEL_370)
parser.add_argument('-L', action='store', required=True)
args, unknown = parser.parse_known_args()
device_id = int(args.L)
lakeshore_model = int(args.LT)

LakeShore = LakeShore370(device_num=device_id, mode='passive', control_channel=6) if lakeshore_model == LAKESHORE_MODEL_370 \
    else LakeShore335(device_num=device_id, mode='passive', control_channel='A', heater_channel=1)

f_exit = threading.Event()
pw = plotWindow("Temperature control", color_buttons=False)

channels = [6, 2, 3, 5] if lakeshore_model == LAKESHORE_MODEL_370 else ['A', 'B']
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

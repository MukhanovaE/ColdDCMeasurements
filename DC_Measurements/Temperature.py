import numpy as np
import time
import threading
from matplotlib import pyplot as plt

from Drivers.Keithley2000 import *
from Drivers.Keithley224 import *
from Drivers.VirtualLakeShore import *
from Lib.lm_utils import *


def UpdateRealtimeThermometer():
    global time_array, temp_array, t, LakeShore, pw

    T_curr = LakeShore.GetTemperature()
    time_array.append(t)
    temp_array.append(T_curr)
    
    if t > 1000:
        temp_array = temp_array[-1000:]  # keep memory and make plot to move left
        time_array = time_array[-1000:]

    axT = pw.Axes[tabTemp]
    axT.clear()
    axT.plot(time_array, temp_array)
    axT.set_title(f'T={T_curr}')
    pw.canvases[0].draw()
    t += 1

def TemperatureThreadProc():
    while not f_exit.is_set():
        UpdateRealtimeThermometer()
        time.sleep(1)


parser = argparse.ArgumentParser()
parser.add_argument('-TR', action='store', required=True)  # readout device ID
parser.add_argument('-TE', action='store', required=True)  # excitation device ID
args, unknown = parser.parse_known_args()
readout_id = int(args.TR)
excitation_id = int(args.TE)

ls_sense = Keithley2000(device_num=readout_id)
ls_source = Keithley224(device_num=excitation_id)

LakeShore = VirtualLakeShore(sense_device=ls_sense, sweep_device=ls_source, heater_device=None, mode='passive')

f_exit = threading.Event()
pw = plotWindow("Temperature control", color_buttons=False)

time_array = []
temp_array = []
t = 0
tabTemp = pw.addLine2D(f'Temperature', 'Time', 'T, K')

thermometer_thread = threading.Thread(target=TemperatureThreadProc)
thermometer_thread.start()

pw.show()  # show main tabbed window
f_exit.set()

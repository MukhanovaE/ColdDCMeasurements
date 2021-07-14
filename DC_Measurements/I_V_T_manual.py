import numpy as np
from scipy.optimize import curve_fit
from matplotlib import pyplot as plt

import os
import time
from datetime import datetime
from copy import copy
from datetime import datetime
import threading
from tkinter import TclError

from Drivers.Leonardo import *
from Drivers.Yokogawa import *
from Drivers.Keithley2182A import *
from Drivers.Keithley6200 import *

from Lib.lm_utils import *


# User input
# ------------------------------------------------------------------------------------------------------------
k_A, k_V_meas, k_R, R, rangeA, stepA, gain, step_delay, num_samples, I_units, V_units, f_save, yok_read, yok_write, \
    ls, read_device_type, exc_device_type, read_device_id, user_params = ParseCommandLine()
Log = Logger(R, k_R, 'I_V_T')
Log.AddGenericEntry(
    f'CurrentRange={(rangeA / R) / k_A} {core_units[k_A]}A; CurrentStep={(stepA / R) / k_A} {core_units[k_A]}A; '
    f'Gain={gain}; IVPointDelay={step_delay} sec; LeonardoPoints={num_samples}')
# ------------------------------------------------------------------------------------------------------------
k_temp = 1000  # to millikelvin from logged value
T = 0  # current measurement temperature
Leonardo = LeonardoMeasurer(n_samples=num_samples) if read_device_type == READOUT_LEONARDO \
    else Keithley2182A(device_num=read_device_id)
Yokogawa = YokogawaMeasurer(device_num=yok_read, dev_range='1E+1', what='VOLT') if exc_device_type == EXCITATION_YOKOGAWA \
    else Keithley6200(device_num=yok_read, what='VOLT', R=R)

f_exit = False
f_save = False

# all Yokogawa generated values (always in volts!!!)
upper_line_1 = np.arange(0, rangeA, stepA)
down_line_1 = np.arange(rangeA, -rangeA, -stepA)
upper_line_2 = np.arange(-rangeA, 0, stepA)

voltValues0 = np.hstack((upper_line_1,
                         down_line_1,
                         upper_line_2))

voltValues = []
currValues = []


def DataSave():
    global f_save
    if not f_save:
        return
    if not isTemperatureObtained.is_set():
        print('Waiting newest logs to get current temperature...')
    isTemperatureObtained.wait()
    SaveData({f'I, {I_units}A': currValues,
              f'U, {I_units}V': voltValues, 'T, mK': [T] * len(currValues)},
             R, caption=f"I_V_T_{T}", k_A=k_A, k_V_meas=k_V_meas, k_R=k_R)
    f_save = True

    Log.Save()

    # upload to cloud services
    UploadToClouds(GetSaveFolder(R, k_R, caption))

# Procedure after window closed - write results to a file
def OnClose(e):
    global f_exit
    DataSave()
    f_exit = True


# Load a temperature from BlueFors software logs
def LoadTemperatureThreadProc():
    global T
    T = LoadTemperatureFromLogs()
    isTemperatureObtained.set()
    print('T=', T, 'mK')


@MeasurementProc(lambda: Yokogawa.SetOutput(0))
def Measurement():
    for volt in voltValues0:
        Yokogawa.SetOutput(volt)
        time.sleep(step_delay)

        V_meas = Leonardo.MeasureNow(6) / gain
        voltValues.append(V_meas / k_V_meas)  # volts / coeff
        currValues.append((volt / R) / k_A)  # (volts/Ohms always) / coeff

        # resistance measurement
        if volt < lower_R_bound or volt > upper_R_bound:
            R_IValues.append(volt / R)  # Amperes forever!
            R_UValues.append(V_meas)
            UpdateResistance(ax1, np.array(R_IValues) * k_A, np.array(R_UValues) * k_V_meas)

        line.set_xdata(currValues)
        line.set_ydata(voltValues)
        ax1.relim()
        ax1.autoscale_view()
        try:
            plt.pause(0.05)
        except TclError:  # don't throw exception after plot closure
            pass
        if f_exit:
            break


# Initialize a plot
plt.ion()
fig, ax1 = plt.subplots(figsize=(14, 8))
fig.canvas.mpl_connect('close_event', OnClose)
line, = ax1.plot([], [])
ax1.set_ylabel(fr"$U, {core_units[k_V_meas]}V$", fontsize=15)
ax1.set_xlabel(fr'$I, {core_units[k_A]}A$', fontsize=15)
ax1.grid()
fig.show()

print('Measurement started.\nTotal points:', len(currValues))
print('When all points wil be measured, data will be saved automatically.')
print('Close a plot window to stop measurement and save only currently obtained data.')

# lists of values used for counting R
percentage_R = 0.1  # how many percents left-right will be used to measure R
fraction_R = int(len(voltValues0) * ((1 / 3) * 2 * percentage_R))  # in how many points R will be measured
count_R = 0
R_IValues = [0]
R_UValues = [0]

# Real-time resistance measurement
lower_R_bound = upper_line_2[int(len(upper_line_2) * percentage_R)]
upper_R_bound = upper_line_1[int(len(upper_line_1) * (1 - percentage_R))]

# Perform measures!
isTemperatureObtained = threading.Event()
temperature_thread = threading.Thread(target=LoadTemperatureThreadProc)
temperature_thread.run()
Measurement()

if (not f_save) and b_save:  # if window was not closed
    DataSave()

plt.ioff()
plt.show()

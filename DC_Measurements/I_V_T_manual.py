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

from Lib.lm_utils import *
from Lib.EquipmentBase import EquipmentBase


def DataSave():
    if not shell.f_save:
        return

    caption = f"IV_{T}"

    if not isTemperatureObtained.is_set():
        print('Waiting newest logs to get current temperature...')
    isTemperatureObtained.wait()
    shell.SaveData({f'I, {shell.I_units}A': currValues,
              f'U, {shell.I_units}V': voltValues, 'T, mK': [T] * len(currValues)}, caption=caption)

    Log.Save()

    # upload to cloud services
    UploadToClouds(shell.GetSaveFolder(caption))


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


@MeasurementProc(lambda: iv_sweeper.SetOutput(0))
def Measurement():
    for volt in voltValues0:
        iv_sweeper.SetOutput(volt)
        time.sleep(shell.step_delay)

        V_meas = iv_sweeper.MeasureNow(6) / shell.gain
        voltValues.append(V_meas / shell.k_V_meas)  # volts / coeff
        currValues.append((volt / shell.R) / shell.k_A)  # (volts/Ohms always) / coeff

        # resistance measurement
        if volt < lower_R_bound or volt > upper_R_bound:
            R_IValues.append(volt / shell.R)  # Amperes forever!
            R_UValues.append(V_meas)
            UpdateResistance(ax1, np.array(R_IValues) * shell.k_A, np.array(R_UValues) * shell.k_V_meas)

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


# User input
shell = ScriptShell('IV')
Log = Logger(shell)

k_temp = 1000  # to millikelvin from logged value
T = 0  # current measurement temperature

iv_sweeper = EquipmentBase(shell)
f_exit = False

# all Yokogawa generated values (always in volts!!!)
upper_line_1 = np.arange(0, shell.rangeA, shell.stepA)
down_line_1 = np.arange(shell.rangeA, -shell.rangeA, -shell.stepA)
upper_line_2 = np.arange(-shell.rangeA, 0, shell.stepA)

voltValues0 = np.hstack((upper_line_1,
                         down_line_1,
                         upper_line_2))

voltValues = []
currValues = []

# Initialize a plot
plt.ion()
fig, ax1 = plt.subplots(figsize=(14, 8))
fig.canvas.mpl_connect('close_event', OnClose)
line, = ax1.plot([], [])
ax1.set_ylabel(fr"$U, {core_units[shell.k_V_meas]}V$", fontsize=15)
ax1.set_xlabel(fr'$I, {core_units[shell.k_A]}A$', fontsize=15)
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

DataSave()

plt.ioff()
plt.show()

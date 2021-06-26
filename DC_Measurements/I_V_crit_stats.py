import numpy as np
from scipy.optimize import curve_fit
import matplotlib
matplotlib.use('Qt5Agg')
import pandas as pd
import seaborn

from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

import time
import threading
from sys import exit

from Drivers.Leonardo import *
from Drivers.Yokogawa import *
from Lib.lm_utils import *
import warnings
warnings.filterwarnings("ignore")  # A critical current function may give warnings in case of bad data, delete them

# User input
# ------------------------------------------------------------------------------------------------------------
k_A, k_V_meas, k_R, R, rangeA, stepA, gain, step_delay, num_samples, I_units, V_units, f_save, yok_read, yok_write, ls, user_params = ParseCommandLine()
# ------------------------------------------------------------------------------------------------------------

Leonardo = LeonardoMeasurer(n_samples=num_samples)
Yokogawa = YokogawaMeasurer(device_num=yok_read, dev_range='1E+1', what='VOLT')

# all Yokogawa generated values (always in volts!!!)
upper_line_1 = np.arange(0, rangeA, stepA)
down_line_1 = np.arange(rangeA, -rangeA, -stepA)
upper_line_2 = np.arange(-rangeA, 0, stepA)
voltValues0 = np.hstack((upper_line_1,
                         down_line_1,
                         upper_line_2))
N_points = len(voltValues0)

# Statistics parameters
try:
    N_stats = int(user_params)
except Exception:
    N_stats = 50  # how many I-U curves will be measured
print('Curves to collect: ', N_stats)

# remaining / estimated time
time_mgr = TimeEstimator(N_stats)

# Data receivers
I_values = []
U_values = []
numbers = []

# plot window preparation
pw = plotWindow("Critical currents distribution", color_buttons=False)
tabIV = pw.addEmptyLine2D('I-V', fr'$I, {core_units[k_A]}A$', fr"$U, {core_units[k_V_meas]}V$")
tabStats = pw.addEmptyPlot('Distribution')


def ErrorCleanup():
    Yokogawa.SetOutput(0)


def GetTemperatureThreadProc():
    global T
    T = LoadTemperatureFromLogs()
    is_temp_obtained.set()


@MeasurementProc(ErrorCleanup)
def main_thread():
    stats_array = []

    def MeasureWaveform(N):
        time_mgr.OneSweepStepBegin()

        voltValues = []
        currValues = []
        currValues_IC = []
        voltValues_IC = []

        # plot prepair

        pw.SetHeader(tabIV, f'Critical current variability stats, curve {N + 1} of {N_stats}')
        line = pw.addAdditionalLine(tabIV)

        for nv, volt in enumerate(voltValues0):
            # Measure
            Yokogawa.SetOutput(volt)
            time.sleep(step_delay)

            V_meas = Leonardo.MeasureNow(6) / gain  # volts

            V = V_meas / k_V_meas
            A = (volt / R) / k_A

            # data for plotting only this curve
            voltValues.append(V)  # volts / coeff
            currValues.append(A)  # (volts/Ohms always) / coeff

            # data for saving
            numbers.append(nv + 1)
            I_values.append(A)
            U_values.append(V)

            # only superconductor->normal transfer states
            if nv < N_points // 4 or (nv > N_points // 2 and nv < N_points * 3 // 4):
                voltValues_IC.append(V)
                currValues_IC.append(A)

            # Plot
            pw.updateAdditionalLine2D(tabIV, line, currValues, voltValues)

        voltValues_IC = voltValues_IC[len(voltValues_IC) // 2:][::-1] + voltValues_IC[0:len(voltValues_IC) // 2]
        currValues_IC = currValues_IC[len(currValues_IC) // 2:][::-1] + currValues_IC[0:len(currValues_IC) // 2]
        left_curr, right_curr = FindCriticalCurrent(currValues_IC, voltValues_IC,
                                                    3)  # we are not near superconductivity end - threshold may be big
        print(f'Ic- {left_curr}, Ic+ {right_curr}')
        stats_array.append(right_curr)
        # seaborn.histplot(np.array(stats_array), kde=True, ax=ax2)
        time_mgr.OneSweepStepEnd(N + 1)

    print('Collecting statistics...')
    for i in range(N_stats):
        print('Measured:', i + 1, 'from', N_stats)
        MeasureWaveform(i)

    # Saving data
    save_title = "Stats"
    fname = GetSaveFileName(R, k_R, save_title, 'pdf')
    pp = PdfPages(fname[:-3] + 'pdf')
    pw.SaveFigureToPDF(tabIV, pp)

    seaborn.histplot(np.array(stats_array), kde=True, ax=pw.Axes[tabStats])
    pw.canvases[1].draw()
    pw.SaveFigureToPDF(tabStats, pp)
    pp.close()

    caption = "Ic_stats"
    dict_save = {'number': numbers, f'I, {I_units}A': I_values, f'U, {V_units}V': U_values}
    SaveData(dict_save, R, caption=caption, k_A=k_A, k_V_meas=k_V_meas, k_R=k_R)
    SaveMatrix(numbers, I_values, U_values, f'I, {I_units}A', R, k_R, caption=caption)

    UploadToClouds(GetSaveFolder(R, k_R, save_title))

    exit(0)


# To show temperature on a plot
T = 0
is_temp_obtained = threading.Event()

thermometer_thread = threading.Thread(target=GetTemperatureThreadProc)
thermometer_thread.start()
main_thread = threading.Thread(target=main_thread)
main_thread.start()

pw.show()

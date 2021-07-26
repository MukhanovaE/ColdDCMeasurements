import numpy as np
from scipy.optimize import curve_fit

from sys import exit
import time
from datetime import datetime
import pandas as pd
import os
import threading

from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import LinearSegmentedColormap

from Drivers.Leonardo import *
from Drivers.Yokogawa import *
from Drivers.LakeShore import *
from Drivers.KeysightN51 import *
from Drivers.Keithley2182A import *
from Drivers.Keithley6200 import *

from Lib.lm_utils import *

# User input
# ------------------------------------------------------------------------------------------------------------
k_A, k_V_meas, k_R, R, rangeA, stepA, gain, step_delay, num_samples, I_units, V_units, f_save, yok_read, yok_write, \
    ls, read_device_type, exc_device_type, read_device_id, user_params = ParseCommandLine()
Log = Logger(R, k_R, 'Shapiro')
Log.AddGenericEntry(
    f'CurrentRange={(rangeA / R) / k_A} {core_units[k_A]}A; CurrentStep={(stepA / R) / k_A} {core_units[k_A]}A; '
    f'Gain={gain}; IVPointDelay={step_delay} sec; LeonardoPoints={num_samples}')
# ------------------------------------------------------------------------------------------------------------

# define a program mode (sweep power or frequency) and sweep parameters
try:
    kind, range_start, range_stop, range_step, fixed_value, generator_id = [float(i) for i in user_params.split(';')]
    kind = int(kind)
    swept_range = np.arange(range_start, range_stop, range_step)
except Exception as e:
    print(e)
    range_start, range_stop, range_step, fixed_value, kind, generator_id = -18, 5, 0.5, 2.5, 0, 18
    swept_range = np.arange(range_start, range_stop, range_step)
if kind == MODE_POWER:  # power
    KeysightGenerator = KeysightN51(device_num=generator_id, sweep='power', freq=fixed_value, power_range=swept_range)
    print(f'Sweeping power, in range: [{range_start}, {range_stop}), step is: {range_step}, frequency={fixed_value} GHz')
else:  # 1 - frequency
    KeysightGenerator = KeysightN51(device_num=generator_id, sweep='freq', power=fixed_value, freq_range=swept_range)
    print(f'Sweeping frequency, in range: [{range_start}, {range_stop}), step is: {range_step}, power={fixed_value} dBm')
# Initialize devices
# ------------------------------------------------------------------------------------------------------------
Leonardo = LeonardoMeasurer(n_samples=num_samples) if read_device_type == READOUT_LEONARDO \
    else Keithley2182A(device_num=read_device_id)
Yokogawa_I = YokogawaMeasurer(device_num=yok_read, dev_range='1E+1', what='VOLT') if exc_device_type == EXCITATION_YOKOGAWA \
    else Keithley6200(device_num=yok_read, what='VOLT', R=R)
LakeShore = LakeShoreController(device_num=ls, mode='passive')
# ------------------------------------------------------------------------------------------------------------

# Yokogawa voltage values (will be generated by Yokogawa 1) (always V!!!)
n_points = int(2 * rangeA // stepA)
upper_line_1 = np.linspace(0, rangeA, n_points // 2 + 1)
down_line_1 = np.linspace(rangeA, -rangeA, n_points)
upper_line_2 = np.linspace(-rangeA, 0, n_points // 2 + 1)
voltValues0 = np.hstack((upper_line_1,
                         down_line_1,
                         upper_line_2))


# Custom plot colormaps
R_3D_colormap = LinearSegmentedColormap.from_list("R_3D", [(0, 0, 1), (1, 1, 0), (1, 0, 0)])

# Resistance measurement
# ----------------------------------------------------------------------------------------------------
percentage_R = 0.1  # how many percents left-right will be used to measure R
fraction_R = int(len(voltValues0) * ((1 / 3) * 2 * percentage_R))  # in how many points R will be measured
lower_R_bound = upper_line_2[int(len(upper_line_2) * percentage_R)]
upper_R_bound = upper_line_1[int(len(upper_line_1) * (1 - percentage_R))]
# ------------------------------------------------------------------------------------------------------------

# data receiver
N_points = len(down_line_1)
currValues_axis = ((-down_line_1 / R) / k_A)
sweptValues_axis = KeysightGenerator.GenericSweptRange
N_powers = len(sweptValues_axis)
data_buff_C = np.zeros((N_points, N_powers))
data_buff_R = np.zeros((N_points, N_powers))
R_buff_C = np.zeros((N_points, N_powers))
R_buff_R = np.zeros((N_points, N_powers))
currValues = []
sweptValues = []
voltValues = []
tempsMomental = []  # for temperatures plot

# behavior on program exit - save data
f_exit = threading.Event()

# remaining / estimated time
time_mgr = TimeEstimator(len(sweptValues_axis))


def DataSave():
    if not f_save:
        return
    caption_file = f'Shapiro_{"power" if kind == MODE_POWER else "freq"}'

    caption = 'Power, dBm' if kind == MODE_POWER else 'Freq, GHz'
    SaveData({caption: sweptValues, f'I, {I_units}A': currValues,
              f'U, {I_units}V': voltValues, 'R': np.gradient(voltValues)},
             R, caption=caption_file, k_A=k_A, k_V_meas=k_V_meas, k_R=k_R)

    print('Saving PDF...')
    fname = GetSaveFileName(R, k_R, caption, 'pdf')
    pp = PdfPages(fname[:-3] + 'pdf')
    pw.SaveAllToPDF(pp)
    pp.close()
    print('Plots were successfully saved to PDF:', fname)

    SaveMatrix(sweptValues, currValues, voltValues, f'I, {I_units}A', R, k_R, caption=caption_file)

    Log.Save()

    # upload to cloud services
    UploadToClouds(GetSaveFolder(R, k_R, caption))


xcaption = 'Power, dBm' if kind == MODE_POWER else 'Frequency, GHz'
pw = plotWindow("Leonardo I-U measurement with different T")

# 0) Colormesh I-V-T plot preparation, crit. curr
tabIVPCMesh = pw.addColormesh('I-U-Power (Color mesh) (crit.)', xcaption, fr"$I, {core_units[k_A]}A$",
                                   sweptValues_axis, currValues_axis, data_buff_C, plt.get_cmap('brg'))

# 1) Colormesh I-V-T plot preparation, ret. curr
tabIVPRMesh = pw.addColormesh('I-U-Power (Color mesh) (retr.)', xcaption, fr"$I, {core_units[k_A]}A$",
                                    sweptValues_axis, currValues_axis, data_buff_R, plt.get_cmap('brg'))

# 2) I-V 2D plot preparation, crit. curr
tabIV = pw.addLine2D('I-U (simple 2D)', fr'$I, {core_units[k_A]}A$', fr"$U, {core_units[k_V_meas]}V$")

# 3) I-V-T 3D plot, crit. curr
tabIVPC3D = pw.add3DPlot('I-U-Power (3D) (crit.)', xcaption, fr'I, {core_units[k_A]}A', fr'$U, {core_units[k_V_meas]}V$')

# 4) I-V-T 3D plot, retr. curr
tabIVPR3D = pw.add3DPlot('I-U-Power (3D) (retr.)', xcaption, fr'I, {core_units[k_A]}A', fr'$U, {core_units[k_V_meas]}V$')

# 5) T - I - R 2D colormesh plot, crit. curr
tabIRPCMesh = pw.addColormesh('I-R-Power (Color mesh) (crit.)', xcaption, fr"$I, {core_units[k_A]}A$",
                                   sweptValues_axis, currValues_axis, R_buff_C, R_3D_colormap)

# 6) T - I - R 2D colormesh plot, ret. curr
tabIRPRMesh = pw.addColormesh('I-R-Power (Color mesh) (retr.)', xcaption, fr"$I, {core_units[k_A]}A$",
                                      sweptValues_axis, currValues_axis, R_buff_R, R_3D_colormap)

####################

# 7) T - I - R 3D plot, crit. curr
tabIRPC3D = pw.add3DPlot('I-R-Power (3D) (crit.)', xcaption, fr'I, {core_units[k_A]}A', fr'$R, Ohm$')

# 8) T - I - R 3D plot, retr. curr
tabIRPR3D = pw.add3DPlot('I-R-Power (3D) (retr.)', xcaption, fr'I, {core_units[k_A]}A', fr'$R, Ohm$')

# 9) T(t) plot - to control temperature in real time
tabTemp = pw.addLine2D('Temperature', 'Time', 'T, mK')
times = []
t = 0


def UpdateRealtimeThermometer():
    global times, tempsMomental, LakeShore, t, pw
    T_curr = LakeShore.GetTemperature()
    times.append(t)
    t += 1
    tempsMomental.append(T_curr)
    if t > 1000:
        tempsMomental = tempsMomental[-1000:]  # keep memory and make plot to move left
        times = times[-1000:]

    if pw.CurrentTab == tabTemp:
        line_T = pw.CoreObjects[tabTemp]
        axT = pw.Axes[tabTemp]
        line_T.set_xdata(times)
        line_T.set_ydata(tempsMomental)
        axT.set_xlim(times[0], times[-1])  # remove green/red points which are below left edge of plot
        axT.autoscale_view()
        axT.set_title(f'T={T_curr}')
        pw.canvases[tabTemp].draw()


def TemperatureThreadProc():
    while not f_exit.is_set():
        UpdateRealtimeThermometer()
        time.sleep(1.5)


# Slowly changes magnetic field from current value to zero
def ReturnAtExit():
    f_exit.set()


def EquipmentCleanup():
    Yokogawa_I.SetOutput(0)
    KeysightGenerator.OutputOff()

# main thread - runs when PyQt5 application is started
curr_curr = 0


@MeasurementProc(EquipmentCleanup)
def thread_proc():
    global Leonardo, Yokogawa_I, LakeShore, KeysightGenerator, pw, f_exit, currValues, voltValues, sweptValues, tempsMomental, curr_curr

    print('Measurement begin')

    for i, swept_now in enumerate(KeysightGenerator):
        time_mgr.OneSweepStepBegin()

        # Mark measurement begin
        UpdateRealtimeThermometer()

        pw.MarkPointOnLine(tabTemp, times[-1], tempsMomental[-1], 'go')
        this_power_V = []  # for I-V 2D plot
        this_power_A = []

        this_RIValues = [0]  # for resistance measurement
        this_RUValues = [0]

        pw.SetHeader(tabIV, 'R will be measured later...')

        def PerformStep(yok, currValues, fieldValues, voltValues,
                        volt, this_field_V, this_field_A, this_B, this_RIValues, this_RUValues):
            # measure I-U curve
            yok.SetOutput(volt)
            time.sleep(step_delay)
            curr_curr = (volt / R) / k_A
            V_meas = Leonardo.MeasureNow(6) / gain

            result = V_meas / k_V_meas
            currValues.append(curr_curr)
            fieldValues.append(this_B)
            voltValues.append(V_meas / k_V_meas)
            this_field_V.append(V_meas / k_V_meas)
            this_field_A.append(curr_curr)

            pw.MouseInit(tabIRPC3D)
            pw.MouseInit(tabIRPR3D)
            pw.MouseInit(tabIVPC3D)
            pw.MouseInit(tabIVPR3D)

            # Update I-U 2D plot
            if pw.CurrentTab == 2:
                pw.updateLine2D(ax2, line2, this_field_A, this_field_V)
            pw.canvases[2].draw()

            # measure resistance on 2D plot
            if volt > upper_R_bound:
                this_RIValues.append(curr_curr)
                this_RUValues.append(V_meas / k_V_meas)
                if pw.CurrentTab == 1:
                    UpdateResistance(ax2, np.array(this_RIValues) * k_A, np.array(this_RUValues) * k_V_meas)

            if f_exit.is_set():
                exit(0)

            return result

        # 1/3: 0 - max curr, Ic+
        for j, volt in enumerate(upper_line_1):
            res = PerformStep(Yokogawa_I, currValues, sweptValues, voltValues,
                              volt, this_power_V, this_power_A, swept_now, this_RIValues, this_RUValues)
            data_buff_C[j + N_points // 2, i] = res

        # 2/3: max curr -> min curr, Ir+, Ic-
        for j, volt in enumerate(down_line_1):
            res = PerformStep(Yokogawa_I, currValues, sweptValues, voltValues,
                              volt, this_power_V, this_power_A, swept_now, this_RIValues, this_RUValues)
            if j < (len(down_line_1) // 2):
                data_buff_R[N_points - j - 1, i] = res
            else:
                data_buff_C[N_points - j - 1, i] = res

        # 3/3: max curr -> min curr, Ir-
        for j, volt in enumerate(upper_line_2):
            res = PerformStep(Yokogawa_I, currValues, sweptValues, voltValues,
                              volt, this_power_V, this_power_A, swept_now, this_RIValues, this_RUValues)
            data_buff_R[j, i] = res

        # Update 3D plot - every magnetic field value
        pw.update3DPlot(tabIVPC3D, sweptValues_axis[:i + 1], currValues_axis, data_buff_C[:, :i + 1],
                        sweptValues_axis, plt.cm.brg)
        pw.update3DPlot(tabIVPR3D, sweptValues_axis[:i + 1], currValues_axis, data_buff_R[:, :i + 1],
                        sweptValues_axis, plt.cm.brg)

        # update pcolormesh (tab 1, 2)
        pw.updateColormesh(tabIVPCMesh, data_buff_C, sweptValues_axis, currValues_axis, 9)
        pw.updateColormesh(tabIVPRMesh, data_buff_R, sweptValues_axis, currValues_axis, 9)

        # calculate R values (as dV/dI)
        R_values_C = np.gradient(np.array(data_buff_C[:, i]) * k_V_meas)  # V in volts, to make R in ohms
        R_buff_C[:, i] = R_values_C
        #
        R_values_R = np.gradient(np.array(data_buff_R[:, i]) * k_V_meas)  # V in volts, to make R in ohms
        R_buff_R[:, i] = R_values_R

        # update R color mesh with these values
        pw.updateColormesh(tabIRPCMesh, R_buff_C, sweptValues_axis, currValues_axis, 9)
        pw.updateColormesh(tabIRPRMesh, R_buff_R, sweptValues_axis, currValues_axis, 9)

        # update R 3D plot
        pw.update3DPlot(tabIRPC3D, sweptValues_axis[:i + 1], currValues_axis, R_buff_C[:, :i + 1],
                        sweptValues_axis, R_3D_colormap)
        pw.update3DPlot(tabIRPR3D, sweptValues_axis[:i + 1], currValues_axis, R_buff_R[:, :i + 1],
                        sweptValues_axis, R_3D_colormap)

        # Mark measurement end
        pw.MarkPointOnLine(tabTemp, times[-1], tempsMomental[-1], 'go')

        time_mgr.OneSweepStepEnd(i + 1)


gui_thread = threading.Thread(target=thread_proc)
gui_thread.start()

thermometer_thread = threading.Thread(target=TemperatureThreadProc)
thermometer_thread.start()

pw.show()  # show main tabbed window

f_exit.set()
DataSave()

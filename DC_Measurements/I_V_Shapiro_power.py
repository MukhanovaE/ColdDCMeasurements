import numpy as np
from sys import exit
import time
from datetime import datetime
import os
import threading

from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import LinearSegmentedColormap

from Drivers.KeysightN51 import *

from Lib.lm_utils import *
from Lib.EquipmentBase import EquipmentBase


def DataSave():
    if not shell.f_save:
        return
    caption_file = f'Shapiro_{"power" if kind == MODE_POWER else "freq"}'

    caption = 'Power, dBm' if kind == MODE_POWER else 'Freq, GHz'
    shell.SaveData({caption: sweptValues, f'I, {shell.I_units}A': currValues,
              f'U, {shell.I_units}V': voltValues, 'R': np.gradient(voltValues)}, caption=caption_file)

    print('Saving PDF...')
    fname = shell.GetSaveFileName(caption_file, 'pdf')
    pp = PdfPages(fname[:-3] + 'pdf')
    pw.SaveAllToPDF(pp)
    pp.close()

    print('Plots were successfully saved to PDF:', fname)

    shell.SaveMatrix(sweptValues, currValues, voltValues, f'I, {shell.I_units}A', caption=caption_file)

    Log.Save()

    # upload to cloud services
    UploadToClouds(shell.GetSaveFolder(caption_file))


def UpdateRealtimeThermometer():
    global times, tempsMomental, t
    T_curr = iv_sweeper.lakeshore.GetTemperature()
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
    iv_sweeper.SetOutput(0)
    KeysightGenerator.OutputOff()


@MeasurementProc(EquipmentCleanup)
def thread_proc():
    global f_exit, currValues, voltValues, sweptValues, tempsMomental, curr_curr

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
            time.sleep(shell.step_delay)
            curr_curr = (volt / shell.R) / shell.k_A
            V_meas = iv_sweeper.MeasureNow(6) / shell.gain

            result = V_meas / shell.k_V_meas
            currValues.append(curr_curr)
            fieldValues.append(this_B)
            voltValues.append(V_meas / shell.k_V_meas)
            this_field_V.append(V_meas / shell.k_V_meas)
            this_field_A.append(curr_curr)

            pw.MouseInit(tabIRPC3D)
            pw.MouseInit(tabIRPR3D)
            pw.MouseInit(tabIVPC3D)
            pw.MouseInit(tabIVPR3D)

            # Update I-U 2D plot
            if pw.CurrentTab == 2:
                pw.updateLine2D(tabIV, this_field_A, this_field_V)
            pw.canvases[2].draw()

            # measure resistance on 2D plot
            if volt > upper_R_bound:
                this_RIValues.append(curr_curr)
                this_RUValues.append(V_meas / shell.k_V_meas)
                if pw.CurrentTab == 1:
                    UpdateResistance(pw.Axes[tabIV], np.array(this_RIValues) * shell.k_A,
                                     np.array(this_RUValues) * shell.k_V_meas)

            if f_exit.is_set():
                exit(0)

            return result

        # 1/3: 0 - max curr, Ic+
        for j, volt in enumerate(upper_line_1):
            res = PerformStep(iv_sweeper, currValues, sweptValues, voltValues,
                              volt, this_power_V, this_power_A, swept_now, this_RIValues, this_RUValues)
            data_buff_C[j + N_points // 2, i] = res

        # 2/3: max curr -> min curr, Ir+, Ic-
        for j, volt in enumerate(down_line_1):
            res = PerformStep(iv_sweeper, currValues, sweptValues, voltValues,
                              volt, this_power_V, this_power_A, swept_now, this_RIValues, this_RUValues)
            if j < (len(down_line_1) // 2):
                data_buff_R[N_points - j - 1, i] = res
            else:
                data_buff_C[N_points - j - 1, i] = res

        # 3/3: max curr -> min curr, Ir-
        for j, volt in enumerate(upper_line_2):
            res = PerformStep(iv_sweeper, currValues, sweptValues, voltValues,
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
        R_values_C = np.gradient(np.array(data_buff_C[:, i]) * shell.k_V_meas)  # V in volts, to make R in ohms
        R_buff_C[:, i] = R_values_C
        #
        R_values_R = np.gradient(np.array(data_buff_R[:, i]) * shell.k_V_meas)  # V in volts, to make R in ohms
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


shell = ScriptShell()
Log = Logger(shell, 'Shapiro')

# define a program mode (sweep power or frequency) and sweep parameters
try:
    kind, range_start, range_stop, range_step, fixed_value, generator_id =\
        [float(i) for i in shell.user_params.split(';')]
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


iv_sweeper = EquipmentBase(shell, temp_mode='passive')

# Yokogawa voltage values (will be generated by Yokogawa 1) (always V!!!)
n_points = int(2 * shell.rangeA // shell.stepA)
upper_line_1 = np.linspace(0, shell.rangeA, n_points // 2 + 1)
down_line_1 = np.linspace(shell.rangeA, -shell.rangeA, n_points)
upper_line_2 = np.linspace(-shell.rangeA, 0, n_points // 2 + 1)
voltValues0 = np.hstack((upper_line_1,
                         down_line_1,
                         upper_line_2))

# Custom plot colormaps
R_3D_colormap = LinearSegmentedColormap.from_list("R_3D", [(0, 0, 1), (1, 1, 0), (1, 0, 0)])

# Resistance measurement
percentage_R = 0.1  # how many percents left-right will be used to measure R
fraction_R = int(len(voltValues0) * ((1 / 3) * 2 * percentage_R))  # in how many points R will be measured
lower_R_bound = upper_line_2[int(len(upper_line_2) * percentage_R)]
upper_R_bound = upper_line_1[int(len(upper_line_1) * (1 - percentage_R))]

# data receiver
N_points = len(down_line_1)
currValues_axis = ((-down_line_1 / shell.R) / shell.k_A)
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
xcaption = 'Power, dBm' if kind == MODE_POWER else 'Frequency, GHz'
pw = plotWindow("Leonardo I-U measurement with different T")

# 0) Colormesh I-V-T plot preparation, crit. curr
tabIVPCMesh = pw.addColormesh('I-U-Power (Color mesh) (crit.)', xcaption, fr"$I, {core_units[shell.k_A]}A$",
                                   sweptValues_axis, currValues_axis, data_buff_C, plt.get_cmap('brg'))

# 1) Colormesh I-V-T plot preparation, ret. curr
tabIVPRMesh = pw.addColormesh('I-U-Power (Color mesh) (retr.)', xcaption, fr"$I, {core_units[shell.k_A]}A$",
                                    sweptValues_axis, currValues_axis, data_buff_R, plt.get_cmap('brg'))

# 2) I-V 2D plot preparation, crit. curr
tabIV = pw.addLine2D('I-U (simple 2D)', fr'$I, {core_units[shell.k_A]}A$', fr"$U, {core_units[shell.k_V_meas]}V$")

# 3) I-V-T 3D plot, crit. curr
tabIVPC3D = pw.add3DPlot('I-U-Power (3D) (crit.)', xcaption, fr'I, {core_units[shell.k_A]}A',
                         fr'$U,{core_units[shell.k_V_meas]}V$')

# 4) I-V-T 3D plot, retr. curr
tabIVPR3D = pw.add3DPlot('I-U-Power (3D) (retr.)', xcaption, fr'I, {core_units[shell.k_A]}A',
                         fr'$U, {core_units[shell.k_V_meas]}V$')

# 5) T - I - R 2D colormesh plot, crit. curr
tabIRPCMesh = pw.addColormesh('I-R-Power (Color mesh) (crit.)', xcaption, fr"$I, {core_units[shell.k_A]}A$",
                                   sweptValues_axis, currValues_axis, R_buff_C, R_3D_colormap)

# 6) T - I - R 2D colormesh plot, ret. curr
tabIRPRMesh = pw.addColormesh('I-R-Power (Color mesh) (retr.)', xcaption, fr"$I, {core_units[shell.k_A]}A$",
                                      sweptValues_axis, currValues_axis, R_buff_R, R_3D_colormap)

# 7) T - I - R 3D plot, crit. curr
tabIRPC3D = pw.add3DPlot('I-R-Power (3D) (crit.)', xcaption, fr'I, {core_units[shell.k_A]}A', fr'$R, Ohm$')

# 8) T - I - R 3D plot, retr. curr
tabIRPR3D = pw.add3DPlot('I-R-Power (3D) (retr.)', xcaption, fr'I, {core_units[shell.k_A]}A', fr'$R, Ohm$')

# 9) T(t) plot - to control temperature in real time
tabTemp = pw.addLine2D('Temperature', 'Time', 'T, mK')
times = []
t = 0

# main thread - runs when PyQt5 application is started
curr_curr = 0

gui_thread = threading.Thread(target=thread_proc)
gui_thread.start()

thermometer_thread = threading.Thread(target=TemperatureThreadProc)
thermometer_thread.start()

pw.show()  # show main tabbed window

f_exit.set()
DataSave()

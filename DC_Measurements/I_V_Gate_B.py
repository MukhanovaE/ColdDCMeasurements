import numpy as np

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

from Drivers.Yokogawa import *

from Lib import FieldUtils
from Lib.lm_utils import *
from Lib.EquipmentBase import EquipmentBase


# data receivers
def InitBuffers():
    global data_buff_C, data_buff_R, R_buff_C, R_buff_R, currValues, voltValues, resistancesMeas, currValues_axis,\
        voltValuesGate_axis, crit_curs, curr_voltages

    data_buff_C = np.zeros((N_points, len(voltValuesGate)))
    data_buff_R = np.zeros((N_points, len(voltValuesGate)))
    R_buff_C = np.zeros((N_points, len(voltValuesGate)))
    R_buff_R = np.zeros((N_points, len(voltValuesGate)))
    currValues = []
    voltValues = []
    curr_voltages = []
    resistancesMeas = []
    currValues_axis = ((sweep_seq.curr_axis / shell.R) / shell.k_A)
    voltValuesGate_axis = voltValuesGate
    crit_curs = np.zeros((2, len(voltValuesGate)))


def DataSave(B):
    if not shell.f_save:
        return
    caption = f'IV(Gate)_{B:.4f}_G'

    print('Saving PDF...')
    fname = shell.GetSaveFileName(caption, 'pdf')
    pp = PdfPages(fname[:-3] + 'pdf')
    pw.SaveAllToPDF(pp)
    pp.close()
    print('Plots were successfully saved to PDF:', fname)
    shell.SaveData({'V_gate, V': curr_voltages, f'I, {shell.I_units}A': currValues,
              f'U, {shell.I_units}V': voltValues, 'R': np.gradient(voltValues)}, caption=caption)
    shell.SaveData({'V_gate, V': voltValuesGate[:len(resistancesMeas)], 'Ic-': crit_curs[0, :][:len(resistancesMeas)],
              'Ic+': crit_curs[1, :][:len(resistancesMeas)]}, caption=caption + '_Ic')
    shell.SaveData({'V_gate, V': voltValuesGate[:len(resistancesMeas)], 'R, Ohm': resistancesMeas},
                   caption=caption + '_R')
    shell.SaveMatrix(curr_voltages, currValues, voltValues, f'I, {shell.I_units}A', caption=caption)

    Log.Save()

    # upload to cloud services
    shell.UploadToClouds()


def TemperatureThreadProc():
    while not f_exit.is_set():
        UpdateRealtimeThermometer()
        time.sleep(1)


def UpdateRealtimeThermometer():
    global times, tempsMomental, t, pw
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
        axT.relim()
        axT.autoscale_view()
        axT.set_xlim(times[0], times[-1])  # remove green/red points which are below left edge of plot
        axT.set_title(f'T={T_curr}')
        pw.canvases[tabTemp].draw()


def EquipmentCleanup():
    print('An error has occurred during measurement process. All equipment will be turned off.')
    #
    Yokogawa_gate.SetOutput(0)
    iv_sweeper.SetOutput(0)

    del Yokogawa_gate
    del Field_controller


# main thread - runs when PyQt5 application is started
@MeasurementProc(EquipmentCleanup)
def thread_proc():
    global  f_exit, currValues, voltValues, voltValuesGate
    global last_resistance

    def set_gate(V_gate):
        Yokogawa_gate.SetOutput(V_gate)

    # slowly change field from 0 to minimum to avoid cryostat heating
    print('Setting magnetic field to a first value...')
    FieldUtils.SlowlyChange(Field_controller, pw, np.linspace(0, rangeB, 15), 'prepairing...')
    print('Magnetic field is set, starting measurements')

    for now_field in sweeper:

        print('Field is: ', now_field, 'Gs')

        # Mark measurement begin
        UpdateRealtimeThermometer()
        pw.MarkPointOnLine(tabTemp, times[-1], tempsMomental[-1], 'go')

        # Initialize data receivers
        InitBuffers()

        # One gate voltage measurement process
        for i, curr_VG in enumerate(voltValuesGate):
            set_gate(curr_VG)

            this_field_V = []  # for I-V 2D plot
            this_field_A = []

            this_RIValues = [0]  # for resistance measurement
            this_RUValues = [0]

            pw.SetHeader(tabIV, 'R will be measured later...')

            def PerformStep(yok, currValues, voltValues,
                            volt, this_field_V, this_field_A, this_B, this_RIValues, this_RUValues):
                global last_resistance
                # measure I-U curve
                yok.SetOutput(volt)
                time.sleep(shell.step_delay)
                curr_curr = (volt / shell.R) / shell.k_A
                V_meas = iv_sweeper.MeasureNow(6) / shell.gain

                result = V_meas / shell.k_V_meas
                currValues.append(curr_curr)
                curr_voltages.append(this_B)
                voltValues.append(V_meas / shell.k_V_meas)
                this_field_V.append(V_meas / shell.k_V_meas)
                this_field_A.append(curr_curr)

                pw.MouseInit(tabIVTC3D)
                pw.MouseInit(tabIVTR3D)
                pw.MouseInit(tabIRTC3D)
                pw.MouseInit(tabIRTR3D)

                # Update I-U 2D plot
                if pw.CurrentTab == tabIV:
                    pw.updateLine2D(tabIV, this_field_A, this_field_V)

                # measure resistance on 2D plot
                if volt > upper_R_bound:
                    this_RIValues.append(curr_curr)
                    this_RUValues.append(V_meas / shell.k_V_meas)
                    last_resistance = UpdateResistance(pw.Axes[tabIV], np.array(this_RIValues) * shell.k_A,
                                                       np.array(this_RUValues) * shell.k_V_meas)

                if f_exit.is_set():
                    exit(0)

                return result

            # record one I-V curve
            # time_mgr.OneSweepStepBegin()

            for j, volt in enumerate(sweep_seq.sequence):
                res = PerformStep(iv_sweeper, currValues, voltValues,
                                  volt, this_field_V, this_field_A, curr_VG, this_RIValues, this_RUValues)
                if j < len(sweep_seq.sequence) // 4:
                    data_buff_C[j + N_points // 2 + 1] = res
                if len(sweep_seq.sequence) // 4 <= j <= 2 * len(sweep_seq.sequence) // 4:
                    data_buff_R[N_points - (j - len(sweep_seq.sequence) // 4) - 1] = res
                if 2 * len(sweep_seq.sequence) // 4 <= j <= 3 * len(sweep_seq.sequence) // 4:
                    data_buff_C[N_points // 2 - (j - 2 * len(sweep_seq.sequence) // 4)] = res
                if j >= 3 * len(sweep_seq.sequence) // 4:
                    data_buff_R[j - 3 * len(sweep_seq.sequence) // 4] = res

            # Update 3D plot - every magnetic field value
            pw.update3DPlot(tabIVTC3D, voltValuesGate_axis[:i + 1], currValues_axis, data_buff_C[:, :i + 1], voltValuesGate,
                            plt.cm.brg)
            pw.update3DPlot(tabIVTR3D, voltValuesGate_axis[:i + 1], currValues_axis, data_buff_R[:, :i + 1], voltValuesGate,
                            plt.cm.brg)

            # update pcolormesh (tab 1, 2)
            pw.updateColormesh(tabIVTCMesh, data_buff_C, voltValuesGate_axis, currValues_axis, 9)
            pw.updateColormesh(tabIVTRMesh, data_buff_R, voltValuesGate_axis, currValues_axis, 9)

            # calculate R values (as dV/dI)
            R_values_C = np.gradient(np.array(data_buff_C[:, i]) * (shell.k_V_meas / shell.k_A))  # to make R in ohms
            R_buff_C[:, i] = R_values_C
            #
            R_values_R = np.gradient(np.array(data_buff_R[:, i]) * (shell.k_V_meas / shell.k_A))  # to make R in ohms
            R_buff_R[:, i] = R_values_R

            # update R color mesh with these values
            pw.updateColormesh(tabIRTCMesh, R_buff_C, voltValuesGate_axis, currValues_axis, 9)
            pw.updateColormesh(tabIRTRMesh, R_buff_R, voltValuesGate_axis, currValues_axis, 9)

            # update R 3D plot
            pw.update3DPlot(tabIRTC3D, voltValuesGate_axis[:i + 1], currValues_axis, R_buff_C[:, :i + 1], voltValuesGate,
                            R_3D_colormap)
            pw.update3DPlot(tabIRTR3D, voltValuesGate_axis[:i + 1], currValues_axis, R_buff_R[:, :i + 1], voltValuesGate,
                            R_3D_colormap)

            # plot critical currents (left and right)
            crit_curs[:, i] = FindCriticalCurrent(currValues_axis, R_values_C)
            xdata = voltValuesGate[:i + 1]
            pw.updateLines2D(tabIcVg, [xdata, xdata], [crit_curs[0, :i + 1], crit_curs[1, :i + 1]])

            # Update resistance plot
            resistancesMeas.append(last_resistance)
            pw.updateLine2D(tabRV, xdata, resistancesMeas)

            pw.canvases[pw.CurrentTab].draw()

            # time_mgr.OneSweepStepEnd(len(resistancesMeas))

            if f_exit.is_set():
                exit(0)

        # Mark measurement end and save data
        UpdateRealtimeThermometer()
        pw.MarkPointOnLine(tabTemp, times[-1], tempsMomental[-1], 'ro')
        DataSave(now_field)

    del Yokogawa_gate


shell = ScriptShell('GateB')
Log = Logger(shell)

# Initialize devices
iv_sweeper = EquipmentBase(shell, temp_mode='passive')
Yokogawa_gate = DebugYokogawaGS200(device_num=shell.field_gate_device_id, dev_range='1E+1', what='VOLT')
Field_controller = DebugYokogawaGS200(device_num=19, dev_range='2E-1', what='CURR')

# Yokogawa voltage values (will be generated by Yokogawa 1) (always V!!!)
sweep_seq = SweepSequence(shell.rangeA, shell.stepA)

# Gate voltage values values (will be generated by Yokogawa 2) (always V!!!)
try:
    gate_amplitude, gate_points, rangeB, stepB = [float(i) for i in shell.user_params.split(';')]
except Exception:
    gate_amplitude = 10
    gate_points = 11
    rangeB = 20  # G
    stepB = 2  # G
    print('Default values were used')
voltValuesGate = np.linspace(-gate_amplitude, gate_amplitude, int(gate_points))
print('Gate voltage sweep amplitude:', gate_amplitude, 'swept points:', int(gate_points))
print('Field sweep range: +-', rangeB, 'G,', 'step is', stepB, 'G')

N_points = len(sweep_seq.down_line_1)
InitBuffers()

# Magnetic field generation
fields = np.arange(-rangeB, rangeB, stepB)

# Custom plot colormaps
R_3D_colormap = LinearSegmentedColormap.from_list("R_3D", [(0, 0, 1), (1, 1, 0), (1, 0, 0)])

# Resistance measurement
percentage_R = 0.1  # how many percents left-right will be used to measure R
fraction_R = int(len(sweep_seq.voltValues0) * ((1 / 3) * 2 * percentage_R))  # in how many points R will be measured
lower_R_bound = sweep_seq.upper_line_2[int(len(sweep_seq.upper_line_2) * percentage_R)]
upper_R_bound = sweep_seq.upper_line_1[int(len(sweep_seq.upper_line_1) * (1 - percentage_R))]

# behavior on program exit - save data
f_exit = threading.Event()

# remaining / estimatsd time
time_mgr = TimeEstimator(len(voltValuesGate))

pw = plotWindow("Leonardo I-U measurement with different gate voltage and magnetic fields")

# 0) Colormesh I-V-T plot preparation, crit. curr
tabIVTCMesh = pw.addColormesh('I-U-Vgate (Color mesh) (crit.)', fr'$V_{{gate}}, V$', fr"$I, {core_units[shell.k_A]}A$",
                                  voltValuesGate_axis, currValues_axis, data_buff_C, plt.get_cmap('brg'))

# 1) Colormesh I-V-T plot preparation, ret. curr
tabIVTRMesh = pw.addColormesh('I-U-Vgate (Color mesh) (retr.))', fr'$V_{{gate}}, V$',
                                     fr"$I, {core_units[shell.k_A]}A$",
                                     voltValuesGate_axis, currValues_axis, data_buff_R, plt.get_cmap('brg'))

# 2) I-V 2D plot preparation, crit. curr
tabIV = pw.addLine2D('I-U (simple 2D)', fr"$U, {core_units[shell.k_V_meas]}V$", fr'$I, {core_units[shell.k_A]}A$')

# 3) I-V-T 3D plot, crit. curr
tabIVTC3D = pw.add3DPlot('I-U-Vgate (3D) (crit.)', fr'$V_{{gate}}$', fr'I, {core_units[shell.k_A]}A', fr'$U,'
                                    fr'{core_units[shell.k_V_meas]}V$')

# 4) I-V-T 3D plot, retr. curr
tabIVTR3D = pw.add3DPlot('I-U-Vgate (3D) (retr.)', fr'$V_{{gate}}$', fr'I, {core_units[shell.k_A]}A', fr'$U, '
                                    fr'{core_units[shell.k_V_meas]}V$')

# 5) T - I - R 2D colormesh plot, crit. curr
tabIRTCMesh = pw.addColormesh('I-R-Vgate (crit.)', fr'$V_{{gate}}, V$', fr"$I, {core_units[shell.k_A]}A$",
                                   voltValuesGate_axis, currValues_axis, R_buff_C, R_3D_colormap)

# 6) T - I - R 2D colormesh plot, ret. curr
tabIRTRMesh = pw.addColormesh('I-R-Vgate (Color mesh) (retr.)', fr'$V_{{gate}}, V$',
                                      fr"$I, {core_units[shell.k_A]}A$",
                                      voltValuesGate_axis, currValues_axis, R_buff_R, R_3D_colormap)

# 7) T - I - R 3D plot, crit. curr
tabIRTC3D = pw.add3DPlot('I-R-Vgate (3D) (crit.)', fr'$V_{{gate}}$', fr'I, {core_units[shell.k_A]}A', fr'$R, Ohm$')

# 8) T - I - R 3D plot, retr. curr
tabIRTR3D = pw.add3DPlot('I-R-Vgate (3D) (retr.)', fr'$V_{{gate}}$', fr'I, {core_units[shell.k_A]}A', fr'$R, Ohm$')

# 9) Critical current from gate voltage
tabIcVg = pw.addLines2D('I crit. vs. Vgate', ['$I_c^+$', '$I_c^-$'], '$V_{gate}, V$', fr'$I_C^\pm, '
                                                                                      fr'{core_units[shell.k_A]}A$')

# 10) Resistance from gate voltage
tabRV = pw.addLine2D('R. vs. Vgate', '$V_{gate}, V$', fr'$R, \Omega$', linestyle='-', marker='o')

# 11) T(t) plot - to control temperature in real time
tabTemp = pw.addLine2D('Temperature', 'Time', 'T, mK')

# Update T on the last tab
t = 0
times = []
tempsMomental = []

last_resistance = 0

sweeper = FieldUtils.YokogawaFieldSweeper(fields, shell.coil_constant, Field_controller, pw)
gui_thread = threading.Thread(target=thread_proc)
gui_thread.start()

thermometer_thread = threading.Thread(target=TemperatureThreadProc)
thermometer_thread.start()

pw.show()  # show main tabbed window

FieldUtils.CheckAtExit(Field_controller, pw)

f_exit.set()

import numpy as np

from sys import exit
import time
from datetime import datetime
import os
import threading
import warnings

from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import LinearSegmentedColormap

from Drivers.Yokogawa import *
from Drivers.AMI430 import *
from Drivers.KeysightE3633A import *

from Lib import FieldUtils
from Lib.lm_utils import *
from Lib.EquipmentBase import EquipmentBase


def DataSave():
    # If "Save data and plots" checkbox is not set
    if not shell.f_save:
        return

    pw.ShowTitle('')

    print('Saving data...')
    shell.SaveData({'B, G': fieldValues, f'I, {shell.I_units}A': currValues,
              f'U, {shell.I_units}V': voltValues, 'R': np.gradient(voltValues)})

    print('Saving PDF...')
    fname = shell.GetSaveFileName(ext='pdf')
    pp = PdfPages(fname[:-3] + 'pdf')
    pw.SaveFigureToPDF(tabIVBCMesh, pp)
    pw.SaveFigureToPDF(tabIVBRMesh, pp)
    pw.SaveFigureToPDF(tabIVBC3D, pp)
    pw.SaveFigureToPDF(tabIVBR3D, pp)
    pw.SaveFigureToPDF(tabIRBCMesh, pp)
    pw.SaveFigureToPDF(tabIRBRMesh, pp)
    pw.SaveFigureToPDF(tabIRBC3D, pp)
    pw.SaveFigureToPDF(tabIRBR3D, pp)
    pp.close()
    print('Plots were successfully saved to PDF:', fname)

    shell.SaveMatrix(fieldValues, currValues, voltValues, f'I, {shell.I_units}A')
    shell.SaveData({'B, G': fieldValues_axis[:len(resistanceValues)], 'R, Ohm': resistanceValues}, shell.title + '_R')
    
    Log.Save()

    print('All data were successfully saved.')

    print('Uploading to clouds')
    UploadToClouds(shell.GetSaveFolder())


def UpdateRealtimeThermometer():
    global times, tempsMomental, t
    T_curr = iv_sweeper.lakeshore.GetTemperature()
    times.append(t)
    t += 1
    tempsMomental.append(T_curr)
    if t > 100:
        tempsMomental = tempsMomental[-100:]  # keep memory and make plot to move left
        times = times[-100:]

    if pw.CurrentTab == tabTemp:
        line_T = pw.CoreObjects[tabTemp]
        axT = pw.Axes[tabTemp]
        line_T.set_xdata(times)
        line_T.set_ydata(tempsMomental)
        axT.relim()
        axT.autoscale_view()
        axT.set_xlim(times[0], times[-1])  # remove green/red points which are below left edge of plot

        # if changes are too small, set more zoomed-out scale
        mn, mx = np.min(tempsMomental), np.max(tempsMomental)
        if abs(mx - mn) < 0.05:
            avg = (mx + mn) / 2
            delta = abs(mx - mn) * 6
            axT.set_ylim(np.clip(avg - delta / 2, a_min=0, a_max=99999999), avg + delta / 2)

        axT.set_title(f'T={T_curr:.6f} K')
        pw.canvases[tabTemp].draw()


def TemperatureThreadProc():
    while not f_exit.is_set():
        UpdateRealtimeThermometer()
        time.sleep(1)


def EquipmentCleanup():
    print('Returning magnetic field to zero...')
    sweeper.error_cleanup()
    iv_sweeper.SetOutput(0)


# @MeasurementProc(EquipmentCleanup)
def thread_proc():
    global Field_controller, pw, f_exit, currValues, voltValues, fieldValues, tempsMomental, \
        curr_curr, f_saved, R_now

    # Slowly change: 0 -> min. field
    # FieldUtils.SlowlyChange(Yokogawa_B, pw, np.linspace(0, -rangeA_B, 15), 'prepairing...')

    print('Measurement begin')

    for i, curr_B in enumerate(sweeper):

        if len(tempsMomental) != 0:
            Log.AddParametersEntry('B', curr_B, 'G', temp=tempsMomental[-1])

        # Mark measurement begin
        UpdateRealtimeThermometer()
        pw.MarkPointOnLine(tabTemp, times[-1], tempsMomental[-1], 'go', markersize=4)
        this_field_V = []  # for I-V 2D plot
        this_field_A = []

        this_RIValues = [0]  # for resistance measurement
        this_RUValues = [0]

        pw.SetHeader(tabIV, 'R will be measured later...')
        
        # offset correction
        zero_value = iv_sweeper.MeasureNow(6) / shell.gain

        def PerformStep(yok, currValues, fieldValues, voltValues,
                        volt, this_field_V, this_field_A, this_B, this_RIValues, this_RUValues):
            global R_now
            # measure I-U curve
            yok.SetOutput(volt)
            time.sleep(shell.step_delay)
            curr_curr = (volt / shell.R) / shell.k_A
            V_meas = iv_sweeper.MeasureNow(6) / shell.gain - zero_value

            result = V_meas / shell.k_V_meas
            currValues.append(curr_curr)
            fieldValues.append(this_B)
            voltValues.append(V_meas / shell.k_V_meas)
            this_field_V.append(V_meas / shell.k_V_meas)
            this_field_A.append(curr_curr)

            pw.MouseInit(tabIVBR3D)
            pw.MouseInit(tabIVBC3D)
            pw.MouseInit(tabIRBR3D)
            pw.MouseInit(tabIRBC3D)

            # Update I-U 2D plot
            if pw.CurrentTab == tabIV:
                pw.updateLine2D(tabIV, this_field_A, this_field_V)

            # measure resistance on 2D plot
            if volt > upper_R_bound:
                this_RIValues.append(curr_curr)
                this_RUValues.append(V_meas / shell.k_V_meas)

                R_now = UpdateResistance(pw.Axes[tabIV], np.array(this_RIValues) * shell.k_A,
                                         np.array(this_RUValues) * shell.k_V_meas)
            if f_exit.is_set():
                exit(0)

            return result

        # 1/3: 0 - max curr, Ic+
        for j, volt in enumerate(upper_line_1):
            res = PerformStep(iv_sweeper, currValues, fieldValues, voltValues,
                              volt, this_field_V, this_field_A, curr_B, this_RIValues, this_RUValues)
            data_buff_C[j + N_points // 2, i] = res

        # 2/3: max curr -> min curr, Ir+, Ic-
        for j, volt in enumerate(down_line_1):
            res = PerformStep(iv_sweeper, currValues, fieldValues, voltValues,
                              volt, this_field_V, this_field_A, curr_B, this_RIValues, this_RUValues)
            if j <= (len(down_line_1) // 2):
                data_buff_R[N_points - j - 1, i] = res
            if j >= (len(down_line_1) // 2):
                data_buff_C[N_points - j - 1, i] = res

        # 3/3: max curr -> min curr, Ir-
        for j, volt in enumerate(upper_line_2):
            res = PerformStep(iv_sweeper, currValues, fieldValues, voltValues,
                              volt, this_field_V, this_field_A, curr_B, this_RIValues, this_RUValues)
            data_buff_R[j, i] = res

        resistanceValues.append(R_now)

        # Update 3D plot - every magnetic field value
        pw.update3DPlot(tabIVBC3D, fieldValues_axis[:i + 1], currValues_axis, data_buff_C[:, :i + 1],
                        fieldValues_axis, plt.cm.brg)
        #
        pw.update3DPlot(tabIVBR3D, fieldValues_axis[:i + 1], currValues_axis, data_buff_R[:, :i + 1],
                        fieldValues_axis, plt.cm.brg)

        # update pcolormesh (tab 1, 2)
        pw.updateColormesh(tabIVBCMesh, data_buff_C, fieldValues_axis, currValues_axis, 9)
        pw.updateColormesh(tabIVBRMesh, data_buff_R, fieldValues_axis, currValues_axis, 9)

        # calculate R values (as dV/dI)
        R_values_C = np.gradient(np.array(data_buff_C[:, i]) * shell.k_V_meas)  # V in volts, to make R in ohms
        R_buff_C[:, i] = R_values_C
        #
        R_values_R = np.gradient(np.array(data_buff_R[:, i]) * shell.k_V_meas)  # V in volts, to make R in ohms
        R_buff_R[:, i] = R_values_R

        # update R color mesh with these values
        pw.updateColormesh(tabIRBCMesh, R_buff_C, fieldValues_axis, currValues_axis, 9)
        pw.updateColormesh(tabIRBRMesh, R_buff_R, fieldValues_axis, currValues_axis, 9)

        # update R 3D plot
        pw.update3DPlot(tabIRBC3D, fieldValues_axis[:i + 1], currValues_axis, R_buff_C[:, :i + 1],
                        fieldValues_axis, R_3D_colormap)
        pw.update3DPlot(tabIRBR3D, fieldValues_axis[:i + 1], currValues_axis, R_buff_R[:, :i + 1],
                        fieldValues_axis, R_3D_colormap)

        crit_curs[:, i] = FindCriticalCurrent(this_field_A, this_field_V, threshold=1.5)

        # update R(B) plot
        pw.updateLine2D(tabResistance, fieldValues_axis[:len(resistanceValues)], resistanceValues)

        # plot them
        xdata = fields[:i + 1]
        pw.updateLines2D(tabICT, [xdata, xdata], [crit_curs[0, :i + 1], crit_curs[1, :i + 1]])

        # Mark measurement end
        pw.MarkPointOnLine(tabTemp, times[-1], tempsMomental[-1], 'ro', markersize=4)

    print('\nMeasurement was successfully performed.')
    DataSave()
    f_saved = True


shell = ScriptShell('IV(H)')
Log = Logger(shell)

# Yokogawa voltage values (will be generated by Yokogawa 1) (always V!!!)
n_points = 2*int(shell.rangeA // shell.stepA) - 1
upper_line_1 = np.arange(0, shell.rangeA, shell.stepA)  # np.linspace(0, rangeA, n_points // 2)
down_line_1 = np.arange(shell.rangeA, -shell.rangeA, -shell.stepA)   # np.linspace(rangeA, -rangeA, n_points)
upper_line_2 = np.arange(-shell.rangeA, 0, shell.stepA)  # np.linspace(-rangeA, 0, n_points // 2)
voltValues0 = np.hstack((upper_line_1,
                         down_line_1,
                         upper_line_2))

# Solenoid current values (will be generated by Yokogawa 2) (always mA!!!)
try:
    rangeB, stepB = [float(i) for i in shell.user_params.split(';')]
except Exception:  # default value if params are not specified in command-line
    rangeB = 20
    stepB = 2
    print('Using default values: ')
print('Field sweep range: +-', rangeB, 'G', 'step is', stepB, 'G')
n_points_B = int(rangeB // stepB)
fields = np.linspace(-rangeB, rangeB, n_points_B)

# Custom plot colormaps
R_3D_colormap = LinearSegmentedColormap.from_list("R_3D", [(0, 0, 1), (1, 1, 0), (1, 0, 0)])

# Initialize devices
# ------------------------------------------------------------------------------------------------------------
if isinstance(shell.field_gate_device_id, int):
    print('Using Yokogawa for magnetic field control')
    Field_controller = KeysightE3633A(device_num=shell.field_gate_device_id) # YokogawaGS200(device_num=shell.field_gate_device_id, dev_range='2E-1', what='CURR')  # range in mA 
else:
    print('Using AMI430 for magnetic field control')
    Field_controller = AMI430(shell.field_gate_device_id, fields)

iv_sweeper = EquipmentBase(shell, temp_mode='passive')
# ------------------------------------------------------------------------------------------------------------

# Resistance measurement
# ----------------------------------------------------------------------------------------------------
percentage_R = 0.1  # how many percents left-right will be used to measure R
fraction_R = int(len(voltValues0) * ((1 / 3) * 2 * percentage_R))  # in how many points R will be measured
lower_R_bound = upper_line_2[int(len(upper_line_2) * percentage_R)]
upper_R_bound = upper_line_1[int(len(upper_line_1) * (1 - percentage_R))]
# ------------------------------------------------------------------------------------------------------------

# data receiver
N_points = len(down_line_1)
N_fields = len(fields)
data_buff_C = np.zeros((N_points, N_fields))
data_buff_R = np.zeros((N_points, N_fields))
R_buff_C = np.zeros((N_points, N_fields))
R_buff_R = np.zeros((N_points, N_fields))
crit_curs = np.zeros((2, N_fields))
currValues = []
fieldValues = []
voltValues = []
resistanceValues = []
currValues_axis = ((-down_line_1 / shell.R) / shell.k_A)
fieldValues_axis = fields  # FieldUtils.I_to_B(upper_line_1B)
tempsMomental = []  # for temperatures plot

# behavior on program exit - save data
f_exit = threading.Event()
f_saved = False

warnings.filterwarnings('ignore')  # there can be math warnings in some points
pw = plotWindow("Leonardo I-U measurement with different B")

# 0) Colormesh I-V-T plot preparation, crit. curr
tabIVBCMesh = pw.addColormesh('I-U-B (Color mesh) (crit.)', '$B, G$', fr"$I, {core_units[shell.k_A]}A$",
                              fieldValues_axis, currValues_axis, data_buff_C, plt.get_cmap('brg'))

# 1) Colormesh I-V-T plot preparation, ret. curr
tabIVBRMesh = pw.addColormesh('I-U-B (Color mesh) (retr.)', '$B, G$', fr"$I, {core_units[shell.k_A]}A$",
                              fieldValues_axis, currValues_axis, data_buff_R, plt.get_cmap('brg'))

# 2) I-V 2D plot preparation, crit. curr
tabIV = pw.addLine2D('I-U (simple 2D)', fr'$I, {core_units[shell.k_A]}A$', fr"$U, {core_units[shell.k_V_meas]}V$")

# 3) I-V-B 3D plot, crit. curr
tabIVBC3D = pw.add3DPlot('I-U-B (3D) (crit.)', 'B, G', fr'I, {core_units[shell.k_A]}A',
                         fr'$U, {core_units[shell.k_V_meas]}V$')

# 4) I-V-T 3D plot, retr. curr
tabIVBR3D = pw.add3DPlot('I-U-B (3D) (retr.)', 'B, G', fr'I, {core_units[shell.k_A]}A',
                         fr'$U, {core_units[shell.k_V_meas]}V$')

# 5) T - I - R 2D colormesh plot, crit. curr
tabIRBCMesh = pw.addColormesh('I-R-B (Color mesh) (crit.)', '$B, G$', fr"$I, {core_units[shell.k_A]}A$",
                              fieldValues_axis, currValues_axis, R_buff_C, R_3D_colormap)

# 6) T - I - R 2D colormesh plot, ret. curr
tabIRBRMesh = pw.addColormesh('I-R-B (Color mesh) (retr.)', '$B, G$', fr"$I, {core_units[shell.k_A]}A$",
                              fieldValues_axis, currValues_axis, R_buff_R, R_3D_colormap)

# 7) T - I - R 3D plot, crit. curr
tabIRBC3D = pw.add3DPlot('I-R-B (3D) (crit.)', 'B, G', fr'I, {core_units[shell.k_A]}A', fr'$R, Ohm$')

# 8) T - I - R 3D plot, retr. curr
tabIRBR3D = pw.add3DPlot('I-R-B (3D) (retr.)', 'B, G', fr'I, {core_units[shell.k_A]}A', fr'$R, Ohm$')

# 9 I_crit. vs. B
tabICT = pw.addLines2D("I crit. vs. B", ['$I_c^+$', '$I_c^-$'], 'B, G',
                       fr'$I_C^\pm, {core_units[shell.k_A]}A$', linestyle='-', marker='o')
                       
tabResistance = pw.addLine2D("Resistance", "Field, G", r"Resistance, $\Omega$", linestyle='-', marker='o')

# 10) T(t) plot - to control temperature in real time
tabTemp = pw.addLine2D('Temperature', 'Time', 'T, K')
times = []
t = 0

curr_curr = 0
R_now = 0


if isinstance(shell.field_gate_device_id, int):
    sweeper = FieldUtils.YokogawaFieldSweeper(fields, Field_controller, pw)
else:
    sweeper = FieldUtils.AmericanMagneticsFieldSweeper(fields, Field_controller, pw)
gui_thread = threading.Thread(target=thread_proc)
gui_thread.start()

thermometer_thread = threading.Thread(target=TemperatureThreadProc)
thermometer_thread.start()

pw.show()  # show main tabbed window
# If window was closed before experiment ended
if not f_saved:
    DataSave()

# if exited before current returned to zero
# FieldUtils.CheckAtExit(Yokogawa_B, pw)

f_exit.set()

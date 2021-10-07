import numpy as np
from sys import exit
import time
import threading

from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import LinearSegmentedColormap

from Drivers.Yokogawa import *

from Lib.lm_utils import *
from Lib.EquipmentBase import EquipmentBase


def DataSave():
    if not shell.f_save:
        return

    print('Saving PDF...')
    fname = shell.GetSaveFileName(ext='pdf')
    pp = PdfPages(fname[:-3] + 'pdf')
    pw.SaveAllToPDF(pp)
    pp.close()
    print('Plots were successfully saved to PDF:', fname)

    shell.SaveData({'V_gate, V': curr_voltages, f'I, {shell.I_units}A': currValues,
              f'U, {shell.I_units}V': voltValues, 'R': np.gradient(voltValues)})
    shell.SaveData({'V_gate, V': voltValuesGate[:len(resistancesMeas)], 'Ic-': crit_curs[0, :][:len(resistancesMeas)],
              'Ic+': crit_curs[1, :][:len(resistancesMeas)]}, caption=shell.title + '_Ic')
    shell.SaveData({'V_gate, V': voltValuesGate[:len(resistancesMeas)], 'R, Ohm': resistancesMeas},
                   caption=shell.title + '_R')
    shell.SaveMatrix(curr_voltages, currValues, voltValues, f'I, {shell.I_units}A')

    Log.Save()

    # upload to cloud services
    UploadToClouds(shell.GetSaveFolder())


def EquipmentCleanup():
    print('An error has occurred during measurement process.')
    Yokogawa_gate.SetOutput(0)
    iv_sweeper.SetOutput(0)


@MeasurementProc(EquipmentCleanup)
def thread_proc():
    global f_exit, currValues, voltValues, voltValuesGate, curr_curr
    global lastResistance

    def set_field(V_gate):
        Yokogawa_gate.SetOutput(V_gate)

    for i, curr_VG in enumerate(voltValuesGate):
        set_field(curr_VG)

        this_field_V = []  # for I-V 2D plot
        this_field_A = []

        this_RIValues = [0]  # for resistance measurement
        this_RUValues = [0]

        pw.SetHeader(tabIV, 'R will be measured later...')

        def PerformStep(yok, currValues, voltValues,
                        volt, this_field_V, this_field_A, this_B, this_RIValues, this_RUValues):
            global lastResistance
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

            # Make 3D plots  mouse-scrollable
            pw.MouseInit(tabIRTC3D)
            pw.MouseInit(tabIRTR3D)
            pw.MouseInit(tabIVTC3D)
            pw.MouseInit(tabIVTR3D)

            # Update I-U 2D plot
            if pw.CurrentTab == tabIV:
                pw.updateLine2D(tabIV, this_field_A, this_field_V)

            # measure resistance on 2D plot
            if volt > upper_R_bound:
                this_RIValues.append(curr_curr)
                this_RUValues.append(V_meas / shell.k_V_meas)
                lastResistance = UpdateResistance(pw.Axes[tabIV], np.array(this_RIValues) * shell.k_A,
                                                  np.array(this_RUValues) * shell.k_V_meas)

            if f_exit.is_set():
                exit(0)

            return result

        # record one I-V curve
        time_mgr.OneSweepStepBegin()

        # 1/3: 0 - max curr
        for j, volt in enumerate(upper_line_1):
            res = PerformStep(iv_sweeper, currValues, voltValues,
                              volt, this_field_V, this_field_A, curr_VG, this_RIValues, this_RUValues)
            data_buff_C[j + N_points // 2, i] = res

        # 2/3: max curr -> min curr
        for j, volt in enumerate(down_line_1):
            res = PerformStep(iv_sweeper, currValues, voltValues,
                              volt, this_field_V, this_field_A, curr_VG, this_RIValues, this_RUValues)
            if j < (len(down_line_1) // 2):
                data_buff_R[N_points - j - 1, i] = res
            else:
                data_buff_C[N_points - j - 1, i] = res

        # 3/3: max curr -> min curr
        for j, volt in enumerate(upper_line_2):
            res = PerformStep(iv_sweeper, currValues, voltValues,
                              volt, this_field_V, this_field_A, curr_VG, this_RIValues, this_RUValues)
            data_buff_R[j, i] = res

        print('R=', lastResistance)

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
        resistancesMeas.append(lastResistance)
        pw.updateLine2D(tabRV, xdata, resistancesMeas)

        pw.canvases[pw.CurrentTab].draw()

        time_mgr.OneSweepStepEnd(len(resistancesMeas))

        if f_exit.is_set():
            exit(0)

    del Yokogawa_gate


def Graph_thread():
    while not f_exit.is_set():
        for cnv in pw.canvases:
            cnv.draw()
        time.sleep(5)


shell = ScriptShell('IV(Gate)')
Log = Logger(shell)

iv_sweeper = EquipmentBase(shell)
Yokogawa_gate = YokogawaGS200(device_num=shell.field_gate_device_id, dev_range='1E+1', what='VOLT')

# Yokogawa voltage values (will be generated by Yokogawa 1) (always V!!!)
n_points = int(2 * shell.rangeA // shell.stepA)
upper_line_1 = np.linspace(0, shell.rangeA, n_points // 2 + 1)
down_line_1 = np.linspace(shell.rangeA, -shell.rangeA, n_points)
upper_line_2 = np.linspace(-shell.rangeA, 0, n_points // 2 + 1)
voltValues0 = np.hstack((upper_line_1,
                         down_line_1,
                         upper_line_2))

# Gate voltage values values (will be generated by Yokogawa 2) (always V!!!)
try:
    gate_amplitude, gate_points = [float(i) for i in shell.user_params.split(';')]
except Exception:
    gate_amplitude = 10
    gate_points = 11
voltValuesGate = np.linspace(-gate_amplitude, gate_amplitude, int(gate_points))
print('Gate voltage sweep amplitude:', gate_amplitude, 'swept points:', gate_points)

N_points = len(down_line_1)

# Custom plot colormaps
R_3D_colormap = LinearSegmentedColormap.from_list("R_3D", [(0, 0, 1), (1, 1, 0), (1, 0, 0)])

# Resistance measurement
# ----------------------------------------------------------------------------------------------------
percentage_R = 0.1  # how many percents left-right will be used to measure R
fraction_R = int(len(voltValues0) * ((1 / 3) * 2 * percentage_R))  # in how many points R will be measured
lower_R_bound = upper_line_2[int(len(upper_line_2) * percentage_R)]
upper_R_bound = upper_line_1[int(len(upper_line_1) * (1 - percentage_R))]
# ------------------------------------------------------------------------------------------------------------

# data receivers
data_buff_C = np.zeros((N_points, len(voltValuesGate)))
data_buff_R = np.zeros((N_points, len(voltValuesGate)))
R_buff_C = np.zeros((N_points, len(voltValuesGate)))
R_buff_R = np.zeros((N_points, len(voltValuesGate)))
currValues = []
voltValues = []
resistancesMeas = []
currValues_axis = ((-down_line_1 / shell.R) / shell.k_A)
voltValuesGate_axis = voltValuesGate
crit_curs = np.zeros((2, len(voltValuesGate)))

f_exit = threading.Event()

# remaining / estimated time
time_mgr = TimeEstimator(len(voltValuesGate))
pw = plotWindow("Leonardo I-U measurement with different gate voltage")

# 0) Colormesh I-V-T plot preparation, crit. curr
tabIVTCMesh = pw.addColormesh('I-U-Vgate (Color mesh) (crit.)', fr'$V_{{gate}}, V$', fr"$I, {core_units[shell.k_A]}A$",
                              voltValuesGate_axis, currValues_axis, data_buff_C, plt.get_cmap('brg'))

# 1) Colormesh I-V-T plot preparation, ret. curr
tabIVTRMesh = pw.addColormesh('I-U-Vgate (Color mesh) (retr.))', fr'$V_{{gate}}, V$',
                              fr"$I, {core_units[shell.k_A]}A$",
                              voltValuesGate_axis, currValues_axis, data_buff_R, plt.get_cmap('brg'))

# 2) I-V 2D plot preparation, crit. curr
tabIV = pw.addLine2D('I-U (simple 2D)', fr'$I, {core_units[shell.k_A]}A$', fr"$U, {core_units[shell.k_V_meas]}V$")

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
tabIcVg = pw.addLines2D('I crit. vs. Vgate', ['$I_c^+$', '$I_c^-$'], '$V_{gate}, V$', fr'$I_C^\pm,'
                                                                                      fr'{core_units[shell.k_A]}A$')

# 10) Resistance from gate voltage
tabRV = pw.addLine2D('R. vs. Vgate', '$V_{gate}, V$', fr'$R, \Omega$', linestyle='-', marker='o')

# main thread - runs when PyQt5 application is started
curr_curr = 0
lastResistance = 0
curr_voltages = []

gui_thread = threading.Thread(target=thread_proc)
gui_thread.start()

graph_thread = threading.Thread(target=Graph_thread)
graph_thread.start()

pw.show()  # show main tabbed window

f_exit.set()
DataSave()

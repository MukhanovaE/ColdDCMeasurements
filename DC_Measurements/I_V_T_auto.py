import numpy as np
from scipy.optimize import curve_fit
from sys import exit
import warnings
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import LinearSegmentedColormap

from Lib.lm_utils import *
from Lib.EquipmentBase import EquipmentBase


def DataSave():
    if not shell.f_save:
        return

    # save main data
    shell.SaveData({'T, mK': tempValues, f'I, {shell.I_units}A': currValues,
              f'U, {shell.V_units}V': voltValues, 'R': np.gradient(voltValues)})

    print('Saving PDF...')
    fname = shell.GetSaveFileName(ext='pdf')
    pp = PdfPages(fname[:-3] + 'pdf')
    # I-U-T color mesh
    pw.SaveFigureToPDF(tabIVTCMesh, pp)
    pw.SaveFigureToPDF(tabIVTRMesh, pp)
    # I-U-T 3D plot
    pw.SaveFigureToPDF(tabIVTC3D, pp)
    pw.SaveFigureToPDF(tabIVTR3D, pp)
    # R 2D plots
    pw.SaveFigureToPDF(tabRCMesh, pp)
    pw.SaveFigureToPDF(tabRRMesh, pp)
    # R 3D plots
    pw.SaveFigureToPDF(tabRC3D, pp)
    pw.SaveFigureToPDF(tabRR3D, pp)
    pp.close()
    print('Plots were successfully saved to PDF:', fname)

    # save critical temperature values
    caption_cr = shell.title + '_crit'
    shell.SaveData({'T, mK': tempValues_axis[:N_meas], f'Crit curr., negative, {shell.I_units}A': crit_curs[0, :N_meas],
              f'Crit curr., positive, {shell.I_units}A': crit_curs[1, :N_meas]}, caption=caption_cr)
    shell.SaveMatrix(tempValues, currValues, voltValues, f'I, {shell.I_units}A')
    shell.SaveData({'T': tempValuesR, f'R': resistValuesR}, caption=shell.title + '_R')

    Log.Save()
    # upload to cloud services
    shell.UploadToClouds()


def EquipmentCleanup():
    iv_sweeper.SetOutput(0)


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
        ax = pw.Axes[tabTemp]
        line_T.set_xdata(times)
        line_T.set_ydata(tempsMomental)
        ax.relim()
        ax.autoscale_view()
        ax.set_xlim(times[0], times[-1])  # remove green/red points which are below left edge of plot
        ax.set_title(f'T={T_curr}')
        pw.canvases[tabTemp].draw()


def TemperatureThreadProc():
    while not f_exit.is_set():
        UpdateRealtimeThermometer()
        time.sleep(1)


#@MeasurementProc(EquipmentCleanup)
def thread_proc():
    global f_exit, currValues, voltValues, tempValues, tempsMomental, N_meas, resist

    # Temperature change and measurement process!
    for i, temp in enumerate(iv_sweeper.lakeshore):
        temp = iv_sweeper.lakeshore.GetTemperature()
        # read 
        # write data to logs
        #Log.AddParametersEntry('T', temp, 'K', PID=iv_sweeper.lakeshore.pid,
        #                       HeaterRange=iv_sweeper.lakeshore.htrrng,
        #                       Excitation=iv_sweeper.lakeshore.excitation)
        all_Ic = []
        all_Ir = []
        all_this_temp_A = []
        all_this_temp_V = []

        for Ncurve in range(N_curves_each_time):
            this_temp_buff_ic = np.zeros(data_buff.shape[0])
            this_temp_buff_ir = np.zeros(data_buff.shape[0])

            # measure one of required curves
            print('Measuring', Ncurve+1, 'of', N_curves_each_time)
            # try to measure while temperature will be stable
            fMeasSuccess = False
            while not fMeasSuccess:
                # Mark measurement begin
                UpdateRealtimeThermometer()
                pw.MarkPointOnLine(tabTemp, times[-1], tempsMomental[-1], 'go', markersize=4)

                this_temp_V = []  # for I-V 2D plot
                this_temp_A = []

                this_T = []  # for quality control

                this_RIValues = [0]  # for resistance measurement
                this_RUValues = [0]

                pw.SetHeader(tabIV, 'R will be measured later...')

                # process one point of I-V curve
                def PerformStep(yok, currValues, tempValues, voltValues,
                                volt, this_temp_V, this_temp_A, this_T, this_RIValues, this_RUValues):
                    global resist
                    yok.SetOutput(volt)
                    time.sleep(shell.step_delay)
                    curr_curr = (volt / shell.R) / shell.k_A
                    V_meas = iv_sweeper.MeasureNow(6) / shell.gain

                    result_data = V_meas / shell.k_V_meas

                    this_temp_V.append(V_meas / shell.k_V_meas)
                    this_temp_A.append(curr_curr)

                    # keep temperatures to estimate measurements quality
                    this_T.append(tempsMomental[-1])

                    # Make 3D plots mouse-scrollable
                    pw.MouseInit(tabIVTC3D)
                    pw.MouseInit(tabIVTR3D)
                    pw.MouseInit(tabRC3D)
                    pw.MouseInit(tabRR3D)
                    # Update I-U 2D plot
                    if pw.CurrentTab == tabIV:
                        pw.updateLine2D(tabIV, this_temp_A, this_temp_V, redraw=False)
                    # measure resistance on 2D plot
                    if volt > upper_R_bound:
                        this_RIValues.append(curr_curr)
                        this_RUValues.append(V_meas / shell.k_V_meas)
                        resist = UpdateResistance(pw.Axes[tabIV], np.array(this_RIValues) * shell.k_A,
                                                  np.array(this_RUValues) * shell.k_V_meas)

                    pw.canvases[pw.CurrentTab].draw()

                    if f_exit.is_set():
                        exit(0)

                    return result_data

                # 1/3: 0 - max curr, Ic+
                for j, volt in enumerate(upper_line_1):
                    res = PerformStep(iv_sweeper, currValues, tempValues, voltValues,
                                      volt, this_temp_V, this_temp_A, this_T, this_RIValues, this_RUValues)
                    this_temp_buff_ic[j + N_points // 2] = res

                # 2/3: max curr -> min curr, Ir+, Ic-
                for j, volt in enumerate(down_line_1):
                    res = PerformStep(iv_sweeper, currValues, tempValues, voltValues,
                                      volt, this_temp_V, this_temp_A, this_T, this_RIValues, this_RUValues)
                    if j < (len(down_line_1) // 2):
                        this_temp_buff_ir[N_points - j - 1] = res
                    else:
                        this_temp_buff_ic[N_points - j - 1] = res

                # 3/3: min curr -> 0, Ir-
                for j, volt in enumerate(upper_line_2):
                    res = PerformStep(iv_sweeper, currValues, tempValues, voltValues,
                                      volt, this_temp_V, this_temp_A, this_T, this_RIValues, this_RUValues)
                    this_temp_buff_ir[j] = res

                N_meas += 1

                # check measurements accuracy
                fMeasSuccess = True
                '''
                mean_temp = np.mean(this_T)
                if abs(mean_temp - temp) > 0.005:  # toleracy is 5 mK
                    print(f'Temperature was unstable, desired - {temp}, average - {mean_temp}. Now retrying...')

                    # retry loop, do not exit while
                    fMeasSuccess = False
                else:
                    fMeasSuccess = True'''

            all_Ic.append(this_temp_buff_ic)
            all_Ir.append(this_temp_buff_ir)
            all_this_temp_A.append(this_temp_A)
            all_this_temp_V.append(this_temp_V)
            
            resistValuesR.append(resist)
            tempValuesR.append(temp)
            
            pw.updateLine2D(tabResist, tempValuesR, resistValuesR)

        # end for (3 times)
        # get averaged data and put them into buffers/arrays
        all_Ic = np.column_stack(all_Ic)
        all_Ir = np.column_stack(all_Ir)
        all_this_temp_V = np.column_stack(all_this_temp_V)
        all_this_temp_A = np.column_stack(all_this_temp_A)

        data_buff[:, i] = np.mean(all_Ic, axis=1)
        data_buff_ir[:, i] = np.mean(all_Ir, axis=1)
        this_temp_V_final = np.mean(all_this_temp_V, axis=1)
        this_temp_A_final = np.mean(all_this_temp_A, axis=1)

        tempValues.extend([temp] * len(this_temp_V_final))
        currValues.extend(this_temp_A_final)
        voltValues.extend(this_temp_V_final)

        # Update plots
        # Update I-U-T 3D
        pw.update3DPlot(tabIVTC3D, tempValues_axis[:i + 1], currValues_axis, data_buff[:, :i + 1],
                        iv_sweeper.lakeshore.TempRange, plt.cm.brg)
        pw.update3DPlot(tabIVTR3D, tempValues_axis[:i + 1], currValues_axis, data_buff_ir[:, :i + 1],
                        iv_sweeper.lakeshore.TempRange, plt.cm.brg)

        # update T-I-V color mesh (ir and ic)
        pw.updateColormesh(tabIVTCMesh, data_buff, iv_sweeper.lakeshore.TempRange, currValues_axis, 9)
        pw.updateColormesh(tabIVTRMesh, data_buff_ir, iv_sweeper.lakeshore.TempRange, currValues_axis, 9)

        # calculate R
        R_values_ic = np.gradient(np.array(data_buff[:, i]) * (shell.k_V_meas / shell.k_A))  # to make R in ohms
        R_buff[:, i] = R_values_ic
        #
        R_values_ir = np.gradient(np.array(data_buff_ir[:, i]) * (shell.k_V_meas / shell.k_A))  # to make R in ohms
        R_buff_ir[:, i] = R_values_ir

        crit_curs[:, i] = FindCriticalCurrent(this_temp_A, this_temp_V, threshold=1.5)

        # plot them
        xdata = iv_sweeper.lakeshore.TempRange[:i + 1]
        pw.updateLines2D(tabICT, [xdata, xdata], [crit_curs[0, :i + 1], crit_curs[1, :i + 1]])

        # update R color mesh (ir and ic)
        pw.updateColormesh(tabRCMesh, R_buff, iv_sweeper.lakeshore.TempRange, currValues_axis, 9)
        pw.updateColormesh(tabRRMesh, R_buff_ir, iv_sweeper.lakeshore.TempRange, currValues_axis, 9)

        # update R 3D plot (ir and ic)
        pw.update3DPlot(tabRC3D, tempValues_axis[:i + 1], currValues_axis, R_buff[:, :i + 1],
                        iv_sweeper.lakeshore.TempRange, R_3D_colormap)
        pw.update3DPlot(tabRR3D, tempValues_axis[:i + 1], currValues_axis, R_buff_ir[:, :i + 1],
                        iv_sweeper.lakeshore.TempRange, R_3D_colormap)

    # end of measurements
    f_exit.set()  # terminate all another threads


# User input
shell = ScriptShell('IV(T)')
Log = Logger(shell)
warnings.filterwarnings('ignore')

# get LakeShore temperature sweep parameters from command line
temp0, max_temp, temp_step, N_curves_each_time = [float(i) for i in shell.user_params.split(';')]
N_curves_each_time = int(N_curves_each_time)
if temp0 == 0:
    temp0 = None  # if 0 specified in a command-line, use current LakeShore temperature as starter in sweep

print(
    f'Temperature sweep range: from {"<current>" if temp0 is None else temp0 * 1e+3} mK to {max_temp} K, with step: {temp_step * 1e+3:.3f} mK, each temperature will be measured',
    N_curves_each_time, 'times')

# Initialize devices
iv_sweeper = EquipmentBase(shell, temp_mode='active', temp_start=temp0, temp_end=max_temp, temp_step=temp_step)
print('Temperatures will be:\n', iv_sweeper.lakeshore.TempRange)

# Yokogawa voltage values
n_points = int(2 * shell.rangeA // shell.stepA)
upper_line_1 = np.arange(0, shell.rangeA, shell.stepA)  # np.linspace(0, rangeA, n_points // 2)
down_line_1 = np.arange(shell.rangeA, -shell.rangeA, -shell.stepA)  # np.linspace(rangeA, -rangeA, n_points)
upper_line_2 = np.arange(-shell.rangeA, 0, shell.stepA)  # np.linspace(-rangeA, 0, n_points // 2)
voltValues0 = np.hstack((upper_line_1,
                         down_line_1,
                         upper_line_2))
print(n_points)
N_points = len(down_line_1)
N_temps = len(iv_sweeper.lakeshore.TempRange)

# Custom plot colormaps
R_3D_colormap = LinearSegmentedColormap.from_list("R_3D", [(0, 0, 1), (1, 1, 0), (1, 0, 0)])

# Resistance measurement
percentage_R = 0.2  # how many percents left-right will be used to measure R
fraction_R = int(len(voltValues0) * ((1 / 3) * 2 * percentage_R))  # in how many points R will be measured
lower_R_bound = upper_line_2[int(len(upper_line_2) * percentage_R)]
upper_R_bound = upper_line_1[int(len(upper_line_1) * (1 - percentage_R))]

# data receivers
data_buff = np.zeros((N_points, N_temps))
data_buff_ir = np.zeros((N_points, N_temps))
R_buff = np.zeros((N_points, N_temps))
R_buff_ir = np.zeros((N_points, N_temps))
currValues = []
tempValues = []
voltValues = []
crit_curs = np.zeros((2, N_temps))
currValues_axis = ((-down_line_1 / shell.R) / shell.k_A)
tempValues_axis = iv_sweeper.lakeshore.TempRange
tempsMomental = []  # for temperatures plot

tempValuesR = []
resistValuesR = []
N_meas = 0
resist = 0

# behavior on program exit - save data
f_exit = threading.Event()

# remaining / estimatsd time
time_mgr = TimeEstimator(iv_sweeper.lakeshore.NumTemps)
pw = plotWindow("Leonardo I-U measurement with different T")

# 0 Colormesh I-V-T (crit. current) plot preparation
tabIVTCMesh = pw.addColormesh('I-U-T, crit. (Color mesh)', r'Temperature, K', fr'$I, {core_units[shell.k_A]}A$',
                              tempValues_axis, currValues_axis, data_buff, plt.get_cmap('brg'))

# 1 Colormesh I-V-T (retrapping current) plot preparation

tabIVTRMesh = pw.addColormesh('I-U-T, retr. (Color mesh)', r'Temperature, K', fr'$I, {core_units[shell.k_A]}A$',
                              tempValues_axis,
                              currValues_axis, data_buff_ir, plt.get_cmap('brg'))

# 2 I-V 2D plot preparation
tabIV = pw.addLine2D('I-U (simple 2D)', fr'$I, {core_units[shell.k_A]}A$', fr"$U, {core_units[shell.k_V_meas]}V$")

# 3 I-V-T (critical current) 3D plot
tabIVTC3D = pw.add3DPlot('I-U-T, crit. (3D)', 'Temperature, K', fr'$U, {core_units[shell.k_V_meas]}V$',
                         fr'I, {core_units[shell.k_A]}A')

# 4 I-V-T (critical current) 3D plot
tabIVTR3D = pw.add3DPlot('I-U-T, retr. (3D)', 'Temperature, K', fr'$U, {core_units[shell.k_V_meas]}V$',
                         fr'I, {core_units[shell.k_A]}A')

# 5 T - I - R (critical current) 2D colormesh plot
tabRCMesh = pw.addColormesh('I-R-T, crit. (Color mesh)', 'Temperature, K', fr"$I, {core_units[shell.k_A]}A$",
                            tempValues_axis, currValues_axis, R_buff, R_3D_colormap)

# 6 T - I - R (retrapping current) 2D colormesh plot
tabRRMesh = pw.addColormesh('I-R-T, retr. (Color mesh)', 'Temperature, K', fr"$I, {core_units[shell.k_A]}A$",
                            tempValues_axis, currValues_axis, R_buff_ir, R_3D_colormap)

# 7 T - I - R (critical current) 3D plot
tabRC3D = pw.add3DPlot('I-R-T, crit. (3D)', 'Temperature, K', fr'I, {core_units[shell.k_A]}A', '$R, Ohm$')

# 8 T - I - R (retrapping current) 3D plot
tabRR3D = pw.add3DPlot('I-R-T, retr. (3D)', 'Temperature, K', fr'I, {core_units[shell.k_A]}A', '$R, Ohm$')

# 9 I_crit. vs. T
tabICT = pw.addLines2D("I crit. vs. T", ['$I_c^+$', '$I_c^-$'], 'Temperature, K',
                       fr'$I_C^\pm, {core_units[shell.k_A]}A$', linestyle='-', marker='o')

tabResist = pw.addScatter2D('Resistance', 'Temperature', r'R, $\Omega$')

# 10 T(t) plot - to control temperature in real time
tabTemp = pw.addLine2D('Temperature', 'Time', 'T, K')

# Update T on the last tab
t = 0
times = []

gui_thread = threading.Thread(target=thread_proc)
gui_thread.start()

thermometer_thread = threading.Thread(target=TemperatureThreadProc)
thermometer_thread.start()

pw.show()  # show main tabbed window

f_exit.set()
DataSave()

EquipmentCleanup()

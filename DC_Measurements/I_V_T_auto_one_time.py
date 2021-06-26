import numpy as np
from scipy.optimize import curve_fit
from sys import exit
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import LinearSegmentedColormap

from Drivers.Leonardo import *
from Drivers.Yokogawa import *
from Drivers.LakeShore import *
from Lib.lm_utils import *

# User input
# ------------------------------------------------------------------------------------------------------------
k_A, k_V_meas, k_R, R, rangeA, stepA, gain, step_delay, num_samples, I_units, V_units, f_save, yok_read, yok_write, ls, user_params = ParseCommandLine()
Log = Logger(R, k_R, 'Temp')
Log.AddGenericEntry(
    f'CurrentRange={(rangeA / R) / k_A} {core_units[k_A]} A; CurrentStep={(stepA / R) / k_A} {core_units[k_A]} A; '
    f'Gain={gain}; IVPointDelay={step_delay} sec; LeonardoPoints={num_samples}')
# ------------------------------------------------------------------------------------------------------------

# get LakeShore temperature sweep parameters from command line
try:
    temp0, max_temp, temp_step = [float(i) for i in user_params.split(';')]
    if temp0 == 0:
        temp0 = None  # if 0 specified in a command-line, use current LakeShore temperature as starter in sweep
except Exception:
    temp0, max_temp, temp_step = None, 1.1, 100 * 1E-3
print(f'Temperature sweep range: from {"<current>" if temp0 is None else temp0*1e+3} mK to {max_temp} K, with step: {temp_step*1e+3:.3f} mK')

# Initialize devices
# ------------------------------------------------------------------------------------------------------------
Leonardo = LeonardoMeasurer(n_samples=num_samples)
Yokogawa = YokogawaMeasurer(device_num=yok_read, dev_range='1E+1', what='VOLT')
LakeShore = LakeShoreController(device_num=ls, temp0=temp0, max_temp=max_temp, tempStep=temp_step)
print('Temperatures will be:\n', LakeShore.TempRange)

# Yokogawa voltage values
n_points = int(2 * rangeA // stepA)
upper_line_1 = np.arange(0, rangeA, stepA)  # np.linspace(0, rangeA, n_points // 2)
down_line_1 = np.arange(rangeA, -rangeA, -stepA)   # np.linspace(rangeA, -rangeA, n_points)
upper_line_2 = np.arange(-rangeA, 0, stepA)  # np.linspace(-rangeA, 0, n_points // 2)
voltValues0 = np.hstack((upper_line_1,
                         down_line_1,
                         upper_line_2))

N_points = len(down_line_1)
N_temps = len(LakeShore.TempRange)
# ------------------------------------------------------------------------------------------------------------


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
data_buff = np.zeros((N_points, N_temps))
data_buff_ir = np.zeros((N_points, N_temps))
R_buff = np.zeros((N_points, N_temps))
R_buff_ir = np.zeros((N_points, N_temps))
currValues = []
tempValues = []
voltValues = []
crit_curs = np.zeros((2, N_temps))
currValues_axis = ((-down_line_1 / R) / k_A)
tempValues_axis = LakeShore.TempRange
resistValues = []
tempsMomental = []  # for temperatures plot

# behavior on program exit - save data
f_exit = threading.Event()

# remaining / estimatsd time
time_mgr = TimeEstimator(LakeShore.NumTemps)


def DataSave():
    if not f_save:
        return

    # save main data
    caption = 'Temp'
    SaveData({'T, mK': tempValues, f'I, {I_units}A': currValues,
              f'U, {V_units}V': voltValues, 'R': np.gradient(voltValues)},
             R, caption=caption, k_A=k_A, k_V_meas=k_V_meas, k_R=k_R)

    print('Saving PDF...')
    fname = GetSaveFileName(R, k_R, caption, 'pdf')
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
    caption_cr = caption + '_crit'
    fname = GetSaveFileName(R, k_R, caption_cr, 'dat')
    SaveData({'T, mK': tempValues_axis[:N_meas], f'Crit curr., negative, {I_units}A': crit_curs[0, :N_meas],
              f'Crit curr., positive, {I_units}A': crit_curs[1, :N_meas]},
             R, caption=caption_cr, k_A=k_A, k_V_meas=k_V_meas, k_R=k_R)
    SaveMatrix(tempValues, currValues, voltValues, f'I, {I_units}A', R, k_R, caption=caption)
    
    SaveData({'T_mK': tempValues_axis[:len(resistValues)], 'R_Ohm': resistValues}, R, caption=caption + '_R', k_A=k_A, k_V_meas=k_V_meas, k_R=k_R)
    
    # save log
    Log.Save()

    # upload to cloud services
    UploadToClouds(GetSaveFolder(R, k_R, caption))


pw = plotWindow("Leonardo I-U measurement with different T")

# 0 Colormesh I-V-T (crit. current) plot preparation
tabIVTCMesh = pw.addColormesh('I-U-T, crit. (Color mesh)', r'$T, mK$', fr'$I, {core_units[k_A]}A$', tempValues_axis,
                              currValues_axis, data_buff, plt.get_cmap('brg'))

# 1 Colormesh I-V-T (retrapping current) plot preparation

tabIVTRMesh = pw.addColormesh('I-U-T, retr. (Color mesh)', r'$T, mK$', fr'$I, {core_units[k_A]}A$',
                              tempValues_axis,
                              currValues_axis, data_buff_ir, plt.get_cmap('brg'))

# 2 I-V 2D plot preparation
tabIV = pw.addLine2D('I-U (simple 2D)', fr'$I, {core_units[k_A]}A$', fr"$U, {core_units[k_V_meas]}V$")

# 3 I-V-T (critical current) 3D plot
tabIVTC3D = pw.add3DPlot('I-U-T, crit. (3D)', 'T, mK', fr'$U, {core_units[k_V_meas]}V$', fr'I, {core_units[k_A]}A')

# 4 I-V-T (critical current) 3D plot
tabIVTR3D = pw.add3DPlot('I-U-T, retr. (3D)', 'T, mK', fr'$U, {core_units[k_V_meas]}V$', fr'I, {core_units[k_A]}A')

# 5 T - I - R (critical current) 2D colormesh plot
tabRCMesh = pw.addColormesh('I-R-T, crit. (Color mesh)', fr'$T, mK$', fr"$I, {core_units[k_A]}A$",
                            tempValues_axis, currValues_axis, R_buff, R_3D_colormap)

# 6 T - I - R (retrapping current) 2D colormesh plot
tabRRMesh = pw.addColormesh('I-R-T, retr. (Color mesh)', fr'$T, mK$', fr"$I, {core_units[k_A]}A$",
                            tempValues_axis, currValues_axis, R_buff_ir, R_3D_colormap)

# 7 T - I - R (critical current) 3D plot
tabRC3D = pw.add3DPlot('I-R-T, crit. (3D)', 'T, mK', fr'I, {core_units[k_A]}A', '$R, Ohm$')

# 8 T - I - R (retrapping current) 3D plot
tabRR3D = pw.add3DPlot('I-R-T, retr. (3D)', 'T, mK', fr'I, {core_units[k_A]}A', '$R, Ohm$')

# 9 I_crit. vs. T
tabICT = pw.addLines2D("I crit. vs. T", ['$I_c^+$', '$I_c^-$'], 'T, mK',
                                        fr'$I_C^\pm, {core_units[k_A]}A$', linestyle='-', marker='o')
                                        
# 10 Resistance vs. T
tabResistance = pw.addLine2D('Resistance', 'T', 'R, $\Omega$', linestyle='-', marker='o')

# 11 T(t) plot - to control temperature in real time
tabTemp = pw.addLine2D('Temperature', 'Time', 'T, mK')

# Update T on the last tab
t = 0
times = []


def EquipmentCleanup():
    Yokogawa.SetOutput(0)


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


# main thread - runs when QT application is started
N_meas = 0
R_now = 0

@MeasurementProc(EquipmentCleanup)
def thread_proc():
    global Leonardo, Yokogawa, LakeShore, pw, f_exit, currValues, voltValues, tempValues, tempsMomental, N_meas, R_now

    # Temperature change and measurement process!
    for i, temp in enumerate(LakeShore):
        # calculate estimated time
        time_mgr.OneSweepStepBegin()

        # write data to logs
        Log.AddParametersEntry('T', temp, 'K', PID=LakeShore.pid, HeaterRange=LakeShore.htrrng,
                               Excitation=LakeShore.excitation)

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
                global R_now
                yok.SetOutput(volt)
                time.sleep(step_delay)
                curr_curr = (volt / R) / k_A
                V_meas = Leonardo.MeasureNow(6) / gain

                result_data = V_meas / k_V_meas
                currValues.append(curr_curr)
                tempValues.append(temp * 1000)
                voltValues.append(V_meas / k_V_meas)
                this_temp_V.append(V_meas / k_V_meas)
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
                    this_RUValues.append(V_meas / k_V_meas)

                    R_now = UpdateResistance(pw.Axes[tabIV], np.array(this_RIValues) * k_A, np.array(this_RUValues) * k_V_meas)

                pw.canvases[pw.CurrentTab].draw()

                if f_exit.is_set():
                    exit(0)

                return result_data

            # 1/3: 0 - max curr, Ic+
            for j, volt in enumerate(upper_line_1):
                res = PerformStep(Yokogawa, currValues, tempValues, voltValues,
                                  volt, this_temp_V, this_temp_A, this_T, this_RIValues, this_RUValues)
                data_buff[j + N_points // 2, i] = res

            # 2/3: max curr -> min curr, Ir+, Ic-
            for j, volt in enumerate(down_line_1):
                res = PerformStep(Yokogawa, currValues, tempValues, voltValues,
                                  volt, this_temp_V, this_temp_A, this_T, this_RIValues, this_RUValues)
                if j <= (len(down_line_1) // 2):
                    data_buff_ir[N_points - j - 1, i] = res
                if j >= (len(down_line_1) // 2):
                    data_buff[N_points - j - 1, i] = res

            # 3/3: min curr -> 0, Ir-
            for j, volt in enumerate(upper_line_2):
                res = PerformStep(Yokogawa, currValues, tempValues, voltValues,
                                  volt, this_temp_V, this_temp_A, this_T, this_RIValues, this_RUValues)
                data_buff_ir[j, i] = res

            N_meas += 1

            # Update plots
            # Update I-U-T 3D
            pw.update3DPlot(tabIVTC3D, tempValues_axis[:i + 1], currValues_axis, data_buff[:, :i + 1],
                            LakeShore.TempRange, plt.cm.brg)
            pw.update3DPlot(tabIVTR3D, tempValues_axis[:i + 1], currValues_axis, data_buff_ir[:, :i + 1],
                            LakeShore.TempRange, plt.cm.brg)

            # update T-I-V color mesh (ir and ic)
            pw.updateColormesh(tabIVTCMesh, data_buff, LakeShore.TempRange, currValues_axis, 9)
            pw.updateColormesh(tabIVTRMesh, data_buff_ir, LakeShore.TempRange, currValues_axis, 9)

            # calculate R
            R_values_ic = np.gradient(np.array(data_buff[:, i]) * (k_V_meas / k_A))  # to make R in ohms
            R_buff[:, i] = R_values_ic
            #
            R_values_ir = np.gradient(np.array(data_buff_ir[:, i]) * (k_V_meas / k_A))  # to make R in ohms
            R_buff_ir[:, i] = R_values_ir

            crit_curs[:, i] = FindCriticalCurrent(this_temp_A, this_temp_V, threshold=1.5)

            # plot them
            xdata = LakeShore.TempRange[:i + 1]
            pw.updateLines2D(tabICT, [xdata, xdata], [crit_curs[0, :i + 1], crit_curs[1, :i + 1]])

            # update R color mesh (ir and ic)
            pw.updateColormesh(tabRCMesh, R_buff, LakeShore.TempRange, currValues_axis, 9)
            pw.updateColormesh(tabRRMesh, R_buff_ir, LakeShore.TempRange, currValues_axis, 9)

            # update R 3D plot (ir and ic)
            pw.update3DPlot(tabRC3D, tempValues_axis[:i + 1], currValues_axis, R_buff[:, :i + 1],
                            LakeShore.TempRange, R_3D_colormap)
            pw.update3DPlot(tabRR3D, tempValues_axis[:i + 1], currValues_axis, R_buff_ir[:, :i + 1],
                            LakeShore.TempRange, R_3D_colormap)
            
            # Update resistance
            resistValues.append(R_now)
            pw.updateLine2D(tabResistance, tempValues_axis[:len(resistValues)], resistValues)
               
            # Mark measurement end
            pw.MarkPointOnLine(tabTemp, times[-1], tempsMomental[-1], 'ro', markersize=4)

            # check measurements accuracy
            mean_temp = np.mean(this_T)
            if abs(mean_temp - temp) > 0.005:  # toleracy is 5 mK
                print(f'Temperature was unstable, desired - {temp}, average - {mean_temp}. Now retrying...')

                # Erase now measured data
                # 2D buffers will be rewritten, there is no append(), so it is not required to erase data from them
                currValues = currValues[:-len(voltValues0)]
                voltValues = voltValues[:-len(voltValues0)]
                tempValues = tempValues[:-len(voltValues0)]
                # retry loop, do not exit while
                fMeasSuccess = False
            else:
                fMeasSuccess = True

        # calculate estimated time
        time_mgr.OneSweepStepEnd(i + 1)

    # end of measurements
    f_exit.set()  # terminate all another threads


gui_thread = threading.Thread(target=thread_proc)
gui_thread.start()

thermometer_thread = threading.Thread(target=TemperatureThreadProc)
thermometer_thread.start()

pw.show()  # show main tabbed window

f_exit.set()
DataSave()

EquipmentCleanup()

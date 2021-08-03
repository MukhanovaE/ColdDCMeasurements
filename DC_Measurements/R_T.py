import numpy as np
from scipy.optimize import curve_fit
from sys import exit
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.backends.backend_pdf import PdfPages

from Lib.lm_utils import *
from Lib.EquipmentBase import EquipmentBase

# User input
# ------------------------------------------------------------------------------------------------------------
k_A, k_V_meas, k_R, R, rangeA, stepA, gain, step_delay, num_samples, I_units, V_units, f_save, yok_read, yok_write, \
    ls, ls_model, read_device_type, exc_device_type, read_device_id, user_params = ParseCommandLine()
Log = Logger(R, k_R, 'R_T')
Log.AddGenericEntry(
    f'CurrentRange={(rangeA / R) / k_A} {core_units[k_A]}A; CurrentStep={(stepA / R) / k_A} {core_units[k_A]}A; '
    f'Gain={gain}; IVPointDelay={step_delay} sec; LeonardoPoints={num_samples}')
# ------------------------------------------------------------------------------------------------------------

# Initialize devices
# ------------------------------------------------------------------------------------------------------------
'''Leonardo = Leonardo(n_samples=num_samples) if read_device_type == READOUT_LEONARDO \
    else Keithley2182A(device_num=read_device_id)
Yokogawa = YokogawaGS200(device_num=yok_read, dev_range='1E+1', what='VOLT') if exc_device_type == EXCITATION_YOKOGAWA \
    else Keithley6200(device_num=yok_read, what='VOLT', R=R)
LakeShore = LakeShore370(device_num=ls, mode='passive', control_channel=6) if ls_model == LAKESHORE_MODEL_370 \
    else LakeShore335(device_num=ls, mode='passive', control_channel='A', heater_channel=1)'''
iv_sweeper = EquipmentBase(source_id=yok_write, source_model=exc_device_type, sense_id=yok_read,
                           sense_model=read_device_type, R=R, max_voltage=rangeA, sense_samples=num_samples,
                           temp_id=ls, temp_mode='passive')

# Yokogawa voltage values
upper_line_1 = np.arange(0, rangeA, stepA)
down_line_1 = np.arange(rangeA, -rangeA, -stepA)
upper_line_2 = np.arange(-rangeA, 0, stepA)
voltValues0 = np.hstack((upper_line_1,
                         down_line_1,
                         upper_line_2))
N_points = len(voltValues0)
percent_points = 0.05  # 5% points around zero to measure R

# temperature limit from command-line parameters (in mK)
try:
    temp_limit = float(user_params[0])
except Exception:
    temp_limit = 20
# print('Measurements will be done until temp limit:', temp_limit, 'mK')

# Main program window
pw = plotWindow("R(T)", color_buttons=False)

# I-V 2D plot preparation
tabIV = pw.addLine2D('I-U', fr'$I, {core_units[k_A]}A$', fr"$U, {core_units[k_V_meas]}V$")

# T(t) plot
tabTemp = pw.addLine2D('Temperature', 'Time', 'T, mK')

# R(T) plot
tabRT = pw.addScatter2D('R(T)', 'T, K', r'R, $\Omega$')


def EquipmentCleanup():
    pass


def DataSave():
    # if not f_save:
    #    return

    # save main data
    caption = 'R_T'
    # print(len(tempValues), len(currValues), len(voltValues))
    SaveData({'R, Ohm': R_values, 'T, K': T_values},
             R, caption=caption, k_A=k_A, k_V_meas=k_V_meas, k_R=k_R)

    # save plot to PDF
    fname = GetSaveFileName(R, k_R, caption, 'pdf')
    pp = PdfPages(fname)
    pw.SaveFigureToPDF(tabRT, pp)
    pp.close()
    print('Plots were successfully saved to PDF:', fname)
    Log.Save()

    print('Uploading to clouds')
    UploadToClouds(GetSaveFolder(R, k_R, caption))

    exit(0)


f_exit = threading.Event()
t = 0
tempsMomental = []  # for temperatures plot
times = []


def UpdateRealtimeThermometer():
    global t, tempsMomental, times
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


T_values = []
R_values = []


@MeasurementProc(EquipmentCleanup)
def MeasureProc():
    len_line = N_points / 4

    def IsNeededNowMeasureR(num):
        return (2 * len_line - percent_points * len_line < num < 2 * len_line + percent_points * len_line) \
               or (num > 0 * len_line + percent_points * len_line) or (num < N_points - percent_points * len_line)

    curr_temp = iv_sweeper.lakeshore.GetTemperature()
    while not f_exit.is_set():
        # measure I_V
        V_for_R = []
        I_for_R = []
        I_values = []
        V_values = []
        R_meas = 0

        for i, volt in enumerate(voltValues0):
            # measure I-V point
            iv_sweeper.SetOutput(volt)
            time.sleep(step_delay)
            V_meas = iv_sweeper.MeasureNow(6) / gain
            I_values.append((volt / R) / k_A)
            V_values.append(V_meas / k_V_meas)

            # measure R
            if IsNeededNowMeasureR(i):
                I_for_R.append(volt / R)
                V_for_R.append(V_meas)
                R_meas = UpdateResistance(pw.Axes[tabIV], I_for_R, V_for_R)  # is being updated at each point

            # update plot
            try:
                pw.updateLine2D(tabIV, I_values, V_values)
            except Exception:
                pass

        # Store data
        T_values.append(curr_temp)
        R_values.append(R_meas)  # Last value - there will be all points
        print('Temperature:', curr_temp, 'resistance:', R_meas)

        # Update R(T) plot
        try:
            pw.updateLine2D(tabRT, T_values, R_values)
        except Exception:
            pass

        # Sleep between (R, T) points
        s = 'Waiting time for a next curve...'
        try:
            pw.SetHeader(tabIV, s)
        except Exception:
            pass
        print(s)
        time.sleep(10)

        curr_temp = iv_sweeper.lakeshore.GetTemperature()  # for next measurement
    # end while
    f_exit.set()
    exit(0)


def TemperatureThreadProc():
    while not f_exit.is_set():
        UpdateRealtimeThermometer()
        time.sleep(1)


gui_thread = threading.Thread(target=MeasureProc)
gui_thread.start()

thermometer_thread = threading.Thread(target=TemperatureThreadProc)
thermometer_thread.start()

pw.show()  # show main tabbed window

f_exit.set()
DataSave()
EquipmentCleanup()

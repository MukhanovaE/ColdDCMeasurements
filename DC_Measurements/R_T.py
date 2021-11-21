import numpy as np
from sys import exit
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from Lib.lm_utils import *
from Lib.EquipmentBase import EquipmentBase


def EquipmentCleanup():
    pass


def DataSave():
    # if not f_save:
    #    return

    # save main data
    # print(len(tempValues), len(currValues), len(voltValues))
    shell.SaveData({'T_K': T_values, 'R_Ohm': R_values})

    # save plot to PDF
    fname = shell.GetSaveFileName(ext='pdf')
    pp = PdfPages(fname)
    pw.SaveFigureToPDF(tabRT, pp)
    pp.close()
    print('Plots were successfully saved to PDF:', fname)
    Log.Save()

    print('Uploading to clouds')
    shell.UploadToClouds()

    exit(0)


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


# @MeasurementProc(EquipmentCleanup)
def MeasureProc():
    len_line = N_points / 4

    def IsNeededNowMeasureR(num):
        return True #(2 * len_line - percent_points * len_line < num < 2 * len_line + percent_points * len_line) \
               #or (num > 0 * len_line + percent_points * len_line) or (num < N_points - percent_points * len_line)
    while len(tempsMomental) == 0:
        time.sleep(1)
    curr_temp = tempsMomental[-1]  #iv_sweeper.lakeshore.GetTemperature()
    while (not f_exit.is_set()) and (curr_temp >= temp_limit or temp_limit == -1):
        # measure I_V
        V_for_R = []
        I_for_R = []
        I_values = []
        V_values = []
        R_meas = 0

        for i, volt in enumerate(voltValues0):
            # measure I-V point
            iv_sweeper.SetOutput(volt)
            # time.sleep(shell.step_delay)
            V_meas = iv_sweeper.MeasureNow(1) / shell.gain
            I_values.append((volt / shell.R) / shell.k_A)
            V_values.append(V_meas / shell.k_V_meas)

            # measure R
            if IsNeededNowMeasureR(i):
                I_for_R.append(volt / shell.R)
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
        time.sleep(time_to_wait)

        curr_temp = tempsMomental[-1]  # iv_sweeper.lakeshore.GetTemperature()  # for next measurement
    # end while
    f_exit.set()
    exit(0)


def TemperatureThreadProc():
    while not f_exit.is_set():
        UpdateRealtimeThermometer()
        # time.sleep(1)


# User input
shell = ScriptShell('R(T)')
Log = Logger(shell)

# Initialize devices
iv_sweeper = EquipmentBase(shell, temp_mode='passive')

# Yokogawa voltage values
upper_line_1 = np.arange(0, shell.rangeA, shell.stepA)
down_line_1 = np.arange(shell.rangeA, -shell.rangeA, -shell.stepA)
upper_line_2 = np.arange(-shell.rangeA, 0, shell.stepA)
voltValues0 = np.hstack((upper_line_1,
                         down_line_1,
                         upper_line_2))
N_points = len(voltValues0)
percent_points = 0.05  # 5% points around zero to measure R

# temperature limit from command-line parameters (in mK)
# specify 0 in a command line to perform a measurement without a limit
# 0 is bad and will be replaced to -1, because in some cases LakeShore can return 0
# and this will make measurement to end.
try:
    temp_limit, time_to_wait = [float(i) for i in shell.user_params.split(';')]
except Exception:
    temp_limit = 0

if temp_limit != 0:
    print('Measurements will be done until temp limit:', temp_limit, 'mK')
else:
    print('Close main window to end this measurement, it will not be done automatically')
    temp_limit = -1
print('Interval between curves is:', time_to_wait, 'sec.')

# Main program window
pw = plotWindow("R(T)", color_buttons=False)

# I-V 2D plot preparation
tabIV = pw.addLine2D('I-U', fr'$I, {core_units[shell.k_A]}A$', fr"$U, {core_units[shell.k_V_meas]}V$")

# T(t) plot
tabTemp = pw.addLine2D('Temperature', 'Time', 'T, mK')

# R(T) plot
tabRT = pw.addScatter2D('R(T)', 'T, K', r'R, $\Omega$')

f_exit = threading.Event()
t = 0
tempsMomental = []  # for temperatures plot
times = []
T_values = []
R_values = []

gui_thread = threading.Thread(target=MeasureProc)
gui_thread.start()

thermometer_thread = threading.Thread(target=TemperatureThreadProc)
thermometer_thread.start()

pw.show()  # show main tabbed window

f_exit.set()
DataSave()
EquipmentCleanup()

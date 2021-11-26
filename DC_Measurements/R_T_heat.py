import numpy as np
from sys import exit
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from copy import copy

from Lib.lm_utils import *
from Lib.EquipmentBase import EquipmentBase


def EquipmentCleanup():
    pass


def LocalSave():
    for curr, (ri, ti) in total_result.items():
        cpt = f'R(T)_current_{curr*1e+6}_mkA'
        shell.SaveData({'T': ti, 'R': ri}, caption=cpt, preserve_unique=True)
        
    d = dict([(k, pd.Series(v)) for k,v in global_dict.items()])
    shell.SaveData(d, preserve_unique=False)


def DataSave():
    # if not f_save:
    #    return

    # save main data
    caption = 'R_T'
    # print(len(tempValues), len(currValues), len(voltValues))
    LocalSave()

    # save plot to PDF
    fname = shell.GetSaveFileName(caption, 'pdf')
    pp = PdfPages(fname)
    pw.SaveFigureToPDF(tabRT_total, pp)
    pp.close()
    print('Plots were successfully saved to PDF:', fname)
    Log.Save()

    print('Uploading to clouds')
    shell.UploadToClouds()

    exit(0)


def UpdateRealtimeThermometer():
    global t, tempsMomental, times
    T_curr = iv_sweeper.lakeshore.GetTemperature()
    if T_curr != 0:
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


#@MeasurementProc(EquipmentCleanup)
def MeasureProc():
    global global_dict
    len_line = N_points / 4
    
    
    def IsNeededNowMeasureR(num):
        return (2 * len_line - percent_points * len_line < num < 2 * len_line + percent_points * len_line) \
               or (num > 0 * len_line + percent_points * len_line) or (num < N_points - percent_points * len_line)
    
    def set_current(curr_amperes):
        iv_sweeper.SetOutput(curr_amperes * shell.R)
      
    iv_sweeper.SetOutput(0)

    for i, bias_current in enumerate(bias_currents):
        zero_volt = iv_sweeper.MeasureNow(6) / shell.gain

        print('Heating...')
        iv_sweeper.lakeshore.set_one_temperature(temp_to + 0.2, tol_temp=0.2, stabilize=False)

        curr_temp = iv_sweeper.lakeshore.GetFloat('KRDG? A')  # GetTemperature()
        prev_temp = 0
        while curr_temp < 9:
            time.sleep(1)
            curr_temp = iv_sweeper.lakeshore.GetTemperature()

        time.sleep(4)
        print('Successfully heated, now measuring...')

        T_values = []
        R_values = []

        iv_sweeper.source.SendString(f'CURRent:RANGe {bias_current}')
        iv_sweeper.source.SendString('CURRent:COMPliance 15')
        set_current(bias_current)
        iv_sweeper.source.SendString('OUTPut ON')
        print('Actual current is:', iv_sweeper.source.GetFloat('CURRent?'))
        iv_sweeper.lakeshore.set_one_temperature(temp_from, tol_temp=100000, stabilize=False)  # do not wait to be established

        while (not f_exit.is_set()) and (curr_temp >= temp_from):
            curr_temp = iv_sweeper.lakeshore.GetFloat('KRDG? B')  # GetTemperature()
            while curr_temp == 0:
                curr_temp = iv_sweeper.lakeshore.GetTemperature()
                # time.sleep(0.5)
            V_meas = iv_sweeper.MeasureNow(6) / shell.gain - zero_volt
            R_meas = abs(V_meas / bias_current)

            # Store data
            T_values.append(curr_temp)
            R_values.append(R_meas)  # Last value - there will be all points
            # print('I =', bias_current, 'U =', V_meas, 'R=', R_meas)

            # Update R(T) plot
            try:
                pw.updateLine2D(tabRT, T_values, R_values)
            except Exception:
                pass

            #time.sleep(0.5)


        # end while
        total_result[bias_current] = (R_values, T_values)
        pw.plotOnScatter2D(tabRT_total, T_values, R_values, f'I={bias_current} A', 'o', markersize=4)
        global_dict[f'T_{bias_current*1e+6}_{i}_mkA'] = copy(T_values)
        global_dict[f'R_{bias_current*1e+6}_{i}_mkA'] = copy(R_values)
        LocalSave()
    # end for (bias current)
    f_exit.set()

    # turn off heater
    iv_sweeper.lakeshore.SendString('RANGE 1, 0')
    exit(0)


def TemperatureThreadProc():
    while not f_exit.is_set():
        UpdateRealtimeThermometer()
        time.sleep(2)


# User input
shell = ScriptShell('R(T)')
Log = Logger(shell)

# Initialize devices
iv_sweeper = EquipmentBase(shell, temp_mode='active')

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

temp_from, temp_to, bias_currs = shell.user_params.split(';')
temp_from, temp_to = float(temp_from), float(temp_to)

bias_currents = np.array([float(i) for i in bias_currs.split('!')]) * 1e-6  # mkA

global_dict = {}

# Main program window
pw = plotWindow("R(T)", color_buttons=False)


# T(t) plot
tabTemp = pw.addLine2D('Temperature', 'Time', 'T, K')

# R(T) plot
tabRT = pw.addScatter2D('R(T)', 'T, K', r'R, $\Omega$')

# all R(T) plots
tabRT_total = pw.addScatter2D('R(T) (all curves)', 'T, K', r'R, $\Omega$')

f_exit = threading.Event()
t = 0
tempsMomental = []  # for temperatures plot
times = []

total_result = {}

gui_thread = threading.Thread(target=MeasureProc)
gui_thread.start()

thermometer_thread = threading.Thread(target=TemperatureThreadProc)
thermometer_thread.start()

pw.show()  # show main tabbed window

f_exit.set()
DataSave()
EquipmentCleanup()

import numpy as np
from sys import exit
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from Lib.lm_utils import *
from Lib.EquipmentBase import EquipmentBase


def EquipmentCleanup():
    pass


def LocalSave():
    for curr, (ri, ti) in total_result.items():
        cpt = f'R_T_current_{curr*1e+6}_mkA'
        shell.SaveData({'T': ti, 'R': ri}, caption = cpt)


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
    UploadToClouds(shell.GetSaveFolder(caption))

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


#@MeasurementProc(EquipmentCleanup)
def MeasureProc():
    
    len_line = N_points / 4
    
    
    def IsNeededNowMeasureR(num):
        return (2 * len_line - percent_points * len_line < num < 2 * len_line + percent_points * len_line) \
               or (num > 0 * len_line + percent_points * len_line) or (num < N_points - percent_points * len_line)
    
    def set_current(curr_amperes):
        iv_sweeper.SetOutput(curr_amperes * shell.R)
      
    iv_sweeper.SetOutput(0)     
    zero_volt = iv_sweeper.MeasureNow(6) / shell.gain
    
    
    for bias_current in [100e-6]: # [100e-6, 10e-6, 5e-6]: # #[1e-4, 1e-5, 1e-6, 1e-7, 1e-8, 1e-9, 0.5e-9]:
        print('Heating...')
        iv_sweeper.lakeshore.SendString('MOUT 1, 60')
        iv_sweeper.lakeshore.SendString('RANGE 1, 2')
        
        curr_temp = iv_sweeper.lakeshore.GetTemperature()
        while curr_temp <=11:
            time.sleep(1)
            curr_temp = iv_sweeper.lakeshore.GetTemperature()
            
        print('Successfully heated, now measuring...')
        
        T_values = []
        R_values = []
        
        iv_sweeper.source.SendString(f'CURRent:RANGe {bias_current}')
        iv_sweeper.source.SendString('CURRent:COMPliance 15')
        set_current(bias_current)
        iv_sweeper.source.SendString('OUTPut ON')
        print('Actual current is:', iv_sweeper.source.GetFloat('CURRent?'))
        iv_sweeper.lakeshore.SendString('MOUT 1, 0')
        
        while (not f_exit.is_set()) and (curr_temp >= 7.7):
            curr_temp = iv_sweeper.lakeshore.GetTemperature()
            while curr_temp == 0:
                curr_temp = iv_sweeper.lakeshore.GetTemperature()
                time.sleep(0.5)
            V_meas = iv_sweeper.MeasureNow(6) / shell.gain - zero_volt
            R_meas = V_meas / bias_current

            # Store data
            T_values.append(curr_temp)
            R_values.append(R_meas)  # Last value - there will be all points
            print('I =', bias_current, 'U =', V_meas, 'R=', R_meas)

            # Update R(T) plot
            try:
                pw.updateLine2D(tabRT, T_values, R_values)
            except Exception:
                pass

            #time.sleep(0.5)

            
        # end while
        total_result[bias_current] = (R_values, T_values)
        pw.plotOnScatter2D(tabRT_total, T_values, R_values, f'I={bias_current} A', 'o', markersize=4)
        LocalSave()
    # end for (bias current)
    f_exit.set()
    iv_sweeper.lakeshore.SendString('MOUT 1, 0')
    iv_sweeper.lakeshore.SendString('RANGE 1, 0')
    exit(0)


def TemperatureThreadProc():
    while not f_exit.is_set():
        UpdateRealtimeThermometer()
        time.sleep(1)


# User input
shell = ScriptShell()
Log = Logger(shell, 'R_T')

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

# Main program window
pw = plotWindow("R(T)", color_buttons=False)


# T(t) plot
tabTemp = pw.addLine2D('Temperature', 'Time', 'T, mK')

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

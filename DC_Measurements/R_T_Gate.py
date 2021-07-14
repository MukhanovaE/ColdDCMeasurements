import numpy as np
from scipy.optimize import curve_fit
import warnings
from sys import exit
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.backends.backend_pdf import PdfPages

from Drivers.Leonardo import *
from Drivers.Yokogawa import *
from Drivers.LakeShore import *
from Drivers.Keithley2182A import *
from Drivers.Keithley6200 import *

from Lib.lm_utils import *

# User input
# ------------------------------------------------------------------------------------------------------------
k_A, k_V_meas, k_R, R, rangeA, stepA, gain, step_delay, num_samples, I_units, V_units, f_save, yok_read, yok_write, \
    ls, read_device_type, exc_device_type, read_device_id, user_params = ParseCommandLine()
Log = Logger(R, k_R, 'R_T_Gate')
Log.AddGenericEntry(
    f'CurrentRange={(rangeA / R) / k_A} {core_units[k_A]}A; CurrentStep={(stepA / R) / k_A} {core_units[k_A]}A; '
    f'Gain={gain}; IVPointDelay={step_delay} sec; LeonardoPoints={num_samples}')
# ------------------------------------------------------------------------------------------------------------

# Initialize devices
# ------------------------------------------------------------------------------------------------------------
Leonardo = LeonardoMeasurer(n_samples=num_samples) if read_device_type == READOUT_LEONARDO \
    else Keithley2182A(device_num=read_device_id)
Yokogawa = YokogawaMeasurer(device_num=yok_read, dev_range='1E+1', what='VOLT') if exc_device_type == EXCITATION_YOKOGAWA \
    else Keithley6200(device_num=yok_read, what='VOLT', R=R)
Yokogawa_gate = DebugYokogawaMeasurer(device_num=yok_write, dev_range='1E+1', what='VOLT')

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
    temp0, max_temp, temp_step, gate_amplitude, gate_points = [float(i) for i in user_params.split(';')]
    if temp0 == 0:
        temp0 = None  # if 0 specified in a command-line, use current LakeShore temperature as starter in sweep
except Exception:
    temp0, max_temp, temp_step = None, 1.1, 100 * 1E-3

LakeShore = DebugLakeShoreController(device_num=ls, temp0=temp0, max_temp=max_temp, tempStep=temp_step)
voltValuesGate = [0, 0.25, 0.5, 0.75, 1][::-1]  # np.linspace(0, gate_amplitude, int(gate_points))

print(f'Temperature sweep range: from {"<current>" if temp0 is None else temp0} K to {max_temp} K, with step: {temp_step} K')
print('Gate voltage sweep amplitude:', gate_amplitude, 'swept points:', int(gate_points))
print('Temperatures will be:', LakeShore.TempRange)

# Main program window
pw = plotWindow("R(T)", color_buttons=False)

# I-V 2D plot preparation
tabIV = pw.addLine2D('I-U', fr'$I, {core_units[k_A]}A$', fr"$U, {core_units[k_V_meas]}V$")

# T(t) plot
tabTemp = pw.addLine2D('Temperature', 'Time', 'T, mK')

# R(T) plot
tabRT = pw.addScatter2D('R(T)', 'T, K', r'R, $\Omega$')

warnings.filterwarnings('ignore')

def EquipmentCleanup():
    pass


def DataSave(vg):
    if not f_save:
        return

    # save main data
    caption = f'R_T_Gate_{vg:.2f}_V'
    SaveData({'R, Ohm': R_values, 'T, K': T_values},
             R, caption=caption, k_A=k_A, k_V_meas=k_V_meas, k_R=k_R)

    # save plot to PDF
    fname = GetSaveFileName(R, k_R, caption, 'pdf')
    pp = PdfPages(fname)
    pw.SaveFigureToPDF(tabRT, pp)
    pp.close()
    print('Plots were successfully saved to PDF:', fname)

    Log.Save()

    # upload to cloud services
    UploadToClouds(GetSaveFolder(R, k_R, caption))


f_exit = threading.Event()
t = 0
tempsMomental = []  # for temperatures plot
times = []


def UpdateRealtimeThermometer():
    global t, tempsMomental, times
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


vg_now = None
T_values = []
R_values = []


@MeasurementProc(EquipmentCleanup)
def MeasureProc():
    global vg_now, T_values, R_values
    len_line = N_points / 4

    def IsNeededNowMeasureR(num):
        return (2 * len_line - percent_points * len_line < num < 2 * len_line + percent_points * len_line) \
               or (num > 0 * len_line + percent_points * len_line) or (num < N_points - percent_points * len_line)

    for vgate_now in voltValuesGate:
        print('Gate voltage:', vgate_now, 'V')
        Yokogawa_gate.SetOutput(vgate_now)
        vg_now = vgate_now
        T_values = []
        R_values = []
        for curr_temp in LakeShore:
            # measure I_V 3 times
            Log.AddParametersEntry('T', curr_temp, 'K', Vg=vgate_now, PID=LakeShore.pid, HeaterRange=LakeShore.htrrng,
                                   Excitation=LakeShore.excitation)
            UpdateRealtimeThermometer()
            pw.MarkPointOnLine(tabTemp, times[-1], tempsMomental[-1], 'go', markersize=4)

            for _ in range(3):
                I_values = []
                V_values = []
                for i, volt in enumerate(voltValues0):
                    if f_exit.is_set():
                        exit(0)
                    # measure I-V point
                    Yokogawa.SetOutput(volt)
                    time.sleep(step_delay)
                    V_meas = Leonardo.MeasureNow(6) / gain
                    I_values.append((volt / R) / k_A)
                    V_values.append(V_meas / k_V_meas)

                    # measure R
                    R_meas = UpdateResistance(pw.Axes[tabIV], np.array(I_values) * k_A, np.array(V_values) * k_V_meas)  # is being updated at each point

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

                pw.MarkPointOnLine(tabTemp, times[-1], tempsMomental[-1], 'ro', markersize=4)

        DataSave(vgate_now)

    # all measurements end
    f_exit.set()
    vg_now = 0  # mark that last portion of data is already saved
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
EquipmentCleanup()

if vg_now != 0:
    print('Exit before program ends')
    DataSave(vg_now)

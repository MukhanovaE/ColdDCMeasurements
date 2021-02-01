import numpy as np
import pandas as pd
import time
import threading
import sys

from Lib.lm_utils import *
from Drivers.Leonardo import *
from Drivers.Yokogawa import *
from Drivers.LakeShore import *
from Drivers.KeysightAWG import *

# User input
# ------------------------------------------------------------------------------------------------------------
k_A, k_V_meas, k_R, R, rangeA, stepA, gain, step_delay, num_samples, I_units, V_units, f_save, yok_read, yok_write, ls, user_params = ParseCommandLine()
Log = Logger(R, k_R, 'Gate_pulse')
Log.AddGenericEntry(f'Gain={gain}; LeonardoPoints={num_samples}')
# ------------------------------------------------------------------------------------------------------------

# Initialize devices
# ------------------------------------------------------------------------------------------------------------
Leonardo = LeonardoMeasurer(n_samples=num_samples)
Yokogawa = YokogawaMeasurer(device_num=yok_read, dev_range='1E+1', what='VOLT')
LakeShore = LakeShoreController(mode='passive', device_num=ls)
# parse user-defined parameters
try:
    length0, length_end, length_step, n_repeat, amplitude, current, device_id = [float(i) for i in user_params.split(';')]
    n_repeat = int(n_repeat)
    device_id = int(device_id)
    current *= 1e-9  # nA to A
except Exception:  # default values
    length0 = 5
    length_end = 0.1
    length_step = 0.1
    n_repeat = 10
    amplitude = 0.6
    current = 300e-9
    device_id = 228  # TODO: set a default device number
# show entered parameters
print('Pulse length from:', length0, 'to:', length_end, 'with step:', length_step)
print('Ome length will be repeated:', n_repeat, 'times, pulse amplitude:', amplitude, 'V')
print('Bias current:', current*1e+9, 'nA')
print('Keysight AWG device ID:', device_id)
# generate required sequences and values
swept_lengths = [5, 0.5, 0.05, 0.005]#np.arange(length0, length_end, length_step)  # TODO: return!
volt_yok = current * R  # voltage to set on Yokogawa (one point on I-V curve) U=IR
# set up the AWG device
AWG = KeysightAWG(device_num=device_id, voltageAmplitude=amplitude)

pw = plotWindow("Gate pulses", color_buttons=False)
tabMainVT = pw.addLine2D("V(t)", "Time, sec", "Voltage (V)")
tabTemp = pw.addLine2D('Temperature', 'Time', 'T, mK')

# measured data
times = []
voltages = []
pulseStartTimes = []
pulseEndTimes = []
triggerState = False
nStarts = 0

# Update T on the last tab
t = 0
timesT = []
tempsMomental = []

# flag to perform exit from all threads after program ends
f_exit = threading.Event()
start_time = time.time()
def measureTimeNow():
    return time.time() - start_time


def TemperatureThreadProc():
    while not f_exit.is_set():
        UpdateRealtimeThermometer()
        time.sleep(1)


def UpdateRealtimeThermometer():
    global timesT, tempsMomental, LakeShore, t, pw
    T_curr = LakeShore.GetTemperature()
    timesT.append(t)
    t += 1
    tempsMomental.append(T_curr)
    if t > 1000:
        tempsMomental = tempsMomental[-1000:]  # keep memory and make plot to move left
        timesT = timesT[-1000:]

    if pw.CurrentTab == tabTemp:
        line_T = pw.CoreObjects[tabTemp]
        axT = pw.Axes[tabTemp]
        line_T.set_xdata(timesT)
        line_T.set_ydata(tempsMomental)
        axT.relim()
        axT.autoscale_view()
        axT.set_xlim(timesT[0], timesT[-1])  # remove green/red points which are below left edge of plot
        axT.set_title(f'T={T_curr}')
        pw.canvases[tabTemp].draw()


# Save measurements data
def DataSave(length):
    freq = 1 / (2*length)
    caption = f"Gate_pulse_{freq}Hz"

    # save V(t) curve
    SaveData({'time': times, 'voltage': voltages}, R, caption, k_A, k_V_meas, k_R)

    # save pulse start and end times
    # if number of end times is less than the number of start times, it means that the last point was not registered
    # (for example, a program was closed before pulse end)
    # so, write a zero there
    #if len(pulseStartTimes) - len(pulseEndTimes) > 0:
    #    pulseEndTimes.extend([0] * (len(pulseStartTimes) - len(pulseEndTimes)))

    # save start/end points
    #SaveData({'StartTimes': pulseStartTimes, 'EndTimes': pulseEndTimes}, R, caption + '_points', k_A, k_V_meas, k_R)
    fig = pw.Figures[tabMainVT]
    x, y = fig.get_size_inches()
    x = 65535 / 100  # figure maximum size
    fig.set_size_inches(x, y)
    pw.SaveFigureToOneFile(tabMainVT, GetSaveFileName(R, k_R, caption, "pdf"))
    Log.Save()


# turns off all equipment if an error occurs
def EquipmentCleanup():
    Yokogawa.SetOutput(0)
    # del AWG
    f_exit.set()


def GraphingThread():
    while not f_exit.is_set():
        pw.updateLine2D(tabMainVT, times, voltages, True)
        time.sleep(0.5)


# Measure one voltage point
def MeasureOneVoltage():
    t = measureTimeNow()
    v = Leonardo.MeasureNow(6) / gain

    times.append(t)
    voltages.append(v)


# read trigger signal and mark begin/end of each waveform
def HandleTrigger():
    global triggerState, nStarts
    threshold = 2  # volts

    trig = Leonardo.MeasureNow(4) 
    trig_now = (trig > threshold)

    if trig_now and not triggerState:  # if trigger turned on - begin of a cycle
        pw.MarkPointOnLine(tabMainVT, times[-1], voltages[-1], 'yo', markersize=6)
        pulseStartTimes.append(times[-1])
        nStarts+=1
        triggerState = True

    if not trig_now and triggerState:  # trigger turned off - end of a cycle
        pw.MarkPointOnLine(tabMainVT, times[-1], voltages[-1], 'bo', markersize=6)
        pulseEndTimes.append(times[-1])
        triggerState = False


# A thread for voltage measurement
def VoltageMeasurementProc():
    while not f_exit.is_set():
        MeasureOneVoltage()
        # HandleTrigger()


@MeasurementProc(EquipmentCleanup)
def MeasurementProc():
    global nStarts, times, voltages
    for length in swept_lengths:
        print('Now measuring sweep length:', length)
        times = []
        voltages = []

        MeasureOneVoltage()
        pw.MarkPointOnLine(tabMainVT, times[-1], voltages[-1], 'go', markersize=8)
        if len(tempsMomental) == 0:
            UpdateRealtimeThermometer()
        pw.MarkPointOnLine(tabTemp, times[-1], tempsMomental[-1], 'go')

        AWG.GenerateAndSetOutput(length, length, n_repeat)
        print('Duration:', 2*length*n_repeat + length, 'sec')

        time.sleep(2*length*n_repeat + length)  # high and low voltage, repeat

        pw.MarkPointOnLine(tabMainVT, times[-1], voltages[-1], 'ro', markersize=8)
        pw.MarkPointOnLine(tabTemp, times[-1], tempsMomental[-1], 'ro')

        DataSave(length)

        if f_exit.is_set():
            sys.exit(0)

    print('Measurement end')
    f_exit.set()


# start measurement threads
measurement_thread = threading.Thread(target=VoltageMeasurementProc)
measurement_thread.start()

main_thread = threading.Thread(target=MeasurementProc)
main_thread.start()

thermometer_thread = threading.Thread(target=TemperatureThreadProc)
thermometer_thread.start()

graphing_thread = threading.Thread(target=GraphingThread)
graphing_thread.start()

# show program main window and wait till it be closed, then exit all threads and save data
pw.show()
f_exit.set()


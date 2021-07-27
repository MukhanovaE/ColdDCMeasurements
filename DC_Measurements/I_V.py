import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from tkinter import TclError
import threading

from Drivers.Leonardo import *
from Drivers.Yokogawa import *
from Drivers.Keithley2182A import *
from Drivers.Keithley6200 import *
from Lib.lm_utils import *

# User input
# ------------------------------------------------------------------------------------------------------------
k_A, k_V_meas, k_R, R, rangeA, stepA, gain, step_delay, num_samples, I_units, V_units, f_save, yok_read, yok_write, \
    ls, ls_model, read_device_type, exc_device_type, read_device_id, user_params = ParseCommandLine()
Log = Logger(R, k_R, 'simple_I_V')
Log.AddGenericEntry(
    f'CurrentRange={(rangeA / R) / k_A} {core_units[k_A]}A; CurrentStep={(stepA / R) / k_A} {core_units[k_A]}A; '
    f'Gain={gain}; IVPointDelay={step_delay} sec; LeonardoPoints={num_samples}')
# ------------------------------------------------------------------------------------------------------------
# gain = 100
# step_delay = 0.02
# num_samples = 500
Leonardo = LeonardoMeasurer(n_samples=num_samples) if read_device_type == READOUT_LEONARDO \
    else Keithley2182A(device_num=read_device_id)
Yokogawa = YokogawaMeasurer(device_num=yok_read, dev_range='1E+1', what='VOLT') if exc_device_type == EXCITATION_YOKOGAWA \
    else Keithley6200(device_num=yok_read, what='VOLT', R=R, max_current=(rangeA / R))

# all Yokogawa generated values (always in volts!!!)
upper_line_1 = np.arange(0, rangeA, stepA)
down_line_1 = np.arange(rangeA, -rangeA, -stepA)
upper_line_2 = np.arange(-rangeA, 0, stepA)

# always in volts!
voltValues0 = np.hstack((upper_line_1,
                         down_line_1,
                         upper_line_2))
voltValues = []
currValues = []


pw = plotWindow("I-V")
tabIV = pw.addLine2D('I-V', f'I, {I_units}A', f'U, {V_units}V')
tabR = pw.addLine2D(r'dV/dI', f'I, {I_units}A', r'$\frac{dV}{dI}$, $\Omega$')
f_exit = threading.Event()


# Write results to a file
def DataSave():
    if not f_save:
        return
    caption = "simple_I_V"
    SaveData(data_dict={f'I, {I_units}A': currValues, f'U, {V_units}V': voltValues},
             R=R, caption=caption, k_A=k_A, k_V_meas=k_V_meas, k_R=k_R)

    fname = GetSaveFileName(R, k_R, caption, 'pdf')
    pp = PdfPages(fname[:-3] + 'pdf')
    pw.SaveFigureToPDF(tabIV, pp)
    pw.SaveFigureToPDF(tabR, pp)
    pp.close()

    Log.Save()

    print('Plots were successfully saved to PDF:', fname)

    print('Uploading to clouds')
    UploadToClouds(GetSaveFolder(R, k_R, caption))


def Cleanup():
    Yokogawa.SetOutput(0)


@MeasurementProc(Cleanup)
def MeasurementThreadProc():
    print('Measurement started.\nTotal points:', len(currValues))
    print('When all points wil be measured, data will be saved automatically.')
    print('Close a plot window to stop measurement and save only currently obtained data.')
    fMeasDeriv = False

    # Set zero current and calculate offset (if it is present)
    Yokogawa.SetOutput(0)
    zero_value = Leonardo.MeasureNow(6) / gain

    for i, volt in enumerate(voltValues0):
        Yokogawa.SetOutput(volt)
        time.sleep(step_delay)

        V_meas = Leonardo.MeasureNow(6) / gain - zero_value
        voltValues.append(V_meas / k_V_meas)
        currValues.append((volt / R) / k_A)

        if fMeasDeriv:
            R_values = np.abs(np.gradient(voltValues) * k_V_meas * 1e+7)  # in Ohms

        # resistance measurement
        if volt < lower_R_bound or volt > upper_R_bound:
            R_IValues.append(volt / R)  # Amperes forever!
            R_UValues.append(V_meas)  # volts

            UpdateResistance(pw.Axes[tabIV], np.array(R_IValues), np.array(R_UValues))

        pw.updateLine2D(tabIV, currValues, voltValues)
        if fMeasDeriv:
            pw.updateLine2D(tabR, currValues, R_values)

        fMeasDeriv = True
        if f_exit.is_set():
            break
    print('Measurement finished, turning off')
    Cleanup()


# Resistance measurement
# ----------------------------------------------------------------------------------------------------
percentage_R = 0.1  # how many percents left-right will be used to measure R
fraction_R = int(len(voltValues0) * ((1 / 3) * 2 * percentage_R))  # in how many points R will be measured
R_IValues = [0]
R_UValues = [0]

lower_R_bound = upper_line_2[int(len(upper_line_2) * percentage_R)]
upper_R_bound = upper_line_1[int(len(upper_line_1) * (1 - percentage_R))]
N_half = len(upper_line_1) + 1
# ----------------------------------------------------------------------------------------------------


meas_thread = threading.Thread(target=MeasurementThreadProc)
meas_thread.start()

pw.show()
Cleanup()
f_exit.set()

DataSave()


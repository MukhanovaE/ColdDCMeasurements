import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
import threading

from Lib.EquipmentBase import EquipmentBase
from Lib.lm_utils import *


# Write results to a file
def DataSave():
    if not shell.f_save:
        return
    shell.SaveData({f'I, {shell.I_units}A': currValues, f'U, {shell.V_units}V': voltValues, 'R, Ohm': R_values})

    fname = shell.GetSaveFileName(ext='pdf')
    pp = PdfPages(fname[:-3] + 'pdf')
    pw.SaveFigureToPDF(tabIV, pp)
    pw.SaveFigureToPDF(tabR, pp)
    pp.close()
    print('Plots were successfully saved to PDF:', fname)

    Log.Save()

    print('Uploading to clouds')
    UploadToClouds(shell.GetSaveFolder())


def Cleanup():
    iv_sweeper.SetOutput(0)


@MeasurementProc(Cleanup)
def MeasurementThreadProc():
    global R_values
    print('Measurement started.\nTotal points:', len(currValues))
    print('When all points wil be measured, data will be saved automatically.')
    print('Close a plot window to stop measurement and save only currently obtained data.')
    fMeasDeriv = False

    # Set zero current and calculate offset (if it is present)
    iv_sweeper.SetOutput(0)
    zero_value = iv_sweeper.MeasureNow(6) / shell.gain

    for i, volt in enumerate(voltValues0):
        iv_sweeper.SetOutput(volt)
        time.sleep(shell.step_delay)

        V_meas = iv_sweeper.MeasureNow(6) / shell.gain - zero_value
        voltValues.append(V_meas / shell.k_V_meas)
        currValues.append((volt / shell.R) / shell.k_A)

        if fMeasDeriv:
            R_values = np.abs(np.gradient(voltValues) * shell.k_V_meas * 1e+7)  # in Ohms

        # resistance measurement
        if volt < lower_R_bound or volt > upper_R_bound:
            R_IValues.append(volt / shell.R)  # Amperes forever!
            R_UValues.append(V_meas)  # volts

            UpdateResistance(pw.Axes[tabIV], np.array(R_IValues), np.array(R_UValues))

        pw.updateLine2D(tabIV, currValues, voltValues)
        if fMeasDeriv:
            pw.updateLine2D(tabR, currValues[1:-1], R_values[1:-1])

        fMeasDeriv = True
        if f_exit.is_set():
            break
    print('Measurement finished, turning off')
    Cleanup()


shell = ScriptShell(title='IV')
Log = Logger(shell)
iv_sweeper = EquipmentBase(shell)

# all Yokogawa generated values (always in volts!!!)
upper_line_1 = np.arange(0,  shell.rangeA,  shell.stepA)
down_line_1 = np.arange( shell.rangeA, - shell.rangeA, - shell.stepA)
upper_line_2 = np.arange(- shell.rangeA, 0,  shell.stepA)

# always in volts!
voltValues0 = np.hstack((upper_line_1,
                         down_line_1,
                         upper_line_2))
voltValues = []
currValues = []
R_values = []

pw = plotWindow("I-V")
tabIV = pw.addLine2D('I-V', f'I, {shell.I_units}A', f'U, {shell.V_units}V')
tabR = pw.addLine2D(r'dV/dI', f'I, {shell.I_units}A', r'$\frac{dV}{dI}$, $\Omega$')
f_exit = threading.Event()

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

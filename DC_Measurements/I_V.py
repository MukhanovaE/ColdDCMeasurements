import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from tkinter import TclError

from Drivers.Leonardo import *
from Drivers.Yokogawa import *
from Drivers.Keithley2182A import *
from Drivers.Keithley6200 import *
from Lib.lm_utils import *

# User input
# ------------------------------------------------------------------------------------------------------------
k_A, k_V_meas, k_R, R, rangeA, stepA, gain, step_delay, num_samples, I_units, V_units, f_save, yok_read, yok_write, \
    ls, read_device_type, exc_device_type, read_device_id, user_params = ParseCommandLine()
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
    else Keithley6200(device_num=yok_read, what='VOLT', R=R)

f_exit = False

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


# rocedure after window closed - write results to a file
def OnClose(_):
    global f_exit, f_save, fig
    caption = "simple_I_V"
    SaveData(data_dict={f'I, {I_units}A': currValues, f'U, {I_units}V': voltValues},
             R=R, caption=caption, k_A=k_A, k_V_meas=k_V_meas, k_R=k_R)

    fname = GetSaveFileName(R, k_R, caption, 'pdf')
    pp = PdfPages(fname[:-3] + 'pdf')
    pp.savefig(fig)
    Log.Save()
    pp.close()
    print('Plots were successfully saved to PDF:', fname)

    print('Uploading to clouds')
    UploadToClouds(GetSaveFolder(R, k_R, caption))
    f_exit = f_save = True


# Initialize a plot
plt.ion()
fig, ax1 = plt.subplots(figsize=(14, 8))
fig.canvas.mpl_connect('close_event', OnClose)
line, = ax1.plot([], [])
ax1.set_xlabel(fr'$I, {core_units[k_A]}A$', fontsize=15)
ax1.set_ylabel(fr"$U, {core_units[k_V_meas]}V$", fontsize=15)
ax1.grid()
fig.show()

print('Measurement started.\nTotal points:', len(currValues))
print('When all points wil be measured, data will be saved automatically.')
print('Close a plot window to stop measurement and save only currently obtained data.')

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

# Perform measurements!
try:
    for i, volt in enumerate(voltValues0):
        Yokogawa.SetOutput(volt)
        time.sleep(step_delay)
        # delay at curve ends to prevent hysteresis
        '''if (i == N_half or i == 3*N_half) and step_delay < 0.01:
             print('!!')
             time.sleep(1) '''

        V_meas = Leonardo.MeasureNow(6) / gain
        voltValues.append(V_meas / k_V_meas)  # volts / coeff
        currValues.append((volt / R) / k_A)  # (volts/Ohms always) / coeff

        # resistance measurement
        if volt < lower_R_bound or volt > upper_R_bound:
            R_IValues.append(volt / R)  # Amperes forever!
            R_UValues.append(V_meas)  # volts
            UpdateResistance(ax1, np.array(R_IValues), np.array(R_UValues))

        line.set_xdata(currValues)
        line.set_ydata(voltValues)
        ax1.relim()
        ax1.autoscale_view()
        try:
            plt.pause(step_delay)
        except TclError:  # don't throw exception after plot closure
            pass
        if f_exit:
            break

except Exception as e:
    print('An error has occurred during measurement process.')
    print(e)
    print('Turning current off...')
    Yokogawa.SetOutput(0)

if not f_save:  # if window was not closed
    OnClose(None)

plt.ioff()
plt.show()
Yokogawa.SetOutput(0)
del Yokogawa

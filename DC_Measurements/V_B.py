import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

import threading
from copy import copy
from sys import exit

from Drivers.Yokogawa import *
from Drivers.AMI430 import *

from Lib import FieldUtils
from Lib.lm_utils import *
from Lib.EquipmentBase import EquipmentBase


# Field sweep modes
SWEEP_MODE_INCR = 0
SWEEP_MODE_DECR = 1
SWEEP_MODE_INCR_DECR = 2
SWEEP_MODE_DECR_INCR = 3
SWEEP_MODE_INCR_DECR_ONE_CURVE = 4
SWEEP_MODE_DECR_INCR_ONE_CURVE = 5


# Write temperature obtained from BlueFors log jnto a plot
# If it is not known now (no newest logs), write about it
def FormatTemperature(temp):
    return T if temp != 0 else '<...loading...>'


# Save data after program exit
def DataSave():
    caption = "V_B"

    print('Saving PDF...')
    fname = shell.GetSaveFileName(caption, 'pdf')
    pp = PdfPages(fname)
    pw.SaveAllToPDF(pp)
    pp.close()
    print('Plot was successfully saved to PDF:', fname)
    
    # To save data if a program was closed
    LocalSave()

    Log.Save()

    # upload to cloud services
    UploadToClouds(shell.GetSaveFolder(caption))


def LocalSaveIncr():
    caption = "V_B"
    print('Saving forward curve...')
    # Append a measured curve to a file
    shell.SaveData(data_dict_inc, caption=caption + "_forward",  preserve_unique=False)


def LocalSaveDecr():
    caption = "V_B"
    print('Saving reverse curve...')
    shell.SaveData(data_dict_dec, caption=caption + "_reverse", preserve_unique=False)


def LocalSave():
    if len(data_dict_inc) > 1:
        LocalSaveIncr()
    if len(data_dict_dec) > 1:
        LocalSaveDecr()


def EquipmentCleanup():
    sweeper_incr.error_cleanup()
    iv_sweeper.SetOutput(0)


@MeasurementProc(EquipmentCleanup)
def MainThreadProc():
    global curr_curr

    # offset algorithm initialization
    min_pred_inc = max_pred_inc = 0
    min_pred_dec = max_pred_dec = 0
    gap = 0.02
    curr_plot_bias_inc = 0
    curr_plot_bias_dec = 0

    # "field" column in each data matrix
    data_dict_inc['B_G'] = upper_line_1B
    data_dict_dec['B_G'] = upper_line_1B[::-1]

    # Measurement process
    
    # Sweep magnetic field
    if sweep_mode == SWEEP_MODE_INCR_DECR_ONE_CURVE:
        incr_now = True
        decr_now = False
    elif sweep_mode == SWEEP_MODE_DECR_INCR_ONE_CURVE:
        decr_now = True
        incr_now = False
    else:
        incr_now = (sweep_mode != SWEEP_MODE_DECR)
        decr_now = (sweep_mode != SWEEP_MODE_INCR)
    
    # Sweep bias current
    for k, v0 in enumerate(v0_sweep):
        curr = (v0 / shell.R) / shell.k_A  # bias current now
        now_current = v0 / shell.R
        print('-------------Bias current now is:', now_current*1e+9, 'nA', '-----------------')
        
        time_mgr.OneSweepStepBegin()
        iv_sweeper.SetOutput(v0)

        voltValues_inc = []
        voltValues_dec = []
        fieldValues_inc = []
        fieldValues_dec = []
        resValues_inc = []
        resValues_dec = []
        pw.SetHeader(tabVB, f'I={v0 / shell.R:.5f}')
        
        # increasing sweep
        if incr_now:
            print('Ramping field upwards')
            for curr_field in sweeper_incr:
                pw.SetHeader(tabVB, f'I={(v0 / shell.R) / shell.k_A:.5f} {core_units[shell.k_A]}A, '
                                   f'U={v0:.5f}, T={FormatTemperature(T)}')

                curr_volt = iv_sweeper.MeasureNow(6) / shell.gain  # in volts
                
                fieldValues_inc.append(curr_field)
                voltValues_inc.append(curr_volt / shell.k_V_meas)  # in required units

                resValues_inc.append(curr_volt / now_current)
                pw.updateScatter2D(tabVB, fieldValues_inc, voltValues_inc)
                pw.updateScatter2D(tabVB_resistance, fieldValues_inc, resValues_inc)                
                
                if f_exit.is_set():
                    exit(0)
                
            data_dict_inc[f'V_{curr:.5f}'] = copy(voltValues_inc)
            data_dict_inc[f'R_{curr:.5f}'] = copy(resValues_inc)
            LocalSaveIncr()
            
            # plot on common graph
            # plot without offset
            pw.plotOnScatter2D(tabVBForwardNoOffset, fieldValues_inc, voltValues_inc,
                               f'I={(v0 / shell.R) / shell.k_A:.3f} {core_units[shell.k_A]}A', 'o', markersize=4)
            pw.SetHeader(tabVBForwardNoOffset, f'T={FormatTemperature(T)} mK')
            
            # offset implementation
            if k != 0:
                max_now = np.max(voltValues_inc)
                min_now = np.min(voltValues_inc)
                t = max((max_now - min_now), (max_pred_inc - min_pred_inc))
                distance = t * gap + (max_pred_inc - min_pred_inc)
                voltValues_inc += distance + curr_plot_bias_inc
                curr_plot_bias_inc += (max_now + distance)
                
            # plot offset
            pw.plotOnScatter2D(tabVBForwardOffset, fieldValues_inc, voltValues_inc,
                               f'I={(v0 / shell.R) / shell.k_A:.3f} {core_units[shell.k_A]}A', 'o', markersize=4)
            pw.SetHeader(tabVBForwardOffset, f'T={FormatTemperature(T)} mK')

            # offset algorithm part
            # save current values to calculate distance between this and the next curve
            min_pred_inc = np.min(voltValues_inc)
            max_pred_inc = np.max(voltValues_inc)
        
        # decreasing sweep
        if decr_now:
            print('Ramping field downwards')
            for curr_field in sweeper_decr:
                curr_volt = iv_sweeper.MeasureNow(6) / shell.gain  # in volts
                fieldValues_dec.append(curr_field)
                voltValues_dec.append(curr_volt / shell.k_V_meas)  # in required units

                resValues_dec.append(curr_volt / now_current)
                pw.updateScatter2D(tabVB, fieldValues_dec, voltValues_dec)
                pw.updateScatter2D(tabVB_resistance, fieldValues_dec, resValues_dec)
                
                if f_exit.is_set():
                    exit(0)
        
            # add data to common dictionary
            data_dict_dec[f'V_{curr:.5f}'] = copy(voltValues_dec)[::-1]
            data_dict_dec[f'R_{curr:.5f}'] = copy(resValues_dec)[::-1]

            LocalSaveDecr()
            pw.plotOnScatter2D(tabVBReverseNoOffset, fieldValues_dec, voltValues_dec,
                           f'I={(v0 / shell.R) / shell.k_A:.3f} {core_units[shell.k_A]}A', 'o', markersize=4)
            pw.SetHeader(tabVBReverseNoOffset, f'T={FormatTemperature(T)} mK')
            
            if k != 0:
                max_now = np.max(voltValues_dec)
                min_now = np.min(voltValues_dec)
                t = max((max_now - min_now), (max_pred_dec - min_pred_dec))
                distance = t * gap + (max_pred_dec - min_pred_dec)
                voltValues_dec += distance + curr_plot_bias_dec
                curr_plot_bias_dec += (max_now + distance)
                
            pw.plotOnScatter2D(tabVBReverseOffset, fieldValues_dec, voltValues_dec,
                           f'I={(v0 / shell.R) / shell.k_A:.3f} {core_units[shell.k_A]}A', 'o', markersize=4)
            pw.SetHeader(tabVBReverseOffset, f'T={FormatTemperature(T)} mK')
            
            max_pred_dec = np.max(voltValues_dec)
            min_pred_dec = np.min(voltValues_dec)
        
        # revert mode to the next curve
        if sweep_mode in [SWEEP_MODE_INCR_DECR_ONE_CURVE, SWEEP_MODE_DECR_INCR_ONE_CURVE]:
            incr_now = not incr_now
            decr_now = not decr_now

        time_mgr.OneSweepStepEnd(k + 1)

    # end for V
    EquipmentCleanup()
    f_exit.set()


def GetTemperatureThreadProc():
    global T
    T = LoadTemperatureFromLogs()


shell = ScriptShell()
Log = Logger(shell, 'V_B')

# Solenoid current values (will be generated by Yokogawa 2) (always mA!!!)
try:
    fromA_B, toA_B, stepA_B, bias_start, bias_end, bias_step, sweep_mode = \
        [float(i) for i in shell.user_params.split(';')]

except Exception:  # default value if params are not specified in command-line
    fromA_B = -200
    toA_B = 200  # mA
    stepA_B = 50  # mA
    bias_start = 2.25  # mA
    bias_end = 2.69  # mA
    bias_step = 30  # V
    print('Using default values: ')
print('Field sweep range: from', fromA_B, 'G, to:', toA_B, ' G, step is', stepA_B, 'G')
print(f'Bias current: from {bias_start} mkA to {bias_end} mkA, with step {bias_step}')

upper_line_1B = np.arange(fromA_B, toA_B, stepA_B)
# Magnetic field values: from - to +, then from + to -

fields_incr = np.arange(fromA_B, toA_B, stepA_B)
fields_decr = np.arange(toA_B, fromA_B, -stepA_B)

# Initialize devices
iv_sweeper = EquipmentBase(shell)
if isinstance(shell.field_gate_device_id, int):
    print('Using Yokogawa, ID = ', shell.field_gate_device_id, 'for magnetic field control')
    Field_controller = YokogawaGS200(device_num=shell.field_gate_device_id, dev_range='2E-1', what='CURR')
else:
    print('Using AMI430, ID = ', shell.field_gate_device_id, 'for magnetic field control')
    Field_controller = AMI430(shell.field_gate_device_id, fields_incr)

# Current parameters
v0_sweep = np.linspace(bias_start*1E-6 * shell.R, bias_end*1E-6 * shell.R, int(bias_step))
print(len(v0_sweep), 'points')
# Measurement result
data_dict_inc = {}
data_dict_dec = {}

# Exit main thread when window closed
f_exit = threading.Event()

# Temperature (will be read from logs)
T = 0

# Remaining (estimated) time
time_mgr = TimeEstimator(len(v0_sweep))
pw = plotWindow("V-B measurement", color_buttons=False)

tabVB = pw.addScatter2D('V-B (now)', "$B, G$", fr'$U, {core_units[shell.k_V_meas]}V$', markersize=3)
tabVB_resistance = pw.addScatter2D('R-B(now)', "$B, G$", r"R, $\Omega$")
tabVBForwardOffset = pw.addScatter2D('V-B, forward (with offset)', "$B, Gs$", fr'$U, {core_units[shell.k_V_meas]}V$')
tabVBReverseOffset = pw.addScatter2D('V-B, reverse (with offset)', "$B, Gs$", fr'$U, {core_units[shell.k_V_meas]}V$')
tabVBForwardNoOffset = pw.addScatter2D('V-B, forward (no offset)', "$B, Gs$", fr'$U, {core_units[shell.k_V_meas]}V$')
tabVBReverseNoOffset = pw.addScatter2D('V-B, reverse (no offset)', "$B, Gs$", fr'$U, {core_units[shell.k_V_meas]}V$')

if isinstance(shell.field_gate_device_id, int):
    sweeper_incr = FieldUtils.YokogawaFieldSweeper(fields_incr, Field_controller, pw)
    sweeper_decr = FieldUtils.YokogawaFieldSweeper(fields_decr, Field_controller, pw)
else:
    sweeper_incr = FieldUtils.AmericanMagneticsFieldSweeper(fields_incr, Field_controller, pw)
    sweeper_decr = FieldUtils.AmericanMagneticsFieldSweeper(fields_decr, Field_controller, pw)

curr_curr = 0
gui_thread = threading.Thread(target=MainThreadProc)
gui_thread.start()

thermometer_thread = threading.Thread(target=GetTemperatureThreadProc)
thermometer_thread.start()

pw.show()  # show main tabbed window
f_exit.set()


DataSave()

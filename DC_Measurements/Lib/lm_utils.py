# lm_utils - shared function library for Leonardo measurement utilities

from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QTabWidget, QVBoxLayout, QPushButton, \
    QGridLayout, QSizePolicy
from Lib.GoogleDrive import GoogleDriveUploader
from Lib.CloudRQC import NextCloudUploader
import os
from os import path
import sys
import argparse
import threading
import time
from datetime import datetime
from copy import copy
import numpy as np
import pandas as pd
import win32api

MB_ICONSTOP = 0x10

# core_units, r_units
# Coefficients for units transformation and their symbols
core_units = {1: '', 1e-3: 'm', 1e-6: 'mk', 1e-9: 'n'}
r_units = {1: '', 1e+3: 'K', 1e+6: 'M'}

# Excitation and readout device types
EXCITATION_YOKOGAWA = 0
EXCITATION_KEITHLEY_6200 = 1
EXCITATION_KEITHLEY_2400 = 2
READOUT_LEONARDO = 0
READOUT_KEITHLEY_2182A = 1
READOUT_KEITHLEY_2400 = 2

# LakeShore models
LAKESHORE_MODEL_370 = 0
LAKESHORE_MODEL_335 = 1


# class ScriptShell
# parses command line, makes user input if command-line parameters were not set,
# saves data to a folder
class ScriptShell:
    default_yok_read = 3
    default_yok_write = 6
    default_lakeshore = 17
    default_readout = READOUT_LEONARDO
    default_excitation = EXCITATION_YOKOGAWA
    default_readout_id = 8
    default_lakeshore_model = LAKESHORE_MODEL_370

    @staticmethod
    def _preprocess_string_for_filename(s):
        return s.translate(str.maketrans({':': '_', '/': '_', '\\': '_', '*': '_', '?': '_', '"': '_',
                                          '>': '_', '<': '_', '|': '_'}))

    def _format_contacts_name(self, contacts_string):
        lc = contacts_string.split(",")
        return f'I{lc[0]},{lc[1]}V{lc[2]},{lc[3]}'

    def _user_input(self):
        # units
        self.k_R = list(r_units.keys())[int(input('Enter resistance units (1 - Ohm, 2 - KOhm, 3 - MOhm): ')) - 1]
        self.k_V_meas = list(core_units.keys())[int(input('Enter voltage units (1 - V, 2 - mV, 3 - mkV): ')) - 1]
        self.k_A = list(core_units.keys())[int(input('Enter current units (2 - mA, 3 - mkA, 4 - nA): ')) - 1]

        # resistance
        self.R = float(input(f'Enter resistance ({r_units[self.k_R]}Ohms): '))
        self.R *= self.k_R  # always in Ohms

        # measure range
        self.rangeA = float(input('Enter maximal voltage: '))  # 0.5
        self.stepA = float(input('Enter voltage step: '))  # 0.001

        # gain, delay between steps, number of measurements in each point
        self.gain = int(input('Enter voltage gain: '))
        self.step_delay = float(input('Enter delay between steps (sec.): '))
        self.num_samples = int(input('Enter number of measures in each point: '))

        # equipment parameters
        self.excitation_device_id = self.default_yok_read
        self.field_gate_device_id = self.default_yok_write
        self.lakeshore = self.default_lakeshore
        self.lakeshore_model = LAKESHORE_MODEL_370

        self.readout_device_type = self.default_readout
        self.excitation_device_type = self.default_excitation
        self.readout_device_id = self.default_readout_id

        self.f_save = True
        self.user_params = ""

    def __init__(self, title):
        self._save_path = None
        self.sample_name = ""
        self.structure_name = ""
        self.experimentDate = datetime.now()
        self.contacts = ""
        self.title = title

        if len(sys.argv) == 1:  # user did not specify everything in command line
            self._user_input()

        else:
            # first - key arguments : -mkV, nA, -kOhm etc...
            # then - possible -nosave argument - don't save data
            # then 6 positional arguments:
            # resistance, Yokogawa range, Yokogawa step, voltage gain, delay between steps, number of points to measure
            try:
                p = argparse.ArgumentParser()

                p.add_argument('-RT', action='store', required=False, default=self.default_readout)
                p.add_argument('-WT', action='store', required=False, default=self.default_excitation)
                p.add_argument('-RR', action='store', required=False, default=self.default_readout_id)
                p.add_argument('-LT', action='store', required=False, default=self.default_lakeshore_model)

                p.add_argument('-R', action='store', required=False, default=self.default_yok_read)
                p.add_argument('-W', action='store', required=False, default=self.default_yok_write)
                p.add_argument('-L', action='store', required=False, default=self.default_lakeshore)
                p.add_argument('-P', action='store', required=False, default="")

                p.add_argument('-C', action='store', required=False, default="1,2,3,4")
                p.add_argument('-ST', action='store', required=False, default="Structure1")
                p.add_argument('-CC', action='store', required=False, default="1")

                p.add_argument('-nV', action='store_true')
                p.add_argument('-mkV', action='store_true')
                p.add_argument('-mV', action='store_true')
                p.add_argument('-V', action='store_true')

                p.add_argument('-nA', action='store_true')
                p.add_argument('-mkA', action='store_true')
                p.add_argument('-mA', action='store_true')
                p.add_argument('-A', action='store_true')

                p.add_argument('-KOhm', action='store_true')
                p.add_argument('-MOhm', action='store_true')
                p.add_argument('-Ohm', action='store_true')

                p.add_argument('-nosave', action='store_true')

                p.add_argument('Resistance', action='store')
                p.add_argument('Range', action='store')
                p.add_argument('Step', action='store')
                p.add_argument('Gain', action='store')
                p.add_argument('StepDelay', action='store')
                p.add_argument('NumSamples', action='store')
                args, unknown = p.parse_known_args()

                args = vars(args)
                self.sample_name = " ".join(unknown)
                print('Sample:', self.sample_name)

                for coef, name in core_units.items():
                    if args[f'{name}A']:
                        self.k_A = coef
                    if args[f'{name}V']:
                        self.k_V_meas = coef

                for coef, name in r_units.items():
                    if args[f'{name}Ohm']:
                        self.k_R = coef

                self.R = float(args['Resistance'])
                self.R *= self.k_R  # always in Ohms
                self.rangeA = float(args['Range'])
                self.stepA = float(args['Step'])
                self.gain = int(args['Gain'])
                self.step_delay = float(args['StepDelay'])
                self.num_samples = int(args['NumSamples'])

                self.structure_name = args['ST']
                self.contacts = self._format_contacts_name(args['C'])

                f_save = not args['nosave']
                if not f_save:
                    print('Warning! Data will not be saved!')
                self.f_save = f_save

                self.excitation_device_id = int(args['R'])
                field_gate_device_id = args['W']
                self.lakeshore = int(args['L'])

                self.excitation_device_type = int(args['WT'])
                self.readout_device_type = int(args['WT'])
                self.read_device_id = int(args['RR'])
                self.lakeshore_model = int(args['LT'])
                self.coil_constant = float(args['CC'])

                self.field_gate_device_id = int(field_gate_device_id) if field_gate_device_id.isdigit() \
                    else field_gate_device_id

                self.user_params = args['P'][1: -1]  # remove quotes

            except Exception as e:
                print('Error during command line parsing:')
                print(e)
                self._user_input()

        self.I_units = core_units[self.k_A]
        self.V_units = core_units[self.k_V_meas]
        self.sample_name = self._preprocess_string_for_filename(self.sample_name)
        self.structure_name = self._preprocess_string_for_filename(self.structure_name)
        # print('R=', self.R, 'R*', self.k_R, 'V*', self.k_V_meas, 'A*', self.k_A)  # for debugging

    def _get_measurement_id(self, caption, for_folder):
        if for_folder:
            return f'{self.structure_name}_{self.contacts}_{caption.split("_")[0]}'
        else:
            return f'{self.structure_name}_{self.contacts}_{caption}'

    # GetSaveFolder
    # Get a directory to save experiment data
    # If folder not exists, creates it
    # Parameters:
    # caption - additional string to be added to the end of file
    def GetSaveFolder(self, caption=None):
        if self._save_path is not None:
            return self._save_path
        # get current date only one time
        # to prevent case when part of saved files will have date, for example, 12:00
        # and another part - 12:01

        experimentDate = self.experimentDate
        if caption is None:
            caption = self.title

        cd_first_with_date = experimentDate.strftime('%d-%m-%Y') + '_' + self.sample_name
        cd_this_meas = experimentDate.strftime('%H-%M') + '_' + self._get_measurement_id(caption, for_folder=True)
        save_path = path.join(os.getcwd(), 'Data', cd_first_with_date, cd_this_meas)

        if not path.isdir(save_path):
            os.makedirs(save_path)

        self._save_path = save_path
        return save_path

    # Function GetSaveFileName
    # Get a filename to save
    # Parameters:
    # caption - additional string to be added to the end of file
    def GetSaveFileName(self, caption=None, ext="dat", preserve_unique=True):
        if caption is None:
            caption = self.title
        save_path = self.GetSaveFolder(caption)

        cd = self.experimentDate.strftime('%d-%m-%Y_%H-%M')
        meas_id = self._get_measurement_id(caption, for_folder=False)

        filename = path.join(save_path, f'{cd}_{meas_id}.{ext}')

        # if file, even with this minutes, already exists
        if preserve_unique:
            k = 0
            while os.path.isfile(filename):
                k += 1
                filename = path.join(save_path, f'{cd}_{meas_id}_{k}.{ext}')

        return filename

    # Function SaveData
    # Saves measured data into specified file
    # Parameters:
    # caption - additional string to be added to the end of file
    # data_dict - a dictionary which has a format:
    # {columnName1:[data1, data1,...], columnName2:[data2, data2,...]}
    def SaveData(self, data_dict, caption=None, preserve_unique=True):
        if caption is None:
            caption = self.title
        fname = self.GetSaveFileName(caption=caption, preserve_unique=preserve_unique)

        df = pd.DataFrame(data_dict)
        df.to_csv(fname, sep=" ", header=True, index=False, float_format='%.8f')

        print('Data were successfully saved to:', fname)

    def SaveMatrix(self, all_swept_values, all_currents, all_voltages, rows_header, caption=None):
        def split_curve(curve):
            N_points = len(curve) // 4

            upper_quarter_1 = curve[:N_points]
            down_quarter_2 = curve[N_points:2 * N_points]
            down_quarter_3 = curve[2 * N_points:3 * N_points]
            upper_quarter_4 = curve[3 * N_points:4 * N_points]

            crit_curve = np.hstack((down_quarter_3[::-1], upper_quarter_1))
            retr_curve = np.hstack((upper_quarter_4, down_quarter_2[::-1]))

            return list(crit_curve), list(retr_curve)

        if caption is None:
            caption = self.title

        fname = self.GetSaveFileName(caption + '_matrix')
        fname_c = self.GetSaveFileName(caption + '_matrix_Ic')
        fname_r = self.GetSaveFileName(caption + '_matrix_Ir')
        fname_c_deriv = self.GetSaveFileName(caption + '_matrix_Ic_derivative')
        fname_r_deriv = self.GetSaveFileName(caption + '_matrix_Ir_derivative')

        swept_values = sorted(list(set(all_swept_values)))
        one_stweepstep_length = int(
            len(all_swept_values) // len(
                swept_values))  # assume that every sweep step contains the same number of points
        currents = list(all_currents[:one_stweepstep_length])  # and current (I) points are always equal
        currents_crit, currents_retr = split_curve(currents)

        left_header = currents
        columns = {}

        left_header_c = currents_crit
        columns_c = {}

        left_header_r = currents_retr
        columns_r = {}

        columns_deriv = {}
        columns_c_deriv = {}
        columns_r_deriv = {}

        for i, val in enumerate(swept_values):
            voltages_now = all_voltages[i * one_stweepstep_length: (i + 1) * one_stweepstep_length]  # add header
            voltages_crit, voltages_retr = split_curve(voltages_now)

            columns[val] = voltages_now
            columns_c[val] = voltages_crit
            columns_r[val] = voltages_retr

            columns_deriv[val] = np.gradient(voltages_now)
            columns_c_deriv[val] = np.gradient(voltages_crit)
            columns_r_deriv[val] = np.gradient(voltages_retr)

        df_save = pd.DataFrame(columns, index=left_header)
        df_save.to_csv(fname, sep=" ", header=True, index=True, float_format='%.8f', index_label=rows_header)
        print('Data were successfully saved to:', fname)

        df_save_c = pd.DataFrame(columns_c, index=left_header_c)
        df_save_c.to_csv(fname_c, sep=" ", header=True, index=True, float_format='%.8f', index_label=rows_header)

        df_save_r = pd.DataFrame(columns_r, index=left_header_r)
        df_save_r.to_csv(fname_r, sep=" ", header=True, index=True, float_format='%.8f', index_label=rows_header)

        df_save_c_deriv = pd.DataFrame(columns_c_deriv, index=left_header_c)
        df_save_c_deriv.to_csv(fname_c_deriv, sep=" ", header=True, index=True, float_format='%.8f',
                               index_label=rows_header)

        df_save_r_deriv = pd.DataFrame(columns_r_deriv, index=left_header_r)
        df_save_r_deriv.to_csv(fname_r_deriv, sep=" ", header=True, index=True, float_format='%.8f',
                               index_label=rows_header)

    # Function UploadToClouds
    # Uploads measured data to all possible cloud storages
    def UploadToClouds(self):
        save_dir = self._save_path
        up = GoogleDriveUploader()
        up.UploadMeasFolder(save_dir)
        nc = NextCloudUploader()
        nc.UploadFolder(save_dir)


# Function FindCriticalCurrents
# Looks for critical current (Ic+ and Ic-) points
# input:
# R_array - resistance values (voltage gradient)
# threshold - threshold (how much times a gradient must be bigger than its average value to detect a rapid growth)
# output: list [Ic-, Ic+]
def FindCriticalCurrent(I_array, U_array, threshold=1.5):
    res = [0, 0]
    R_values = np.abs(np.gradient(U_array))
    avg = np.mean(R_values)
    Np = len(R_values)
    try:
        peaks = np.array(np.where(R_values > threshold * avg))[0]
        peaks_left = [peaks[i] for i in np.where(peaks < Np // 2)]
        peaks_right = [peaks[i] for i in np.where(peaks >= Np // 2)]
        peaks_final = (int(np.average(peaks_left)), int(np.average(peaks_right)))
        res = [I_array[peaks_final[0]], I_array[peaks_final[1]]]
    except Exception:  # If cannot find peaks, return a default value (zero)
        pass
    return res


# Function LoadTemperatureFromLogs
# Waits for newest LakeShore log to appear, and gets a last temperature from it
def LoadTemperatureFromLogs():
    strError = 'Check that BlueFors software is started and logging is turned on.'
    k_temp = 1000  # to millikelvin from logged value
    now_date = datetime.now()
    now_date_str = now_date.strftime("%Y-%m-%d")[2:]
    logPath = os.path.join(r'C:\BlueFors Logs', now_date_str, f'CH6 T {now_date_str}.log')

    if not os.path.isfile(logPath):
        print('Cannot detect temperature logs on your computer.')
        print(strError)
        return 0

    file_date0 = datetime.utcfromtimestamp(os.path.getmtime(logPath))
    file_date = copy(file_date0)

    print('Waiting for a newest log, it will waste <= 1 minute...')

    n = 0
    while file_date == file_date0:
        file_date = datetime.utcfromtimestamp(os.path.getmtime(logPath))
        time.sleep(1)
        n += 1
        if n >= 90:
            print('Failed to get temperature from logs!')
            print('It seems like BlueFors software is not updating logs.')
            print(strError)
            return 0

    try:
        with open(logPath, 'r') as f:
            log_str = list(f)[-1].strip()

        T = float(log_str.split(',')[2])
    except Exception:
        print('Error reading log file! Check BlueFors software settings.')
        return 0
    return T


# Class plotWindow
# A window with multiple tabs and a plot on each one
class plotWindow:

    # hide Qt warning messages
    def __handler(self, b, c, d):
        pass

    # tab switch event handler
    def __onChange(self, i):
        if self.__shown:
            self.canvases[i].draw()
        self.__currtab = i
        if self.__userCallback is not None:
            self.__userCallback()

    def __init__(self, title, parent=None, color_buttons=True):
        self.buttons_step = 0.1  # buttons range percentage change
        plt.rcParams.update({'font.size': 15})

        # hide Qt warning messages
        qInstallMessageHandler(self.__handler)

        # window parameters
        self.__currtab = 0
        self.__total_tabs = 0
        self.__shown = False
        self.__tab_info = []  # an array of objects containing a custom information about each tab
        self.__figures = []
        self.__axes = []
        self.__objects = []  # line/pcolormesh for each tab
        self.__userCallback = None

        # initialize and show a window
        self.app = QApplication(sys.argv)
        self.app.setAttribute(Qt.AA_EnableHighDpiScaling)
        self.MainWindow = QMainWindow()
        self.MainWindow.__init__()
        self.MainWindow.setWindowTitle(title)
        self.canvases = []
        self.figure_handles = []
        self.toolbar_handles = []
        self.tab_handles = []
        self.current_window = -1
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.__onChange)

        if color_buttons:
            self.c = QWidget()  # required to be a base widget, because it is impossible to simple place widgets onto a main window
            # I wish mother of PyQT5 developer to dead

            self.decButton = QPushButton('Decrease range')
            self.incButton = QPushButton('Increase range')

            self.layout = QGridLayout()
            self.c.setLayout(self.layout)
            self.layout.addWidget(self.decButton, 1, 0)
            self.layout.addWidget(self.incButton, 1, 1)
            self.layout.addWidget(self.tabs, 0, 0, 1, 2)

            self.decButton.clicked.connect(self.__handler_dec)
            self.incButton.clicked.connect(self.__handler_inc)

            self.MainWindow.setCentralWidget(self.c)
        else:
            self.MainWindow.setCentralWidget(self.tabs)

        self.MainWindow.resize(1280, 900)
        self.MainWindow.show()

    # creates x and y ticks in a color mesh
    def __make_ticks(self, ax, new_xrange, new_yrange, n_ticks):
        lb, ub = ax.get_xlim()
        new_xticks = np.linspace(lb, ub, n_ticks)
        new_xlabels = np.around(np.linspace(min(new_xrange), max(new_xrange), n_ticks), decimals=4)
        ax.set_xticks(new_xticks)
        ax.set_xticklabels(new_xlabels)

        lb, ub = ax.get_ylim()
        new_yticks = np.linspace(lb, ub, n_ticks)
        new_ylabels = np.around(np.linspace(min(new_yrange), max(new_yrange), n_ticks), decimals=4)
        ax.set_yticks(new_yticks)
        ax.set_yticklabels(new_ylabels)

    # button press handlers
    @staticmethod
    def __ErrorMessage():
        win32api.MessageBox(0, "Please open a tab with color mesh!", "Error", MB_ICONSTOP)

    def __handler_dec(self):
        ct = self.__currtab
        user_info = self.__tab_info[ct]
        try:
            min_data = user_info['data_min']
            max_data = user_info['data_max']
        except KeyError:
            self.__ErrorMessage()
            return

        quad = self.__objects[ct]

        user_info['now_percent'] -= self.buttons_step
        perc = user_info['now_percent']
        max_data *= perc
        min_data *= perc

        quad.set_clim(min_data, max_data)
        self.canvases[ct].draw()

    def __handler_inc(self):
        ct = self.__currtab
        user_info = self.__tab_info[ct]
        try:
            min_data = user_info['data_min']
            max_data = user_info['data_max']
        except KeyError:
            self.__ErrorMessage()
            return

        quad = self.__objects[ct]

        user_info['now_percent'] += self.buttons_step
        perc = user_info['now_percent']
        max_data *= perc
        min_data *= perc

        quad.set_clim(min_data, max_data)
        self.canvases[ct].draw()

    # Add tab change handler
    def addOnChange(self, callback):
        self.__userCallback = callback

    # A base method to add a new tab
    # All another methods call it
    def addPlot(self, title, figure, **user_defined_info):
        new_tab = QWidget()
        layout = QVBoxLayout()
        new_tab.setLayout(layout)

        figure.subplots_adjust(left=0.15, right=0.90, bottom=0.15, top=0.85, wspace=0.2, hspace=0.2)
        new_canvas = FigureCanvas(figure)
        new_toolbar = NavigationToolbar(new_canvas, new_tab)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHeightForWidth(True)
        new_canvas.setSizePolicy(sizePolicy)
        layout.addWidget(new_canvas)
        layout.addWidget(new_toolbar)
        self.tabs.addTab(new_tab, title)

        # store objects associated with this tab
        self.toolbar_handles.append(new_toolbar)
        self.canvases.append(new_canvas)
        self.figure_handles.append(figure)
        self.tab_handles.append(new_tab)

        # update tabs counter and info about each tab
        self.__total_tabs += 1
        self.__figures.append(figure)
        self.__axes.append(user_defined_info.get('ax', None))
        self.__objects.append(user_defined_info.get('obj', None))
        self.__tab_info.append(dict(user_defined_info))

        return self.__total_tabs - 1  # returns zero-based index of this tab

    def addEmptyPlot(self, title):
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.tick_params(axis='both', direction='in')
        return self.addPlot(title, fig, ax=ax)

    def addColormesh(self, header, xlabel, ylabel, xaxis, yaxis, data_buff, cmap):
        data_min = np.min(data_buff)
        data_max = np.max(data_buff)

        fig, ax = plt.subplots(figsize=(10, 10))
        quad = ax.pcolormesh(data_buff, cmap=cmap)
        ax.set_xlabel(xlabel, fontsize=15)
        ax.set_ylabel(ylabel, fontsize=15)
        ax.tick_params(axis='both', direction='in')
        fig.colorbar(quad)

        return self.addPlot(header, fig, data_min=data_min, data_max=data_max, now_percent=1, ax=ax, fig=fig,
                            obj=quad)  # fig, ax, quad

    def updateColormesh(self, n, buff, xticks, yticks, n_ticks):
        this_info = self.__tab_info[n]
        ax = self.__axes[n]
        quad = self.__objects[n]

        quad.set_array(np.ravel(buff))  # must be flattened

        data_min, data_max = np.min(buff), np.max(buff)
        perc = this_info['now_percent']
        quad.set_clim(data_min * perc, data_max * perc)

        self.__make_ticks(ax, xticks, yticks, n_ticks)

        this_info['data_min'] = np.min(buff)
        this_info['data_max'] = np.max(buff)

        self.canvases[n].draw()

    # Add 2D plot without any line (to add them manually later)
    def addEmptyLine2D(self, header, xlabel, ylabel):
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.tick_params(axis='both', direction='in')
        ax.set_xlabel(xlabel, fontsize=15)
        ax.set_ylabel(ylabel, fontsize=15)
        ax.grid()

        return self.addPlot(header, fig, ax=ax, fig=fig)  # fig, ax

    # Add new additional line onto 2D plot
    # WARNING! returns a Matplotlib line object
    def addAdditionalLine(self, n):
        ax = self.__axes[n]
        line, = ax.plot([], [])
        return line

    def updateAdditionalLine2D(self, n, line, xvalues, yvalues):
        ax = self.__axes[n]
        line.set_xdata(xvalues)
        line.set_ydata(yvalues)
        ax.relim()
        ax.autoscale_view()
        self.canvases[n].draw()

    def addLine2D(self, header, xlabel, ylabel, **line_kwargs):
        n = self.addEmptyLine2D(header, xlabel, ylabel)
        line, = self.__axes[n].plot([], [], **line_kwargs)
        self.__tab_info[n]['obj'] = line
        self.__objects[n] = line
        return n  # fig, ax, line

    def addScatter2D(self, header, xlabel, ylabel, **line_kwargs):
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.tick_params(axis='both', direction='in')
        line, = ax.plot([], [], 'o', **line_kwargs)
        ax.set_xlabel(xlabel, fontsize=15)
        ax.set_ylabel(ylabel, fontsize=15)
        ax.grid()

        return self.addPlot(header, fig, ax=ax, fig=fig, obj=line)  # fig, ax, line

    def plotOnScatter2D(self, n, x, y, label, marker='o', markersize=4):
        ax = self.__axes[n]

        ax.plot(x, y, marker, markersize=markersize, label=label)
        ax.legend()

    def addLines2D(self, header, titles, xlabel, ylabel, **kwargs_line):
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.tick_params(axis='both', direction='in')
        lines = []
        for tit in titles:
            line_curr, = ax.plot([], [], label=tit, **kwargs_line)
            lines.append(line_curr)
        ax.grid()
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.legend()

        return self.addPlot(header, fig, ax=ax, fig=fig, obj=lines)  # fig, ax, lines

    def updateLines2D(self, n, xdatas, ydatas):
        ax = self.__axes[n]
        lines = self.__objects[n]

        for lin, xi, yi in zip(lines, xdatas, ydatas):
            lin.set_xdata(xi)
            lin.set_ydata(yi)

        ax.relim()
        ax.autoscale_view()
        ax.legend()

        self.canvases[n].draw()

    def updateLine2D(self, n, xdata, ydata, redraw=True):
        ax = self.__axes[n]
        line = self.__objects[n]

        line.set_xdata(xdata)
        line.set_ydata(ydata)
        ax.relim()
        ax.autoscale_view()

        if redraw:
            self.canvases[n].draw()

    def updateScatter2D(self, n, xdata, ydata, redraw=True):
        self.updateLine2D(n, xdata, ydata, redraw=True)

    def MarkPointOnLine(self, n, x, y, marker='o', markersize=4):
        ax = self.__axes[n]
        ax.plot([x], [y], marker, markersize=markersize)
        self.canvases[n].draw()

    def add3DPlot(self, header, xlabel, ylabel, zlabel):
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        X = np.array([])
        Y = np.array([])
        Z = np.array([[]])
        X, Y = np.meshgrid(X, Y)
        ax.plot_surface(X, Y, Z)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_zlabel(zlabel)
        # keep axes titles in user-defined field of this tab to redraw them after each update
        # because they will be lost after each redraw

        return self.addPlot(header, fig, ax=ax, fig=fig, xlabel=xlabel, ylabel=ylabel, zlabel=zlabel)  # fig, ax

    def update3DPlot(self, n, X, Y, Z, xaxis, cmap):
        ax = self.__axes[n]
        user_data = self.__tab_info[n]

        ax.clear()
        ax.set_xlim(xaxis[0], xaxis[-1])
        ax.set_ylim(np.min(Y), np.max(Y))
        ax.set_zlim(np.min(Z), np.max(Z))

        X, Y = np.meshgrid(X, Y)
        ax.plot_surface(X, Y, Z, cmap=cmap)  # Spectral_r)
        ax.relim()
        ax.autoscale_view()

        ax.set_xlabel(user_data['xlabel'])
        ax.set_ylabel(user_data['ylabel'])
        ax.set_zlabel(user_data['zlabel'])

        self.canvases[n].draw()

    def show(self):
        self.__shown = True
        self.app.exec_()

    # Shows a string in every plot header
    def ShowTitle(self, mess):
        for ax in self.__axes:
            ax.set_title(mess)

    @property
    def CurrentTab(self):
        return self.__currtab

    @property
    def Axes(self):
        return self.__axes

    @property
    def Figures(self):
        return self.__figures

    # returns a base object (line, array of lines, pcolormesh, etc...)
    @property
    def CoreObjects(self):
        return self.__objects

    @property
    def TabsCount(self):
        return self.__total_tabs

    def SaveFigureToPDF(self, nfig, pp=None):
        # sometimes an exception may be raised if a measurement was aborted
        try:
            pp.savefig(self.__figures[nfig])
        except Exception:
            print('Error saving PDF')

    def SaveFigureToOneFile(self, nfig, filename):
        self.__figures[nfig].savefig(filename)
        print('Plot was successfully saved to:', filename)

    def SaveAllToPDF(self, pp):
        for fig in self.__figures:
            pp.savefig(fig)

    # call it periodically for each 3d plot tab to allow mouse scrolling
    def MouseInit(self, n):
        self.__axes[n].mouse_init()

    # update tab plot header
    def SetHeader(self, n, header):
        self.__axes[n].set_title(header)


# Decorator MeasurementProc
# Installs an exception handler which turns off equipment if something goes wrong
# Argument: cleanup procedure (must turn off all currents, voltages and magnetic fields)
def MeasurementProc(cleanup_func):
    def PutinIsAThief(func):  # real decorator

        def func_to_make():
            try:
                func()
            except Exception as e:
                print('Error during measurement process, all equipment will be turned off.')
                print(e)
                cleanup_func()

        return func_to_make

    return PutinIsAThief


# function UpdateResistance
# Calculates a resistance, returns it and puts it onto a plot header
def UpdateResistance(ax, I_for_R, U_for_R):
    try:
        resist = abs(np.polyfit(I_for_R, U_for_R, 1)[0])
    except np.linalg.LinAlgError:
        resist = 0
    except TypeError:
        resist = 0
    ax.set_title(f'Resistance is {resist:.6f} Ohm')
    return resist


class TimeEstimator:
    def __init__(self, n_measurements):
        self.__f_first = True
        self.__startTime = None
        self.__endTime = None
        self.__nowTime = None
        self.__N = n_measurements

    @staticmethod
    def __FormatEstimatedTime(secs):
        hours = secs // 3600
        minutes = (secs % 3600) // 60
        seconds = secs % 60
        return f'{hours:.0f} h, {minutes:.0f} mm, {seconds:.0f} ss'

    def __EstimateMeasurementTime(self):
        timedelta = abs(self.__endTime - self.__startTime)
        secs = timedelta.seconds * self.__N
        print(f'Total measurement time: {self.__FormatEstimatedTime(secs)}')

    def __UpdateMeasurementTime(self, measured_now):
        estimated_time = abs(self.__nowTime - self.__startTime).seconds
        new_one_time = estimated_time / measured_now
        total_new_time = new_one_time * self.__N
        remaining = total_new_time - estimated_time
        print('\n')
        print(f'Time from start: {self.__FormatEstimatedTime(estimated_time)}')
        print(f'---Remaining: {self.__FormatEstimatedTime(remaining)}')
        print('\n')

    def OneSweepStepBegin(self):
        if self.__f_first:
            self.__startTime = datetime.now()

    def OneSweepStepEnd(self, measured_now):
        if self.__f_first:
            self.__endTime = datetime.now()
            self.__f_first = False
            self.__EstimateMeasurementTime()
        else:
            self.__nowTime = datetime.now()
            self.__UpdateMeasurementTime(measured_now)


class Logger:
    def __init__(self, shell):
        caption = shell.title
        self.__filename = shell.GetSaveFileName(caption + '_params', ext='log')
        self.__lines = []

        self.AddGenericEntry(
            f'CurrentRange={(shell.rangeA / shell.R) / shell.k_A} {core_units[shell.k_A]}A;'
            f'CurrentStep={(shell.stepA / shell.R) / shell.k_A} {core_units[shell.k_A]}A; '
            f'Gain={shell.gain}; IVPointDelay={shell.step_delay} sec; LeonardoPoints={shell.num_samples}')

    def AddGenericEntry(self, text):
        self.__lines.append(text + '\n')

    def AddParametersEntry(self, swept_caption, swept_value, swept_units, **params):
        strAdd = f'{swept_caption} = {swept_value} {swept_units}'
        for p, v in params.items():
            strAdd += f'; {p} = {v}'
        self.AddGenericEntry(strAdd)

    def Save(self):
        with open(self.__filename, 'w') as f:
            for line in self.__lines:
                f.write(line)
        print('Log was saved to:', self.__filename)
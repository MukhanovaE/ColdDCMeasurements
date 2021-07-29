# A driver for manipulating LakeShore resistance bridge to control a temperature in a cryostat.
# Two working modes are supported: active and passive.
# In active mode, a temperature is automatically swept and controlled.
# In passive mode one can only read a current temperature.

from Drivers.LakeShoreBase import *
import numpy as np
import time
import threading

MAX_TEMP = 1.7  # WARNING!!! Must be <=1.7!!!


# class LakeShore370
# A base class for device manipulation
class LakeShore370(LakeShoreBase):

    # device parameter setters
    def _set_pid(self, pid):
        self.device.write(f'PID {pid}')
        super()._set_pid(pid)

    def _set_heater_range(self, htrrng):
        self.device.write(f'HTRRNG {htrrng}')
        super()._set_heater_range(htrrng)

    def _set_excitation(self, excitation):
        self.device.write(
            f'RDGRNG {self._temp_channel}, 0, {excitation}, 14, 1, 0')  # 6 chan, 0 - voltage exc.,
                                                # n_setting, 14 - 6.32 kOhm, 1 - autorange on, 0 - excitation on(!!!)
        super()._set_excitation(excitation)
        
    def _set_channel(self, chan):
        self.SendString(f'SCAN {chan},0')
        super()._set_channel(chan)

    # Functions for updating LakeShore params depending on temperature
    # Updates thermometer excitation in dependence of temperature
    @staticmethod
    def _get_excitation_for_temperature(temp):
        currTemp = temp * 1000
        # edges and values are obtained experimentally
        if currTemp <= 100:
            n_setting = 2
        elif 100 < currTemp <= 350:
            n_setting = 3
        elif 350 < currTemp <= 400:
            n_setting = 5
        elif 400 < currTemp <= 600:
            n_setting = 6
        elif 600 < currTemp <= 1500:
            n_setting = 7
        elif 1500 < currTemp <= 1800:
            n_setting = 8
        elif 1800 < currTemp <= 6000:  # > 1800
            n_setting = 10
        else:  # if currTemp > 6000:
            n_setting = 12
        return n_setting

    @staticmethod
    def _get_heater_range_from_temperature(temp):
        return 7 if temp < 5 else 8

    def _get_pid_from_temperature(self, temp):
        return '10, 20, 20' if temp > 1.5 else self.__old_pid

    def _remember_old_params(self):
        self.__old_settings = self.GetString('RDGRNG? 6')
        self.__old_pid = self.GetString('PID?')
        self.__pid = self.__old_pid

    def _restore_old_params(self):
        self.device.write(f'RDGRNG {self._temp_channel}, {self.__old_settings}')
        self._set_pid(self.__old_pid)

    # Prints current controller parameters
    def PrintParams(self):
        units_l = ['Kelvin', 'Ohm']
        filts = ['No', 'Yes']
        cp = ['Current', 'Power']
        ranges = ['Off', '31.6 mkA', '100 mkA', '316 mkA', '1 mA', '3.16 mA', '10 mA', '31.6 mA', '100 mA']
        modes = ['Closed loop PID', 'Zone tuning', 'Open loop', 'Off']

        try:
            res = self.GetString('CSET?').rstrip().split(',')
            chan, filt, units, delay, currpow, limit = (int(i) for i in res[:-1])
            resist = float(res[-1])

            mode = int(self.GetString('CMODE?').rstrip())
            print('Control mode:', modes[mode - 1])

            print('Control channel: ', chan, '\nFiltering:', filts[filt - 1], '\nSetpoint units', units_l[units - 1],
                  '\nSetpoint delay', delay,
                  'Heater out diplay', cp[currpow - 1], 'Heater limit:', ranges[limit - 1], 'Heater resistance:',
                  resist)

            pid = [float(i) for i in self.GetString('PID?').rstrip().split(',')]
            print(f'P={pid[0]}, I={pid[1]}, D={pid[2]}')
        except ValueError:
            print('LakeShore returned an invalid response.')

    # Measures a current temperature
    def _meas_temperature(self):
        return self.GetFloat(f'RDGK? {self._temp_channel}')

    # Changes a setpoint
    def _set_setpoint(self, setp):
        self.SendString(f'SETP {setp}')

    def _set_control_mode(self, mode:PIDLoopType):
        # in a device: 1 - closed loop, 3 - open loop, 4 = off
        class_to_device = {PIDLoopType.open_loop: 3,
                           PIDLoopType.close_loop: 1,
                           PIDLoopType.off: 4}

        self.SendString(f'CMODE {class_to_device[mode]}')


# for debugging purposes, doesn't actually change or measure a temperature
class DebugLakeShore370:

    def __init__(self, device_num=17, temp0=None, max_temp=MAX_TEMP, verbose=True, mode="active",
                 tempStep=0.1):
        self.__verbose = verbose
        self._set_channel(6)
        if mode == 'passive':
            self.__dummy_temp = self.__temp_channel
        else:
            initialTemp = temp0 if temp0 is not None else 0.015
            self.__tempValues = np.arange(initialTemp, max_temp, tempStep)
            self.__dummy_temp = temp0

        if self.__verbose:
            print('LakeShore bridge DEBUG MODE (no real temp. change)')
    
    def _set_channel(self, chan):
        self.__temp_channel = chan
        self.__dummy_temp = self.__temp_channel
        print('Scanning', chan, 'channel')
    
    def GetTemperature(self):
        return self.__dummy_temp

    @property
    def NumTemps(self):
        return len(self.__tempValues)

    @property
    def TempRange(self):
        return self.__tempValues

    def __iter__(self):
        for temp in self.__tempValues:
            self.__dummy_temp = temp
            yield temp
    
    @property
    def pid(self):
        return "10,20,20"

    @property
    def htrrng(self):
        return 7

    @property
    def excitation(self):
        return 2
        
    @property
    def temp_channel(self):
        return self.__temp_channel
        
    @temp_channel.setter
    def temp_channel(self, chan):
        self._set_channel(chan)

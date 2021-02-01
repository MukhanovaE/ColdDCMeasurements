# A driver for manipulating LakeShore resistance bridge to control a temperature in a cryostat.
# Two working modes are supported: active and passive.
# In active mode, a temperature is automatically swept and controlled.
# In passive mode one can only read a current temperature.

from . import visa_device
import numpy as np
import time
import threading

MAX_TEMP = 1.7  # WARNING!!! Must be <=1.7!!!


# An exception to be thrown if we try to control a temperature in a passive mode
class LakeShoreException(Exception):
    def __init(self):
        super().__init__("Temperature sweep is allowed only in active mode")


# class LakeShoreConreoller
# A base class for device manipulation
class LakeShoreController(visa_device.visa_device):

    # Updates thermometer excitation in dependence of temperature
    def __UpdateExcitation(self, T):
        bridge = self.device
        currTemp = T * 1000

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
        else:  # > 1800
            n_setting = 13

        bridge.write(
            f'RDGRNG 6, 0, {n_setting}, 14, 1, 0')  # 6 chan, 0 - voltage exc., n_setting, 14 - 6.32 kOhm, 1 - autorange on, 0 - excitation on(!!!)
        print('Excitation is:', n_setting)
        self.excitation = f'0, {n_setting}, 14, 1, 0'

    def __update_heater_range(self, T):
        if T <= 6:
            self.device.write('HTRRNG 7')
            self.htrrng = 7
        elif T > 6:
            self.device.write('HTRRNG 8')
            self.htrrng = 8

    def __update_pid(self, T):
        if T > 1.5:
            set_pid = '10, 20, 20'
        else:
            set_pid = self.__old_pid
        self.device.write(f'PID {set_pid}')
        print(f'PID is: {set_pid}')
        self.pid = set_pid

    def __update_params(self, T):
        print('---------------')
        print('Temperature is:', T)
        self.__UpdateExcitation(T)
        self.__update_pid(T)
        self.__update_heater_range(T)
        print('---------------')

    def __remember_old_params(self):
        self.__old_settings = self.GetString('RDGRNG? 6')
        self.__old_pid = self.GetString('PID?')
        self.pid = self.__old_pid

    def __restore_old_params(self):
        self.device.write(f'RDGRNG 6, {self.__old_settings}')
        self.device.write(f'PID {self.__old_pid}')

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
            print('LakeShore returned an invalid responce.')

    # A class constructor
    # temp0 - starter swept temperature (if None, use current temperature)
    # max_temp - maximum swept temperature, must be <=1.7 K
    # step - sweep step
    def __init__(self, device_num=17, temp0=None, max_temp=MAX_TEMP, step=100 * 1E-3, verbose=True, mode="active",
                 tempStep=0.1):
        # security check
        # assert max_temp <= 1.7, 'This maximum temperature will boll He mixture in a cryostat'

        self.__verbose = verbose
        self.__active = (mode == "active")

        # Load and configure a device
        if self.__verbose:
            print('Connecting LakeShore bridge...')

        super().__init__(device_num)

        # Event to prevent simultaneous temperature request - it will cause an error
        self.__SensorFree = threading.Event()
        self.__SensorFree.set()

        # remember current heater paramrters to restore them after program end
        self.__remember_old_params()

        # Get initial temperature to start from it
        self.SendString('SCAN 6,0')
        initialTemp = temp0 if temp0 is not None else self.GetTemperature()

        # Set LakeShore control and heating parameters
        if self.__active:
            self.SendString('SETP {}'.format(initialTemp))  # first setpoint
            self.SendString('CMODE 1')  # control mode - closed-loop PID
            self.__update_params(initialTemp)

            # temperature swept values
            self.__tempValues = np.arange(initialTemp, max_temp, tempStep)

        # Time from previous temperature measurement request.
        # It is made to avoid a device to stop responding because of a buffer overflow.
        self.__prev_measured = time.time()

        if self.__verbose:
            print('LakeShore bridge connection success')

    # Measures a temperature now
    def GetTemperature(self):
        self.__SensorFree.wait()  # wait for another thread (if one present) to complete operation

        self.__SensorFree.clear()  # lock for another threads

        # check if previous request was too close in time
        curr_meas = time.time()
        time.sleep(0.5)
        if curr_meas - self.__prev_measured < 1:
            time.sleep(1)
        try:
            resp = self.GetFloat('RDGK? 6')
            temp = np.float64(resp)
            res = temp  # if temp < 100 else np.nan  # correct LakeShore error which occurs at the beginning of measurements
        except Exception:
            res = 0
            print('Error in measuring temperature')
        self.__prev_measured = curr_meas

        self.__SensorFree.set()  # unlock

        return res

    # Number of swept temperature values
    @property
    def NumTemps(self):
        if not self.__active:
            raise LakeShoreException()
        return len(self.__tempValues)

    # All swept temperature values (as Numpy array)
    @property
    def TempRange(self):
        if not self.__active:
            raise LakeShoreException()
        return self.__tempValues

    # iterate over all temperatures and set them on a device
    def __iter__(self):
        if not self.__active:
            raise LakeShoreException()
            return

        tol_temp = 0.001
        for temp in self.__tempValues:
            # assert temp <= 1.7, 'ERROR! Attempt to set too high temperature was made.'
            self.SendString('SETP {}'.format(temp))

            # Update temperature measurement parameters depending on T
            self.__update_params(temp)

            actual_temp = self.GetTemperature()
            print(f'Heating... (target temperature - {temp})')

            # Wait for temperature to be established
            c = 0
            while abs(actual_temp - temp) >= tol_temp:
                time.sleep(1)
                actual_temp = self.GetTemperature()

            # A temperature must be stable for 3 seconds
            print('Temperature is set, waiting to be stable...')
            count_ok = 0
            while count_ok < 3:
                time.sleep(3)
                actual_temp = self.GetTemperature()
                print('Now:', actual_temp, 'K, must be:', temp, 'K')
                if abs(actual_temp - temp) <= tol_temp:
                    count_ok += 1
                    print('Stable', count_ok, 'times')
                else:
                    count_ok = 0
                c += 1
                if c > 50:
                    print('Warning! Cannot set a correct temperature')
                    break

            print('Temperature was set')

            yield actual_temp  # last actual temperature

    # class destructor - turn off a heater and free VISA resources
    def __del__(self):
        # Turn off heater and PID control
        if self.__active:
            self.SendString('HTRRNG 0')
            self.SendString('CMODE 4')
            self.__restore_old_params()

        if self.__verbose:
            print('LakeShore bridge disconnected.')
            if self.__active:
                print('Heater is off.')
                print('Old heater range parameters restored.')


# for debugging purposes, doesn't actually change or measure a temperature
class DebugLakeShoreController:

    def __init__(self, device_num=17, temp0=None, max_temp=MAX_TEMP, tempStep=100 * 1E-3, verbose=True, mode="active"):
        self.__verbose = verbose

        if mode == 'passive':
            self.__dummy_temp = 42
        else:
            initialTemp = temp0 if temp0 is not None else 0.015
            self.__tempValues = np.arange(initialTemp, max_temp, tempStep)
            self.__dummy_temp = temp0
            self.pid = 777
            self.htrrng = 888
            self.excitation = 999

        if self.__verbose:
            print('LakeShore bridge DEBUG MODE (no real temp. change)')

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

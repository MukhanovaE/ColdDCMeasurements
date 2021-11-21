import numpy as np
import time
from scipy.interpolate import interp1d
import pandas as pd

from Lib.PID import PID


class VirtualLakeShore:
    def __init__(self, sense_device, sweep_device, heater_device, temp_start=None, temp_range=None, temp_step=None,
            max_thermometer_current=1e-6, mode='passive'):
        self._sense = sense_device
        self._sweep = sweep_device


        self._sweep_seq = [0, max_thermometer_current]  # np.linspace(0, max_thermometer_current, 2)
        # self._sweep_seq = np.hstack((self._sweep_seq, self._sweep_seq[:-1][::-1]))

        # load calibration curve
        fname = 'temp_curve2.dat'
        cal_curve = np.genfromtxt(fname, delimiter=' ')
        resistances = cal_curve[:, 0]
        temperatures = cal_curve[:, 1]
        self._r_t = interp1d(resistances, temperatures, kind='linear', fill_value='extrapolate')
        k, b = np.polyfit(resistances[-5:], temperatures[-5:],1)
        self.ex_k, self.ex_b = k, b
        self.max_res = resistances[-1]

        self._setpoint = None
        self.max_heater_current = 300e-3

        self._p = 3
        self._i = 4
        self._d = 5

        self._mode_active = (mode == 'active')
        self._pid_controller = PID(self._p, self._i, self._d)

        if self._mode_active:
            self.__tempValues = np.arange(temp_start, temp_range, temp_step)
            self._heater = heater_device


    def _set_heater(self, val):
        if val > self.max_heater_current:
            val = self.max_heater_current
        self._heater.SetOutput(val)

    def __meas_resistance(self):
        sweep_seq = self._sweep_seq
        sense = self._sense
        sweeper = self._sweep
        zero = sense.MeasureNow(1)
        voltages = np.zeros_like(sweep_seq)
        for i, curr in enumerate(sweep_seq):
            sweeper.SetOutput(curr)
            time.sleep(0.8)
            #print('----')
            voltages[i] = sense.MeasureNow(1) - zero
            #print(voltages[i])
            #print('-----')

        try:
            #print(sweep_seq, voltages)
            return abs(np.polyfit(sweep_seq, voltages, 1)[0])
        except np.linalg.LinAlgError:
            return 0
        except TypeError:
            return 0
        
    def _extrapolate(self, temp):
        return self.ex_k * temp + self.ex_b
    
    def GetTemperature(self):
        resistance = self.__meas_resistance()
        temp = self._r_t(resistance) if resistance >= self.max_res else self._extrapolate(resistance)
        if self._mode_active and not (self._setpoint is None):
            self._update_step()

        return temp

    def _update_step(self, temperature):
        resp = self._pid_controller.update(temperature)
        print('Temperature:', temperature, 'responce:', resp, f'({resp*1E-4 * 100 / self.max_heater_current:.1f} %)')
        self._set_heater(resp * 1E-4)


    @property
    def temp_channel(self):
        return 1

    @temp_channel.setter
    def temp_channel(self, chan):
        pass

    @property
    def setpoint(self):
        return self._pid_controller.SetPoint

    @setpoint.setter
    def setpoint(self, new_setpoint):
        self._pid_controller.SetPoint = new_setpoint

    def __iter__(self):
        if not self._mode_active:
            raise ValueError('Temperature sweep is allowed only in activ mode')

        tol_temp = 0.001
        for temp in self._tempValues:

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

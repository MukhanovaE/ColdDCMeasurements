from . import visa_device
import time
import numpy as np


class Keithley6200(visa_device.visa_device):
    def __init__(self, device_num, R=None, what='CURR', max_current=2E-5):
        print('Connecting Keithley 6200 series...')
        if what not in ['VOLT', 'CURR']:
            raise ValueError('Invalid control type.\n Please use "CURR" or "VOLT"')
        else:
            self._volt_mode = (what == 'VOLT')
        self.R = R
        if self._volt_mode and R is None:
            raise ValueError('Please specify a resistance for a voltage sweep mode')

        super().__init__(device_num)
        self.SendString('CLEar')
        self.SendString('CURRent:FILTer ON')
        self.SendString('CURRent:RANGe:AUTO OFF')
        self.SendString('OUTPut:ISHield OLOW')
        self.SendString('OUTPut:LTEarth OFF')

        self.SendString('CURRent:COMPliance 15')
        self.SendString(f'CURRent:RANGe {max_current}')
        self.SendString('OUTPut ON')
        print('Keithley 6200 series init success, device ID:', device_num)

    # value in volts or amperes
    def SetOutput(self, value: float):
        if self._volt_mode:
            value /= self.R  # volts -> amperes
        self.SendString(f'CURRent {value}')

    def GetOutput(self):
        return self.GetFloat('CURRent?')

    def __del__(self):
        print('Switching Keithley 6200 series current off')
        now_curr = self.GetOutput()
        currents = np.linspace(now_curr, 0, 20)
        for curr in currents:
            self.SetOutput(curr)
            time.sleep(0.1)


class DebugKeithley6200:
    def __init__(self, device_num):
        print('Keithley 6200 DEBUG mode, no real current output')
        self._curr = 0

    def SetOutput(self, value: float):
        self._curr = value

    def GetOutput(self):
        return self._curr

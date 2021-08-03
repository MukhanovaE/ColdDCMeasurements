from Drivers import visa_device
from enum import Enum

class Keithley2400WorkMode(Enum):
    MODE_SOURCE = 0
    MODE_VOLTMETER = 1
    MODE_BOTH = 2


class Keithley2400(visa_device.visa_device):
    def __init__(self, device_num, mode: Keithley2400WorkMode, R=None, what='CURR', max_current=2E-5):
        modes_UI = {Keithley2400WorkMode.MODE_SOURCE: "Current source",
                    Keithley2400WorkMode.MODE_VOLTMETER: "Voltmeter",
                    Keithley2400WorkMode.MODE_BOTH: "Both mode"}
        print('Connecting Keithley 2400 series, device id = ', device_num)
        print('Working mode: ', modes_UI[mode])

        if what not in ['VOLT', 'CURR']:
            raise ValueError('Invalid control type.\n Please use "CURR" or "VOLT"')
        else:
            self._volt_mode = (what == 'VOLT')
        self.R = R

        if self._volt_mode:
            func = 'VOLTage'
        else:
            func = 'CURRent'
        self._func_for_cmd = func

        if self._volt_mode and R is None:
            raise ValueError('Please specify a resistance for a voltage sweep mode')

        super().__init__(device_num)
        if mode != Keithley2400WorkMode.MODE_SOURCE:  # voltmeter or both
            self.SendString('SENSe:FUNCtion:OFF:ALL')
            self.SendString('SENSe:FUNCtion VOLTage')
            self.SendString('SENSe:VOLTage:NPLCycles 5')
            self.SendString('SENSe:VOLTage:PROTection 15')  # 15 volts
            self.SendString('FORMat:ELEMents VOLTage')
            self.SendString('SYSTem:AZERo OFF')

        if mode == Keithley2400WorkMode.MODE_BOTH:
            self.SendString('SYSTem:RSENse:ON')  # remote sense (4-wire schene)

        if mode != Keithley2400WorkMode.MODE_VOLTMETER:  # source or both
            self.SendString(f'SOURce:FUNCtion "{func}"')
            self.SendString('SOURce:{func}:RANGe:AUTO OFF')
            self.SendString(f'SOURce:{func}:RANGe {max_current}')
            self.SendString(f'SOURce:{func}:MODE FIXed')  # TODO check!
            self.SendString('OUTPut ON')

        self._mode = mode

        print('Keithley 2400 series connection success')

    def MeasureNow(self, channel=None):
        return self.GetFloat(':READ?')

    # value in volts or amperes
    def SetOutput(self, value: float):
        if self._volt_mode:
            value /= self.R  # volts -> amperes

        func = self._func_for_cmd
        self.SendString(f'SOURce:CURRent:LEVel {value}')

    def GetOutput(self):
        func = self._func_for_cmd
        return self.GetFloat(f'SOURce:{func}:LEVel?')

    def __del__(self):
        self.SetOutput(0)
        self.SendString('OUTPut OFF')

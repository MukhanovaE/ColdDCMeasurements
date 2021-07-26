from . import visa_device


class YokogawaMeasurer(visa_device.visa_device):
    def __init__(self, device_num=4, dev_range='1E+0', what='VOLT', verbose=True):
        self.__verbose = verbose

        # check input values
        if what not in ['VOLT', 'CURR']:
            raise ValueError('Invalid control type.\n Please use "CURR" or "VOLT"')
        else:
            self.__what = what

        self.__range = range

        # Load and configure a device
        if self.__verbose:
            print('Connecting Yokogawa...')

        super().__init__(device_num)

        self.SendString('SYSTem:REMote')
        self.SendString(f"SOUR:FUNC {what}")
        self.SendString(f'SOUR:RANGe {dev_range}')
        self.SendString('OUTPut ON')

        if self.__verbose:
            print('Yokogawa connection success, device ID:', device_num)

    def SetOutput(self, value: float):
        self.SendString(f":SOURce:LEVel {value}")

    def GetOutput(self):
        return self.GetFloat('SOURce:LEVel?')

    def __del__(self):
        self.SetOutput(0)  # turn off output
        self.SendString('OUTPut OFF')

        if self.__verbose:
            print('Yokogawa disconnecting, output was set to 0.')


class DebugYokogawaMeasurer:
    def __init__(self, device_num=4, dev_range='1E+0', what='VOLT', verbose=True):
        print('Yokogawa DEBUG version, no real current output')
        self._curr = 0

    def SetOutput(self, value: float):
        self._curr = value

    def GetOutput(self):
        return self._curr

    def __del__(self):
        print('If it was a real Yokogawa, its output will be reset to 0.')

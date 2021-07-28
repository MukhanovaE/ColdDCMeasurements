from Drivers import visa_device


class Keithley2400(visa_device.visa_device):
    def __init__(self, device_num, R=None, what='CURR', max_current=2E-5):
        print('Connecting Keithley 6200 series...')

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
        self.SendString('SENSe:FUNCtion:OFF:ALL')
        self.SendString('SENSe:FUNCtion VOLTage')
        self.SendString('SENSe:VOLTage:NPLCycles 5')
        self.SendString('SENSe:VOLTage:PROTection 15')  # 15 volts

        self.SendString('SYSTem:AZERo OFF')
        self.SendString('FORMat:ELEMents VOLTage')

        self.SendString(f'SOURce:FUNCtion "{func}"')
        self.SendString('SOURce:{func}:RANGe:AUTO OFF')
        self.SendString(f'SOURce:{func}:RANGe {max_current}')
        self.SendString(f'SOURce:{func}:MODE FIXed')  # TODO check!
        self.SendString('OUTPut ON')

    def MeasureNow(self, channel=None):
        return self.GetFloat(':READ?')

    # value in volts or amperes
    def SetOutput(self, value: float):
        func = self._func_for_cmd
        self.SendString(f'SOURce:{func}:LEVel {value}')
        self.SendString('*OPC?')

    def GetOutput(self):
        return self.GetFloat(f'SOURce:{func}:LEVel?')

    def __del__(self):
        self.SetOutput(0)
        self.SendString('OUTPut OFF')

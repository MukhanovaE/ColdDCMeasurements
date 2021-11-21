from Drivers import visa_device


class Keithley2182A(visa_device.visa_device):
    def __init__(self, device_num):
        print('Connecting Keithley 2182A series, ddevice id = ', device_num)

        super().__init__(device_num)
        self.SendString('SENSe:VOLTage')
        self.SendString('SENSe:CHANnel 1')
        self.SendString('SENSe:VOLTage:NPLCycles 5')
        self.SendString('SYSTem:FAZero ON') #OFF')
        self.SendString('SYSTem:AZERo ON') #OFF')
        self.SendString('SYSTem:LSYNc ON')
        # self.SendString('SENSe:VOLTage:CHANnel1:RANGe:UPPer 0.01')
        self.SendString('SENSe:VOLTage:CHANnel1:RANGe:AUTO ON')
        self.SendString('SENSe:VOLTage:CHANnel1:LPASs OFF')
        # self.SendString('OUTPut:RELative ON')
        self.SendString('INITiate')
        self.SendString('INITiate:CONTinuous OFF')
        self._set_channel(1)

        print('Keithley 2182A series connection success')

    def _set_channel(self, channel):
        self._channel = channel
        self.SendString(f'SENSe:CHANnel {channel}')
        self.SendString('INITiate:CONTinuous OFF')

    # returns voltage in volts
    def MeasureNow(self, channel):
        x = self.GetFloat(':READ?')
        return x
        

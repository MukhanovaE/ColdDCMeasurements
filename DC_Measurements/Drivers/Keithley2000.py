from Drivers import visa_device


class Keithley2000(visa_device.visa_device):
    def __init__(self, device_num):
        print('Connecting Keithley 2000 series, ddevice id = ', device_num)

        super().__init__(device_num)
        self.SendString(':CONFigure:VOLTage:DC')
        self.SendString(':SENSe:FUNCtion:VOLTage:DC')
        self.SendString(':SENSe::VOLTage:DC:NPLCycles 1')
        self.SendString(':SENSe::VOLTage:DC:RANGe:AUTO ON')
        self.SendString(':SYSTem:AZERo OFF')
        self.SendString(':SENSe::VOLTage:DC:AVERage ON')
        print('Keithley 2000 series connection success')

    # returns voltage in volts
    def MeasureNow(self, channel):
        read = self.GetString(':READ?')
        # value can be in different formats
        try:
            return float(read)
        except ValueError:
            try:
                x = float(read.split(',')[0][:-3])
            except ValueError:
                return 0
            return x



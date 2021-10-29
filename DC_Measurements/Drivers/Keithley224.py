from Drivers import visa_device


class Keithley224(visa_device.visa_device):
    def __init__(self, device_num):
        print('Connecting Keithley 224 series, ddevice id = ', device_num)
        super().__init__(device_num)
        self.SendString('I0')  # set zero current
        self.SendString('F1')  # output on

    def SetOutput(self, value: float):
        self.SendString(f'I{value}X')


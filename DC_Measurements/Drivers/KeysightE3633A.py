from Drivers import visa_device


class KeysightE3633A(visa_device.visa_device):
    def __init__(self, device_num):
        super().__init__(device_num)
        
        self.SendString('SOURce:CURRent:PROTection:LEVel 4')
        self.SendString('SOURce:CURRent:PROTection:STATe ON')
        self.SendString('OUTPut:STATe ON')
        
    def SetOutput(self, value: float):
        print('Current is:', value)
        print(f":SOURce:CURRent:LEVel {value}")
        self.SendString(f":SOURce:CURRent:LEVel {value}")
        

    def GetOutput(self):
        return self.GetFloat('SOURce:CURRent:LEVel?')
     
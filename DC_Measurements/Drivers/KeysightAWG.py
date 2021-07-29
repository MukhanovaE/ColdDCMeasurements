from Drivers import visa_device
import time


class KeysightAWG(visa_device.visa_device):

    def __init__(self, device_num, voltageAmplitude):
        print('Initializing Keysight AWG, device ID = ', device_num)
        self.__vmax = voltageAmplitude
        super().__init__(device_num)

    # generate and output a sequence with required parameters
    # length are in seconds
    def GenerateAndSetOutput(self, length_on, length_off, n_repeat=10):
        freq = 1 / (length_on + length_off)
        perc = length_on / (length_on + length_off) * 100

        # set trigger output
        self.SendString('OUTPut1:TRIGger:ROUTe SYNA')

        # set waveform parameters
        '''self.SendString('OUTput1 ON')
        self.SendString(f'SOURce:FREQuency1 {freq}HZ')
        self.SendString(f'SOURce:PERiod {length_on + length_off}S')
        self.SendString(f'SOURce:VOLTage1:LEVel:HIGH {self.__vmax}V')
        self.SendString('SOURce:VOLTage1:LEVel:LOW 0V')
        self.SendString('SOURce:FUNCtion1 SQUare')
        self.SendString(f'SOURce:FUNCtion1:SQUare:DCYCle {perc}PCT')

        # set repeat ("burst")
        self.SendString('BURS1:STATe ON')
        self.SendString(':BURS1:MODE GATed')
        self.SendString(f':BURS1:NCYCles {n_repeat}')
        self.SendString('*TRG')  # send one time, so a burst will be executed only for 1 time'''
        self.SendString('OUTput1 ON')
        self.SendString(f'APPL:SQU {freq}HZ, {self.__vmax}, 0')
        self.SendString(f'SOURce:VOLTage1:LEVel:HIGH {self.__vmax}V')
        self.SendString('SOURce:VOLTage1:LEVel:LOW 0V')

        print('----')
        print('Function:', self.GetString('SOURce:FUNCtion?'))
        print('High level:', self.GetString('SOURce:VOLTage1:LEVel:HIGH?'))
        print('Low level:', self.GetString('SOURce:VOLTage1:LEVel:HIGH?'))
        print('Period', self.GetString('SOURce:PERiod?'))
        print(r'% cycle', self.GetString('SOURce:FUNCtion1:SQUare:DCYCle?'))
        print('----')

        # wait for waveform output to be completed
        self.GetString("*OPC?")

    def __del__(self):
        self.SendString('OUTput1 OFF')
        self.SendString('BURS1:STATe OFF')
        print('Keysight AWG disconnecting, output was set to 0')


# for debugging purposes, no real device
class DebugKeysightAWG:
    def __init__(self, device_num, voltageAmplitude):
        pass

    def GenerateAndSetOutput(self, length_on, length_off, n_repeat=10):
        time.sleep(n_repeat * 0.1)

    def __del__(self):
        print('If it was a real generator, its output will be turned off.')

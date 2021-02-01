import numpy as np
import visa

from . import visa_device

MODE_POWER = 0
MODE_FREQ = 1


class KeysightN51(visa_device.visa_device):

    # Sample usages:
    # k = KeysightN51(device_num=18, sweep='power', freq=1, power_range=np.linspace(-50, 10, 40))
    # k = KeysightN51(device_num=18, sweep='freq', power=-50, freq_range=np.linspace(-50, 10, 40))
    def __init__(self, device_num=18, sweep='power', **kwargs):
        super().__init__(device_num)

        if sweep == 'power':
            self.__freq = kwargs['freq']
            self.SetFrequency(self.__freq)
            self.__powers = kwargs['power_range']
            self.__mode = MODE_POWER
        elif sweep == 'freq':
            self.__power = kwargs['power']
            self.SetPower(self.__power)
            self.__freqs = kwargs['freq_range']
            self.__mode = MODE_FREQ
        else:
            raise ValueError('Invalid device mode, use "freq" or "power".')

    def SetFrequency(self, freq, unit='GHz'):
        self.SendString(f':SOURce:FREQuency:FIXed {freq}{unit}')

    def SetPower(self, power):
        self.SendString(f':SOURce:POWer:LEVel:IMMediate:AMPLitude {power}dBm')

    def __iter__(self):
        self.SendString(':OUTPut:STATe ON')
        if self.__mode == MODE_POWER:
            for pow in self.__powers:
                self.SetPower(pow)
                yield pow
        else:
            for freq in self.__freqs:
                self.SetFrequency(freq)
                yield freq
        self.SendString(':OUTPut:STATe OFF')

    @property
    def FreqRange(self):
        return self.__freqs

    @property
    def PowerRange(self):
        return self.__powers

    @property
    def GenericSweptRange(self):
        return self.__powers if self.__mode == MODE_POWER else self.__freqsfreq

    def OutputOff(self):
        self.SendString(':OUTPut:STATe OFF')

    def __del__(self):
        print('Keysight generator output off.')
        self.OutputOff()


class DebugKeysightN51:

    def __init__(self, device_num=18, sweep='power', **kwargs):
        if sweep == 'power':
            self.__freq = kwargs['freq']
            self.SetFrequency(self.__freq)
            self.__powers = kwargs['power_range']
            self.__mode = MODE_POWER
            print('Keysight DEBUG power sweep mode')
        elif sweep == 'freq':
            self.__power = kwargs['power']
            self.SetPower(self.__power)
            self.__freqs = kwargs['freq_range']
            self.__mode = MODE_FREQ
            print('Keysight DEBUG frequency sweep mode')
        else:
            raise ValueError('Invalid device mode, use "freq" or "power".')

    def SetFrequency(self, freq, unit='GHz'):
        print('Debug, frequency=', freq)

    def SetPower(self, power):
        print('Debug, power=', power)

    def __iter__(self):
        if self.__mode == MODE_POWER:
            for pow in self.__powers:
                self.SetPower(pow)
                yield pow
        else:
            for freq in self.__freqs:
                self.SetFrequency(freq)
                yield freq

    @property
    def FreqRange(self):
        return self.__freqs

    @property
    def PowerRange(self):
        return self.__powers

    @property
    def GenericSweptRange(self):
        return self.__powers if self.__mode == MODE_POWER else self.__freqs

    def OutputOff(self):
        pass

    def __del__(self):
        print('If it was a real Keysight generator, its output will be turned off.')


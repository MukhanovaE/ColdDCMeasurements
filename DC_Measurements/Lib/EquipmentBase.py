from Drivers.Yokogawa import *
from Drivers.Leonardo import *
from Drivers.Keithley2182A import *
from Drivers.Keithley6200 import *
from Drivers.Keithley2400 import *
from Drivers.LakeShore370 import *
from Drivers.LakeShore335 import *

from Lib.lm_utils import *


class EquipmentBase:
    def __init__(self, source_id, source_model, sense_id, sense_model, R, max_voltage, sense_samples=500,
                 temp_id=None, temp_model=None, temp_mode='passive', temp_start=None, temp_end=None, temp_step=None):
        max_range_value = (max_voltage / R)
        error_message = 'This device type is not supported yet!'
        print('Excitation device is: ', end='')
        if source_model == EXCITATION_YOKOGAWA:
            self._source = YokogawaGS200(device_num=source_id, what='VOLT')
            print('Yokogawa, ID =', source_id)
        elif source_model == EXCITATION_KEITHLEY_6200:
            self._source = Keithley6200(device_num=source_id, what='CURR', R=R, max_current=max_range_value)
            print('Keithley 6200, ID =', source_id)
        elif source_model == EXCITATION_KEITHLEY_2400:
            self._source = Keithley2400(device_num=source_id, R=R, what='CURR', max_current=max_range_value)
            print('Keithley 2400, ID =', source_id)
        else:
            raise ValueError(error_message)

        print('Readout device is: ', end='')
        if sense_model == READOUT_LEONARDO:
            self._sense = Leonardo(n_samples=sense_samples)
            print('Leonardo')
        elif sense_model == READOUT_KEITHLEY_2182A:
            self._sense = Keithley2182A(device_num=sense_id)
            print('Keithley 2182A, ID =', source_id)
        elif sense_model == READOUT_KEITHLEY_2400 or source_model == EXCITATION_KEITHLEY_2400:
            self._sense = self._source  # one device performs two functions
            print('Keithley 2400, ID =', source_id)
        else:
            raise ValueError(error_message)

        if temp_id is None:
            return
        print('Temperature control device is: ', end='')
        if temp_model == LAKESHORE_MODEL_370:
            self._ls = LakeShore370(device_num=temp_id, control_channel=6, mode=temp_mode,
                                    temp_0=temp_start, max_temp=temp_end, temp_step=temp_step)
        elif temp_model == LAKESHORE_MODEL_335:
            self._ls = LakeShore335(device_num=temp_id, mode=temp_mode, control_channel='A', heater_channel=1,
                                    temp_0=temp_start, max_temp=temp_end, temp_step=temp_step)

    def MeasureNow(self, channel):
        return self._sense.MeasureNow(channel)

    def SetOutput(self, value: float):
        self._source.SetOutput(value)

    def GetOutput(self):
        return self._source.GetOutput()

    @property
    def source(self):
        return self._source

    @property
    def sense(self):
        return self._sense

    @property
    def lakeshore(self):
        return self._ls


from Drivers.Yokogawa import *
from Drivers.Leonardo import *
from Drivers.Keithley2182A import *
from Drivers.Keithley6200 import *
from Drivers.Keithley2400 import *
from Drivers.LakeShore370 import *
from Drivers.LakeShore335 import *

from Lib.lm_utils import *


class EquipmentBase:
    def __init__(self, shell: ScriptShell, temp_mode=None, temp_start=None, temp_end=None, temp_step=None):
        max_range_value = (shell.rangeA / shell.R)
        error_message = 'This device type is not supported yet!'

        print('Excitation device is: ')
        if shell.excitation_device_type == EXCITATION_YOKOGAWA:
            print('Yokogawa, ID =', shell.excitation_device_id)
            self._source = DebugYokogawaGS200(device_num=shell.excitation_device_id, what='VOLT')
        elif shell.excitation_device_type == EXCITATION_KEITHLEY_6200:
            print('Keithley 6200, ID =', shell.excitation_device_id)
            self._source = Keithley6200(device_num=shell.excitation_device_id, what='VOLT', R=shell.R,
                                        max_current=max_range_value)
        elif shell.excitation_device_type == EXCITATION_KEITHLEY_2400:
            print('Keithley 2400, ID =', shell.excitation_device_id)
            if shell.excitation_device_type == shell.readout_device_type:
                mode = Keithley2400WorkMode.MODE_BOTH
            else:
                mode = Keithley2400WorkMode.MODE_SOURCE
            self._source = Keithley2400(device_num=shell.excitation_device_id, R=shell.R,
                                        what='VOLT', max_current=max_range_value, mode=mode)
            
        else:
            raise ValueError(error_message)

        print('\nReadout device is: ')
        if shell.readout_device_type == READOUT_LEONARDO:
            print('Leonardo')
            self._sense = DebugLeonardo(n_samples=shell.num_samples)
        elif shell.readout_device_type == READOUT_KEITHLEY_2182A:
            print('Keithley 2182A, ID =', shell.read_device_id)
            self._sense = Keithley2182A(device_num=shell.read_device_id)
        elif shell.readout_device_type == READOUT_KEITHLEY_2400:
            print('Keithley 2400, ID =', shell.read_device_id)
            if shell.readout_device_type == shell.excitation_device_type:
                self._sense = self._source  # one device performs two functions
            else:
                self._sense = Keithley2400(device_num=shell.read_device_id, R=shell.R, what='VOLT',
                                           max_current=max_range_value, mode=Keithley2400WorkMode.MODE_VOLTMETER)
        else:
            raise ValueError(error_message)

        if temp_mode is None:
            return
        print('Temperature control device is: ', end='')
        if shell.lakeshore_model == LAKESHORE_MODEL_370:
            self._ls = DebugLakeShore370(device_num=shell.lakeshore, max_temp=temp_end, mode=temp_mode)
        elif shell.lakeshore_model == LAKESHORE_MODEL_335:
            self._ls = LakeShore335(device_num=shell.lakeshore, mode=temp_mode, control_channel='A', heater_channel=1,
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


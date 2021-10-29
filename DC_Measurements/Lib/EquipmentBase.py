from Drivers.Yokogawa import *
from Drivers.Leonardo import *
from Drivers.Keithley2182A import *
from Drivers.Keithley6200 import *
from Drivers.Keithley2400 import *
from Drivers.Keithley224 import *
from Drivers.Keithley2000 import *
from Drivers.VirtualLakeShore import *

from Lib.lm_utils import *


class EquipmentBase:
    def __init__(self, shell: ScriptShell, temp_mode=None, temp_start=None, temp_end=None, temp_step=None):
        max_range_value = (shell.rangeA / shell.R)
        print('Current range:', max_range_value)

        print('Excitation device is: Keithley 6200, ID =', shell.excitation_device_id)
        self._source = Keithley6200(device_num=shell.excitation_device_id, what='VOLT', R=shell.R,
                                    max_current=max_range_value)
        
        print('Readout device is: Keithley 2182A, ID =', shell.read_device_id)
        self._sense = Keithley2182A(device_num=shell.read_device_id)
        
        if temp_mode is None:
            return
        ls_sense = Keithley2000(device_num=shell.temp_read_id)
        ls_source = Keithley224(device_num=shell.temp_exc_id)

        if temp_mode == 'active':
            ls_heat_source = Keithley2400(device_num=shell.temp_heat_id, mode=Keithley2400WorkMode.MODE_SOURCE,
                                          R=None, max_current=1)
            self._ls = VirtualLakeShore(sense_device=ls_sense, sweep_device=ls_source, heater_device=ls_heat_source,
                                        mode=temp_mode, temp_start=temp_start, temp_range=temp_end, temp_step=temp_step)
        else:
            self._ls = VirtualLakeShore(sense_device=ls_sense, sweep_device=ls_source, heater_device=None,
                                        mode=temp_mode)

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


from Drivers.LakeShoreBase import *
import math

class LakeShore335(LakeShoreBase):
    # Class constructor
    # Control channel: A or B
    # Heater channel: 1 or 2
    def __init__(self, device_num, control_channel, heater_channel, temp_0=None, max_temp=1.7, verbose=True, mode="active",
                 temp_step=0.1):
        input_letters = {'A', 'B'}
        if control_channel not in input_letters:
            raise ValueError('Please set a valid input channel: A or B')
        self._temp_channel = control_channel
        self._heater_channel = heater_channel

        super().__init__(device_num, control_channel, temp_0, max_temp, verbose, mode, temp_step)

        self._temp_start = temp_0 if temp_0 is not None else self.GetTemperature()
        self._temp_max = max_temp
        self._power_range = np.arange(10, 20, 0.5)
        self._tempValues = self._power_range
        self.SendString(f"OUTMODE {self._heater_channel},3,1,1")

    # Remember parameters of one of two inputs: A or B
    def _get_intype(self):
        chan = self._temp_channel
        read_data = self.GetString(f'INTYPE? {chan}')
        sensor_type, autorange, rng, compensation, units = [int(i) for i in read_data.split(',')]
        self._intype_input = chan
        self._intype_sensor_type = sensor_type
        self._intype_autorange = autorange
        self._intype_range = rng
        self._intype_compensation = compensation
        self._intype_units = units

    # device parameter setters
    def _set_pid(self, pid):
        chan = self._heater_channel
        self.device.write(f'PID {chan},{pid}')
        super()._set_pid(pid)

    def _set_heater_range(self, htrrng):
        chan = self._heater_channel
        self.device.write(f'RANGE {chan},{htrrng}')
        super()._set_heater_range(htrrng)

    def _set_excitation(self, excitation):
        chan = self._temp_channel
        self.device.write(f'INTYPE {chan},{self._intype_sensor_type},{self._intype_autorange},{excitation},{self._intype_compensation},{self._intype_units}')
        super()._set_excitation(excitation)

    def _set_channel(self, chan):
        super()._set_channel(chan)

    def _init_modes(self):
        self.SendString(f"OUTMODE {self._heater_channel},3,1,1")
        self.SendString(f"RANGE {self._heater_channel},2")

    def _set_power(self, power_perc):
        if power_perc > 100:
            raise ValueError('Invalid percentage, please set from 0 to 100')

        command = f"MOUT {self._heater_channel},{power_perc}"
        print(command)
        self.SendString(command)

    # Functions for updating LakeShore params depending on temperature
    # Updates thermometer excitation in dependence of temperature
    @staticmethod
    def _get_excitation_for_temperature(temp):
        # TODO: measure in different temperature ranges and find where '2' must be
        n_setting = 1
        return n_setting

    @staticmethod
    def _get_heater_range_from_temperature(temp):
        return 1

    def _get_pid_from_temperature(self, temp):
        return "5,2,0"  # TODO measure in different temperature ranges and set another values there

    def _remember_old_params(self):
        self._get_intype()
        self.__old_pid = self.GetString(f'PID? {self._heater_channel}')
        self._pid = self.__old_pid

    def _restore_old_params(self):
        self._set_excitation(self._intype_range)
        self._set_pid(self.__old_pid)

    # Prints current controller parameters
    def PrintParams(self):
        pass  # TODO: implement (if will be needed)

    # Measures a current temperature
    def _meas_temperature(self):
        return self.GetFloat(f'KRDG? {self._temp_channel}')

    # Changes a setpoint
    def _set_setpoint(self, setp):
        chan = self._heater_channel
        self.SendString(f'SETP {setp}')

    def _set_control_mode(self, mode: PIDLoopType):
        # in a device: 1 - closed loop, 3 - open loop, 4 = off
        class_to_device = {PIDLoopType.open_loop: 3,
                           PIDLoopType.close_loop: 1,
                           PIDLoopType.off: 4}

        self.SendString(f'CMODE {class_to_device[mode]}')

    # Temperature control without PID
    def __iter__(self):
        if not self._active:
            raise LakeShoreException()

        # tol_temp = 0.001
        power_step = 1
        for power in self._power_range:
            self._set_power(power)

            # Update temperature measurement parameters depending on T
            # self._update_params(temp)

            actual_temp = self.GetTemperature()
            print(f'Heating, now temperature - {actual_temp} K, power - {power}%')

            '''count_ok = 0
            c = 0
            prev_temp = 999999999
            while count_ok < 3:
                time.sleep(3)
                actual_temp = self.GetTemperature()
                print('Now:', actual_temp, 'K', 'establishing...')
                if abs(actual_temp - prev_temp) <= tol_temp:
                    count_ok += 1
                    print('Stable', count_ok, 'times')
                else:
                    count_ok = 0
                prev_temp = actual_temp
                c += 1
                if c > 50:
                    print('Warning! Cannot set a correct temperature')
                    break
            '''
           
            print('Temperature was set, waiting 1 min...')
            time.sleep(60)
            actual_temp = self.GetTemperature()
            print('Ready, measuring')
            yield actual_temp  # resulting actual temperature

            if actual_temp > self._temp_max:
                print('Experiment end')
                break

        print('Turning heater off...')
        self.SendString(f"RANGE {self._heater_channel},0")

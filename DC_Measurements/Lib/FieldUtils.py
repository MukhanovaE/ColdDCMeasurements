import numpy as np
import time


'''# Current to magnetic field
def I_to_B(I):  # I in mA
    k_magnet = 100  # Gauss/A
    return (I / 1000) * k_magnet  # milliamperes to amperes


# Magnetic field to current
def B_to_I(B):  # B in G, returns I in mA
    k_magnet = 100  # Gauss/A
    return (B / k_magnet) * 1000  # milliamperes to amperes
    
# Set a magnetic field on current source
# current is in mA
def SetField(yok, current):
    yok.SetOutput(current * 1E-3)
    
    
# Slowly changes a current in given range, but doesn't perform any measurements
def SlowlyChange(yok, pw_output, line, message):
    step_delay = 0.5
    for i, curr in enumerate(line):
        yok.SetOutput(curr / 1000)
        time.sleep(step_delay)

        mess = f'Field is: {I_to_B(curr)}, {message}'
        print(mess)
        for nax, ax in enumerate(pw_output.Axes):
            ax.set_title(mess)
            pw_output.canvases[nax].draw()



# Slowly changes magnetic field from current value to zero
def ReturnAtExit(yok_B, pw_output):
    now_curr = yok_B.GetOutput()
    print('Returning magnetic field to zero...')
    SlowlyChange(yok_B, pw_output, np.linspace(now_curr, 0, 15), 'returning to zero...')
    print('Magnetic field was returned to zero.')


# check for current magnetic field at program exit
# If field is on, slowly return it to zero
def CheckAtExit(yok_B, pw_output):
    if yok_B.GetOutput() != 0:
        print('Program closed before measurement end, returning magnetic field to zero...')
        ReturnAtExit(yok_B, pw_output)
        print('Magnetic field was returned to zero.')

'''
class FieldSweeper:
    def __init__(self, field_range, plot_window=None):
        self.field_range = field_range
        self.plot_window = plot_window

    # Methods to be overridden in child classes

    # sets a required field (in G)
    def _set_one(self, field):
        pass

    # prepairs measurements (sets up equipment, sets field to initial value)
    def _prepair(self):
        pass

    # finishes measurement (turns off field, etc)
    def _finalize(self):
        pass

    # finishes measurement in case of emergency stop
    def error_cleanup(self):
        pass

    def __iter__(self):
        self._prepair()

        for f in self.field_range:
            self._set_one(f)
            yield f

        self._finalize()


class YokogawaFieldSweeper(FieldSweeper):
    @staticmethod
    def B_to_I(B):  # B in G, returns I in A
        k_magnet = 100  # Gauss/A
        return B / k_magnet
    
    @staticmethod
    def I_to_B(I):  # I in mA
        k_magnet = 100  # Gauss/A
        return (I / 1000) * k_magnet  # milliamperes to amperes

    # slowly change a magnetic field in the specified range
    # line: required fields, in G
    # message: a message for user which shown during field change process
    def _SlowlyChange(self, line, message):
        step_delay = 0.5
        pw_output = self.plot_window

        for i, field in enumerate(line):
            self._set_one(field)
            time.sleep(step_delay)

            mess = f'Field is: {field:.2f} G, {message}'
            print(mess)
            for nax, ax in enumerate(pw_output.Axes):
                ax.set_title(mess)
                pw_output.canvases[nax].draw()
                
    def _MeasureCurrent(self):
        return self.I_to_B(self.yok.GetOutput())

    def __init__(self, field_range, device, plot_window=None):
        super().__init__(field_range, plot_window)
        self.yok = device

    def _set_one(self, field):
        curr = self.B_to_I(field)
        self.yok.SetOutput(curr)
        self.__field = field

    def _prepair(self):
        # slowly change a magnetic field from zero to required value
        first_value = self.field_range[0]
        now_value = self._MeasureCurrent()
        self._SlowlyChange(np.linspace(now_value, first_value, 15), 'prepairing...')
        print('Field was set')

    def _finalize(self):
        # slowly return a magnetic field from current value to zero
        print('Returning magnetic field to zero...')
        now_field = self._MeasureCurrent()
        self._SlowlyChange(np.linspace(now_field, 0, 15), 'returning to zero...')
        print('Magnetic field was returned to zero.')

    def error_cleanup(self):
        print('Measurement aborted before end, magnetic field will be slowly returned to zero')
        self._finalize()
        
        
class AmericanMagneticsFieldSweeper(FieldSweeper):
    def __init__(self, field_range, device, plot_window=None):
        super().__init__(field_range, plot_window)
        self.ami = device
        device.update_fields(field_range)

    # prepair() is not implemented, because it will automatically be a slowly change
    # at an each field set

    def _set_one(self, field):
        self.ami.ramp_to_field(field)
        return field # self.ami.get_actual_field()

    def _finalize(self):
        pass
        # self.ami.ramp_to_zero()
        # self.ami.pswitch_heater_off()

    def error_cleanup(self):
        super().error_cleanup()
        self._finalize()


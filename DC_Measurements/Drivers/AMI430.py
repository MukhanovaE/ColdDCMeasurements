from . import visa_device
import numpy as np
import time

# device ramping states
RAMPING = 1
HOLDING = 2
ZEROING = 6
QUENCH = 7


class QuenchException(Exception):
    pass


class AMI430(visa_device.visa_device):
    max_field = 80e+3  # 80 kG max

    # B in G, return I in A
    def B_to_I(self, B):
        return B / self.__k_magnet

    # I in A, return B in G
    def I_to_B(self, I):
        return I * self.__k_magnet

    def __init__(self, address, field_range, verbose=True):
        super().__init__(address)
        self.__field_range = field_range
        self.verbose = verbose

        if verbose:
            print('Connecting to AMI430 magnet controller...')

        # check field limits
        if np.any(np.abs(field_range) > AMI430.max_field):
            raise ValueError(f'One of the swept values is bigger than the maximum range of {AMI430.max_field}')

        # get coil constant (in Gauss/A)
        k_magnet = 1.06800 #kG/A #self.GetFloat("COILconst?")  # kG/A or T/A
        units_in_kG = True #not bool(self.GetFloat("FIELD:UNITS?"))  # device returns 1 for Tesla, 0 for kG
        print('Field units from settings:', 'KG' if units_in_kG else 'T')
        self.__units_in_kg = units_in_kG
        self.__k_magnet = k_magnet * 1e+3 if units_in_kG else k_magnet * 1e+4  # self.__k_magnet is always in Gauss/A
        print('Coil constant is:', self.__k_magnet, 'Gauss / A')

        # set limits according to field
        #max_field = np.max(np.abs(field_range))
        #max_curr = self.B_to_I(max_field)
        #self.SendString(f"CONFigure:CURRent:LIMit {max_curr}")
        #print('Current limit is set to:', max_curr, 'Amperes, this is a field of', max_field, 'Gausses')

        # set another parameters
        self.SendString("CONFigure:QUench:DETect 3")
        print('Quench detection configured')

        print('Turning on Persistent switch heater, current is 20 mA')
        self.SendString("CONFigure:PSwitch:CURRent 20")
        self.SendString("PSwitch 1")
        print('Waiting 40 sec to complete heating process...')
        time.sleep(40)

        # set ramp rate (TODO: check if it works)
        '''self.SendString("CONFigure:RAMP:RATE:SEGments 3")
        self.SendString("CONFigure:RAMP:RATE:UNITS 0")  # 0 - seconds
        curr_50_kG = self.B_to_I(50e+3)
        curr_80_kG = self.B_to_I(80e+3)
        self.SendString(f"CONFigure: RAMP:RATE: CURRent 1, 0.054, {curr_50_kG}")  # 0.054 Amp/sec
        self.SendString(f"CONFigure: RAMP:RATE: CURRent 2, 0.027, {curr_80_kG}")  # 0.027 Amp/sec
        print('Ramp rates for segments are configured')'''

        self.__now_field = 0

        if verbose:
            print('AMI430 magnet controller commected successfully')

    # ramp to defined field, in Gausses
    def ramp_to_field(self, field):
        print('Ramping to', field, 'G')
        if self.__units_in_kg:
            self.SendString(f"CONFigure:FIELD:TARGet {field*1e-3}")  # G->kG
        else:
            self.SendString(f"CONFigure:FIELD:TARGet {field*1e-4}")  # G->T
        self.SendString("RAMP")

        '''print(f'Target field is: {field}:.4f G, ramping...')
        res = RAMPING
        while res == RAMPING:
            res = self.GetFloat("STATE?")
            if res == QUENCH:
                print('!!!WARNING!!! A quench was detected!')
                print('Measurement will be stopped and magnetic field will be returned to zero')
                print('Please IMMEDIATELY open required valves on your cryostat to avoid high He mixture pressure!')
                self.ramp_to_zero()
                raise QuenchException("Aborting measurements due to a quench")
            time.sleep(1)'''

        delta_field = abs(self.__field_range[1] - self.__field_range[0])
        ramp_rate = 0.027  #A/sec
        ramp_time = self.B_to_I(delta_field) / ramp_rate  # Amperes / (Amperes/sec) = sec
        print('Waiting', ramp_time, 'sec...')
        time.sleep(ramp_time + 5)

        self.__now_field = field
        print('Ramp success')

    # ramp to zero
    def ramp_to_zero(self):
        self.SendString("ZERO")
        print('Returning a magnetic field to zero...')

        '''res = ZEROING
        while res == ZEROING:
            res = self.GetFloat("STATE?")
            time.sleep(1)'''
        delta_field = abs(self.__now_field)
        ramp_rate = 0.027  #A/sec
        ramp_time = self.B_to_I(delta_field) / ramp_rate  # Amperes / (Amperes/sec) = sec
        print('Waiting', ramp_time, 'sec...')
        time.sleep(ramp_time + 5)

        print('A magnetic field was returned to zero')

    # Get actual field, in Gausses
    def get_actual_field(self):
        curr_actual = self.GetFloat("CURRent:MAGnet?")
        return self.I_to_B(curr_actual)

    # sweep all preset fields (a measurement)
    def __iter__(self):
        for field_now in self.__field_range:
            print('------------------------------')
            self.ramp_to_field(field_now)
            field_actual = self.get_actual_field()

            print('Actual field is:', field_actual, 'G')
            print('------------------------------')

    def pswitch_heater_off(self):
        print('Turning persistent switch off...')
        self.SendString("CONFigure:PSwitch:CURRent 0")
        self.SendString("PSwitch 0")
        print('Waiting 40 sec to complete cooling process')
        time.sleep(40)
        
    def update_fields(self, new_fields):
        self.__field_range = new_fields


# For debgging purposes, no actual access to a device
class DebugAMI430:
    max_field = 80e+3  # 80 kG max

    # B in G, return in A
    def B_to_I(self, B):
        return B / self.__k_magnet

    # I in A, return in G
    def I_to_B(self, I):
        return I * self.__k_magnet

    def __init__(self, address, field_range, verbose=True):
        self.__field_range = field_range
        self.verbose = verbose

        if verbose:
            print('AMI430 magnet controller DEBUG MODE')

        # check field limits
        if np.any(np.abs(field_range) > AMI430.max_field):
            raise ValueError(f'One of the swept values is bigger than the maximum range of {AMI430.max_field}')

        # get coil constant (in Gauss/A)
        k_magnet = 1
        units_in_kG = 1
        self.__k_magnet = k_magnet * 1e+3 if units_in_kG else k_magnet * 1e+5
        print('Coil constant is:', self.__k_magnet, 'Gauss / A')

        # set limits according to field
        max_field = np.max(np.abs(field_range))
        max_curr = self.B_to_I(max_field)

        curr_55_G = self.B_to_I(55)
        curr_80_G = self.B_to_I(80)

        if verbose:
            print('AMI430 magnet controller commected successfully')

    # ramp to defined field, in Gausses
    def ramp_to_field(self, field):

        print(f'Target field is: {field} G, ramping...')
        res = RAMPING
        print('Ramp success')

    # ramp to zero
    def ramp_to_zero(self):
        print('Returning a magnetic field to zero...')

        print('A magnetic field was returned to zero')

    # Get actual field
    def get_actual_field(self):

        curr_actual = 10
        return self.I_to_B(curr_actual)

    # sweep all preset fields (a measurement)
    def __iter__(self):
        for field_now in self.__field_range:
            print('------------------------------')
            self.ramp_to_field(field_now)
            field_actual = self.get_actual_field()

            print('Field is:', field_actual, 'G')
            print('------------------------------')

    def pswitch_heater_off(self):
        print('Turning persistent switch off...')

    def update_fields(self, new_fields):
        self.__field_range = new_fields


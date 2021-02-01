import numpy as np
import time


# Current to magnetic field
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

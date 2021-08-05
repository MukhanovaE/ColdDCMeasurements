import numpy as np
import threading

from Lib.lm_utils import *
from Lib.FieldUtils import YokogawaFieldSweeper
from Lib.EquipmentBase import EquipmentBase
from Drivers.KeysightN51 import *
from Drivers.Keithley2651 import *

from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import LinearSegmentedColormap

MODE_UHF_LENGTH = 0
MODE_UHF_POWER = 1


def MeasurementProc():
    print('Setting up a magnetic field...')
    for field_now in field_sweep:
        print('Field =', field_now)
    print('Field was set')

    def thread_proc():
        global Field_controller, pw, f_exit, currValues, voltValues, fieldValues, tempsMomental, \
            curr_curr, f_saved, R_now

        # Slowly change: 0 -> min. field
        # FieldUtils.SlowlyChange(Yokogawa_B, pw, np.linspace(0, -rangeA_B, 15), 'prepairing...')

        print('Measurement begin')

        for i, now_value in enumerate(uhf_sweep_values):

            if len(tempsMomental) != 0:
                Log.AddParametersEntry('B', curr_B, 'G', temp=tempsMomental[-1])

            # Mark measurement begin
            # UpdateRealtimeThermometer()
            # pw.MarkPointOnLine(tabTemp, times[-1], tempsMomental[-1], 'go', markersize=4)
            this_field_V = []  # for I-V 2D plot
            this_field_A = []

            this_RIValues = [0]  # for resistance measurement
            this_RUValues = [0]

            pw.SetHeader(tabIV, 'R will be measured later...')

            def PerformStep(yok, currValues, fieldValues, voltValues,
                            volt, this_field_V, this_field_A, this_B, this_RIValues, this_RUValues):
                global R_now
                # measure I-U curve
                yok.SetOutput(volt)
                time.sleep(step_delay)
                curr_curr = (volt / R) / k_A
                V_meas = iv_sweeper.MeasureNow(6) / gain

                result = V_meas / k_V_meas
                currValues.append(curr_curr)
                fieldValues.append(this_B)
                voltValues.append(V_meas / k_V_meas)
                this_field_V.append(V_meas / k_V_meas)
                this_field_A.append(curr_curr)

                pw.MouseInit(tabIVBR3D)
                pw.MouseInit(tabIVBC3D)
                pw.MouseInit(tabIRBR3D)
                pw.MouseInit(tabIRBC3D)

                # Update I-U 2D plot
                if pw.CurrentTab == tabIV:
                    pw.updateLine2D(tabIV, this_field_A, this_field_V)

                # measure resistance on 2D plot
                if volt > upper_R_bound:
                    this_RIValues.append(curr_curr)
                    this_RUValues.append(V_meas / k_V_meas)

                    R_now = UpdateResistance(pw.Axes[tabIV], np.array(this_RIValues) * k_A,
                                             np.array(this_RUValues) * k_V_meas)
                if f_exit.is_set():
                    exit(0)

                return result

            # 1/3: 0 - max curr, Ic+
            for j, volt in enumerate(upper_line_1):
                res = PerformStep(iv_sweeper, currValues, fieldValues, voltValues,
                                  volt, this_field_V, this_field_A, curr_B, this_RIValues, this_RUValues)
                data_buff_C[j + N_points // 2, i] = res

            # 2/3: max curr -> min curr, Ir+, Ic-
            for j, volt in enumerate(down_line_1):
                res = PerformStep(iv_sweeper, currValues, fieldValues, voltValues,
                                  volt, this_field_V, this_field_A, curr_B, this_RIValues, this_RUValues)
                if j <= (len(down_line_1) // 2):
                    data_buff_R[N_points - j - 1, i] = res
                if j >= (len(down_line_1) // 2):
                    data_buff_C[N_points - j - 1, i] = res

            # 3/3: max curr -> min curr, Ir-
            for j, volt in enumerate(upper_line_2):
                res = PerformStep(iv_sweeper, currValues, fieldValues, voltValues,
                                  volt, this_field_V, this_field_A, curr_B, this_RIValues, this_RUValues)
                data_buff_R[j, i] = res

            resistanceValues.append(R_now)

            # Update 3D plot - every magnetic field value
            pw.update3DPlot(tabIVBC3D, fieldValues_axis[:i + 1], currValues_axis, data_buff_C[:, :i + 1],
                            fieldValues_axis, plt.cm.brg)
            #
            pw.update3DPlot(tabIVBR3D, fieldValues_axis[:i + 1], currValues_axis, data_buff_R[:, :i + 1],
                            fieldValues_axis, plt.cm.brg)

            # update pcolormesh (tab 1, 2)
            pw.updateColormesh(tabIVBCMesh, data_buff_C, fieldValues_axis, currValues_axis, 9)
            pw.updateColormesh(tabIVBRMesh, data_buff_R, fieldValues_axis, currValues_axis, 9)

            # calculate R values (as dV/dI)
            R_values_C = np.gradient(np.array(data_buff_C[:, i]) * k_V_meas)  # V in volts, to make R in ohms
            R_buff_C[:, i] = R_values_C
            #
            R_values_R = np.gradient(np.array(data_buff_R[:, i]) * k_V_meas)  # V in volts, to make R in ohms
            R_buff_R[:, i] = R_values_R

            # update R color mesh with these values
            pw.updateColormesh(tabIRBCMesh, R_buff_C, fieldValues_axis, currValues_axis, 9)
            pw.updateColormesh(tabIRBRMesh, R_buff_R, fieldValues_axis, currValues_axis, 9)

            # update R 3D plot
            pw.update3DPlot(tabIRBC3D, fieldValues_axis[:i + 1], currValues_axis, R_buff_C[:, :i + 1],
                            fieldValues_axis, R_3D_colormap)
            pw.update3DPlot(tabIRBR3D, fieldValues_axis[:i + 1], currValues_axis, R_buff_R[:, :i + 1],
                            fieldValues_axis, R_3D_colormap)

            crit_curs[:, i] = FindCriticalCurrent(this_field_A, this_field_V, threshold=1.5)

            # update R(B) plot
            pw.updateLine2D(tabResistance, fieldValues_axis[:len(resistanceValues)], resistanceValues)

            # plot them
            xdata = fields[:i + 1]
            pw.updateLines2D(tabICT, [xdata, xdata], [crit_curs[0, :i + 1], crit_curs[1, :i + 1]])

            # Mark measurement end
            # pw.MarkPointOnLine(tabTemp, times[-1], tempsMomental[-1], 'ro', markersize=4)

        print('\nMeasurement was successfully performed.')
        DataSave()


k_A, k_V_meas, k_R, R, rangeA, stepA, gain, step_delay, num_samples, I_units, V_units, f_save, yok_read, yok_write, \
    ls, ls_model, read_device_type, exc_device_type, read_device_id, user_params = ParseCommandLine()
Log = Logger(R, k_R, 'B')
Log.AddGenericEntry(
    f'CurrentRange={(rangeA / R) / k_A} {core_units[k_A]}A; CurrentStep={(stepA / R) / k_A} {core_units[k_A]}A; '
    f'Gain={gain}; IVPointDelay={step_delay} sec; LeonardoPoints={num_samples}')

iv_sweeper = EquipmentBase(source_id=yok_read, source_model=exc_device_type, sense_id=read_device_id,
                           sense_model=read_device_type, R=R, max_voltage=rangeA, sense_samples=num_samples)


field0, uhf_fixed_param, uhf_sweep_start, uhf_sweep_end, uhf_sweep_step, mode =\
    [float(i) for i in user_params.split(';')]
mode = int(mode)

uhf_sweep_values = np.arange(uhf_sweep_start, uhf_sweep_end, uhf_sweep_step)
field_setpoint = np.linspace(0, field0, 10)

n_points = 2*int(rangeA // stepA) - 1
upper_line_1 = np.arange(0, rangeA, stepA)  # np.linspace(0, rangeA, n_points // 2)
down_line_1 = np.arange(rangeA, -rangeA, -stepA)   # np.linspace(rangeA, -rangeA, n_points)
upper_line_2 = np.arange(-rangeA, 0, stepA)  # np.linspace(-rangeA, 0, n_points // 2)
voltValues0 = np.hstack((upper_line_1,
                         down_line_1,
                         upper_line_2))

N_points = len(down_line_1)
N_swept = len(uhf_sweep_values)

data_buff_C = np.zeros((N_points, N_swept))
data_buff_R = np.zeros((N_points, N_swept))
R_buff_C = np.zeros((N_points, N_swept))
R_buff_R = np.zeros((N_points, N_swept))

currValues_axis = ((-down_line_1 / R) / k_A)

field_src = Keithley2651(device_num=yok_write)
field_sweep = YokogawaFieldSweeper(device=field_src, field_range=field_setpoint)
uhf_generator = KeysightN51(device_num='TCPIP0::10.20.61.199::inst0::INSTR', sweep='none')

pw = plotWindow(title='UHF demagnetizing', color_buttons=True)
R_3D_colormap = LinearSegmentedColormap.from_list("R_3D", [(0, 0, 1), (1, 1, 0), (1, 0, 0)])
x_axis_caption = 'Length, s' if mode == MODE_UHF_LENGTH else 'Power, dBm'
x_axis_short = 'Length' if mode == MODE_UHF_LENGTH else 'Power'

# 0) Colormesh I-V-T plot preparation, crit. curr
tabIVBCMesh = pw.addColormesh(f'I-U-{x_axis_short} (Color mesh) (crit.)', x_axis_caption, fr"$I, {core_units[k_A]}A$",
                              uhf_sweep_values, currValues_axis, data_buff_C, plt.get_cmap('brg'))

# 1) Colormesh I-V-T plot preparation, ret. curr
tabIVBRMesh = pw.addColormesh(f'I-U-{x_axis_short} (Color mesh) (retr.)', x_axis_caption, fr"$I, {core_units[k_A]}A$",
                              uhf_sweep_values, currValues_axis, data_buff_R, plt.get_cmap('brg'))

# 2) I-V 2D plot preparation, crit. curr
tabIV = pw.addLine2D('I-U (simple 2D)', fr'$I, {core_units[k_A]}A$', fr"$U, {core_units[k_V_meas]}V$")

# 3) I-V-B 3D plot, crit. curr
tabIVBC3D = pw.add3DPlot(f'I-U-{x_axis_short} (crit.)', x_axis_caption, fr'I, {core_units[k_A]}A', fr'$U, {core_units[k_V_meas]}V$')

# 4) I-V-T 3D plot, retr. curr
tabIVBR3D = pw.add3DPlot(f'I-U-{x_axis_short} (3D) (retr.)', x_axis_caption, fr'I, {core_units[k_A]}A', fr'$U, {core_units[k_V_meas]}V$')

# 5) T - I - R 2D colormesh plot, crit. curr
tabIRBCMesh = pw.addColormesh(f'I-R-{x_axis_short} (Color mesh) (crit.)', x_axis_caption, fr"$I, {core_units[k_A]}A$",
                              uhf_sweep_values, currValues_axis, R_buff_C, R_3D_colormap)

# 6) T - I - R 2D colormesh plot, ret. curr
tabIRBRMesh = pw.addColormesh(f'I-R-{x_axis_short} (Color mesh) (retr.)', x_axis_caption, fr"$I, {core_units[k_A]}A$",
                              uhf_sweep_values, currValues_axis, R_buff_R, R_3D_colormap)

# 7) T - I - R 3D plot, crit. curr
tabIRBC3D = pw.add3DPlot(f'I-R-{x_axis_short} (3D) (crit.)', x_axis_caption, fr'I, {core_units[k_A]}A', fr'$R, Ohm$')

# 8) T - I - R 3D plot, retr. curr
tabIRBR3D = pw.add3DPlot(f'I-R--{x_axis_short} (3D) (retr.)', x_axis_caption, fr'I, {core_units[k_A]}A', fr'$R, Ohm$')




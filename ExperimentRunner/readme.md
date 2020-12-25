A simple C# program to run Python scripts in GUI mode. No command line or IPython notebooks are required to start measurement scripts.

Parameters are being sent to programs using a command-line interface. A typical script call looks like:

python I_V_T_auto.py -mkV -mkA -MOhm -R 3 -W 6 -L 17 2 0.5 0.001 100 0.02 500 Ti_Pt SQUID

where:
* -mkV -mkA -MOhm - measurement units. Data will be displayed on plots and saved to a result file in that units.
* -R 3 - current sweeping device (current source) VISA ID
* -W 6 - current output device ID, if required (for example, it controls magnetic field or gate voltage)
* -L 17 - cryostat temperature controlling device ID
* 2 - resistance (in units specified earlier)
* 0.5 - swept voltage range (always in Volts!)
* 0.001 - swept voltage step
* 100 - voltage gain, depends on your preamplifier
* 0.02 - time delay between sweep points
* 500 - how many voltage points will be measured at each point. A Leonardo, ADC board used in our equipment, can measure a lot of points continously. At each sweep point, 500 points will be taken and averaged.

Each measurement has its own tab with measurement parameters. Also, there is a tab to select NI VISA equipment IDs.

A program keeps settings for each tab separately (excluding sample name).

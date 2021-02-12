using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using Microsoft.Win32;
using System.Globalization;

namespace ExperimentRunner
{
    public partial class Form1 : Form
    {
        private RunParams meas_params = new RunParams();

        // Device IDs
        private int nYokRead, nYokWrite, nLakeShore;

        // Settings names in Windows registry
        private const String strSettingsTab = "ActiveTab";
        private const String strSampleName = "SampleName";
        private const String strYokRead = "SourceReadout";
        private const String strYokWrite = "SourceExcitation";
        private const String strLakeShore = "LakeShore";
        private const String sShapiroStartPower = "Shapiro_power_start";
        private const String sShapiroEndPower = "Shapiro_power_end";
        private const String sShapiroStepPower = "Shapiro_power_step";
        private const String sShapiroFixedPower = "Shapiro_const_freq";
        private const String sShapiroStartFreq = "Shapiro_freq_start";
        private const String sShapiroEndFreq = "Shapiro_freq_end";
        private const String sShapiroStepFreq = "Shapiro_freq_step";
        private const String sShapiroFixedFreq = "Shapiro_const_power";
        private const String sShapiroSelected = "Shapiro_type";

        //Shapiro steps masurement sweep modes
        private const int SHAPIRO_POWER = 0;
        private const int SHAPIRO_FREQ = 1;

        private const String strError = "Error";

        //Maximum parameter values which are allowed
        private const double MAX_TEMP = 1.7; //K
        private const float MAX_FIELD = 40; //G
        private const float MAX_CURR = 200; //mA
        private const float MAX_GATE = 4; //V
        private const float MAX_FREQ = 6; //GHz
        private const float MAX_POWER = -30; //dBm

        //tabs numbers
        private const int tabIV = 0;
        private const int tabIVTManual = 1;
        private const int tabIVTAuto = 2;
        private const int tabIVB = 3;
        private const int tabVB = 4;
        private const int tabCritStats = 5;
        private const int tabRT = 6;
        private const int tabRTGate = 7;
        private const int tabGate = 8;
        private const int tabGateT = 9;
        private const int tabGateB = 10;
        private const int tabShapiro = 11;
        private const int tabGatePulse = 12;

        // a flag that shows are the settings loaded into form controls
        // If no, don't handle text field change events
        private bool bFullInitialized = false;

        public Form1()
        {
            InitializeComponent();
        }

        private void button1_Click(object sender, EventArgs e)
        {
            this.Close();
        }

        // functions for input validation
        private bool CheckTemperature(float fInitial, float fNew, float fStep)
        {
            float eps = 0.001F;
            bool fCheckTemp = true;
            string[] args = Environment.GetCommandLineArgs();
            if (args.Count() == 2)
                if (args[1] == "-notemp")
                    fCheckTemp = false;
            if (fNew < fInitial && fStep>0)
            {
                MessageBox.Show(String.Format("Final temperature value {0} mK is less than a starter value {1} mK!", fNew*1000, fInitial),
                    strError, MessageBoxButtons.OK, MessageBoxIcon.Stop);
                return false;
            }
            if (fNew - eps > MAX_TEMP && fCheckTemp)
            {
                MessageBox.Show(String.Format("Invalid final temperature. A temperature more than {0} K is impossible physically!",MAX_TEMP),
                    strError, MessageBoxButtons.OK, MessageBoxIcon.Stop);
                return false;
            }
            if (fNew - eps > MAX_TEMP && !fCheckTemp)
            {
                MessageBox.Show("Warning a temperature is >1.7K, temperature check is disabled. You are performing this measurement on your own risk.", "Warning", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
            }
            return true;
        }

        private bool CheckOneValue(float value, float max_value, String value_name, String value_unit)
        {
            float eps = 0.001F;
            bool f = value - eps < max_value;
            if (!f) MessageBox.Show(String.Format("Too big {0}: {1} {2}, maximum is {3} {2}!", value_name, value, value_unit, max_value, MAX_FIELD),
                         strError, MessageBoxButtons.OK, MessageBoxIcon.Stop);
            return f;
        }

        private bool CheckField(float fRange)
        {
            return CheckOneValue(fRange, MAX_FIELD, "field", "G");
        }

        private bool CheckCurrents(params float[] fCurrents)
        {
            foreach (float curr in fCurrents)
            {
                if(!CheckOneValue(curr, MAX_CURR, "current", "mA")) return false;
            }
            return true;
        }

        private bool CheckGateVoltage(float fGate)
        {
            return CheckOneValue(fGate, MAX_FIELD, "gate voltage", "V");
        }

        private bool CheckFrequency(float freq)
        {
            return CheckOneValue(freq, MAX_FREQ, "frequency", "GHz");
        }

        private bool CheckPower(float power)
        {
            return CheckOneValue(power, MAX_POWER, "power", "dBm");
        }

        //Make a tab-specific validation (for additional experiment parameters)
        private bool ValidateCurrentTab(int nTabNumber)
        {
            float fStart, fEnd, fStep, fRange;
            float fCurr1, fCurr2, fCurr3;
            switch(nTabNumber)
            {
                case tabIVTAuto:  //I-U-T auto
                    fStart = chkIVTA_FromCurrent.Checked ? 0 : RunParams.GetValueFromField(txtIVTA_SweepFrom);
                    fEnd = RunParams.GetValueFromField(txtIVTA_SweepTo);
                    fStep = RunParams.GetValueFromField(txtIVTA_SweepStep);
                    return CheckTemperature(fStart, fEnd, fStep);
                case tabIVB: // I-U-B
                    fRange = RunParams.GetValueFromField(txtIVB_FieldRange);
                    return CheckField(fRange);
                case tabVB: //U-B
                    fRange = RunParams.GetValueFromField(txtVB_FieldRange);
                    fCurr1 = RunParams.GetValueFromField(txtVB_BiasStart);
                    fCurr2 = RunParams.GetValueFromField(txtVB_BiasEnd);
                    fCurr3 = RunParams.GetValueFromField(txtVB_BiasStep);
                    return CheckCurrents(new float[]{fCurr1, fCurr2, fCurr3}) && CheckField(fRange);
                case tabRTGate: //R-T-Gate
                    fStart = chkRTGate_FromStart.Checked ? 0 : RunParams.GetValueFromField(txtRTGate_SweepFrom);
                    fEnd = RunParams.GetValueFromField(txtRTGate_SweepTo);
                    fStep = RunParams.GetValueFromField(txtRTGate_SweepStep);
                    fRange = RunParams.GetValueFromField(txtRTGate_SweepStep);
                    return CheckTemperature(fStart, fEnd, fStep) && CheckField(fRange);
                case tabGate: //I-U-Gate:
                    fRange = RunParams.GetValueFromField(txtGate_VoltRange);
                    return CheckGateVoltage(fRange);
                case tabGateT: //I-U-Gate with different T
                    fStart = chkGateT_FromCurrent.Checked ? 0 : RunParams.GetValueFromField(txtGateT_TempStart);
                    fEnd = RunParams.GetValueFromField(txtGateT_TempEnd);
                    fStep = RunParams.GetValueFromField(txtGateT_TempStep);
                    fRange = RunParams.GetValueFromField(txtGateT_VoltRange);
                    return CheckGateVoltage(fRange) && CheckTemperature(fStart, fEnd, fStep);
                case tabGateB: //I-U-Gate with different B
                    fRange = RunParams.GetValueFromField(txtgateB_FieldSweep);
                    float fRange2 = RunParams.GetValueFromField(txtgateB_GateSweep);
                    return CheckGateVoltage(fRange2) && CheckField(fRange);
                case tabShapiro: //Shapiro steps
                    if(cboShapiroType.SelectedIndex == SHAPIRO_POWER)
                    {
                        float fPowerStart = RunParams.GetValueFromField(txtShapiroStart);
                        float fPowerEnd = RunParams.GetValueFromField(txtShapiroEnd);
                        float fFreq = RunParams.GetValueFromField(txtShapiro_Fixed);
                        return CheckPower(fPowerStart) && CheckPower(fPowerEnd) && CheckFrequency(fFreq);
                    }
                    else
                    {
                        float fFreqStart = RunParams.GetValueFromField(txtShapiroStart);
                        float fFreqEnd = RunParams.GetValueFromField(txtShapiroEnd);
                        float fPower = RunParams.GetValueFromField(txtShapiro_Fixed);
                        return CheckFrequency(fFreqStart) && CheckFrequency(fFreqEnd) && CheckPower(fPower);
                    }
                case tabGatePulse:
                    return true; //TODO: add voltage bounds
                default:
                    return true;
            }
        }

        private void cmdOK_Click(object sender, EventArgs e)
        {
            int nCurrentTab = tabControl1.SelectedIndex;
            if (!ValidateCurrentTab(nCurrentTab)) return;
            if (nCurrentTab == tabControl1.TabCount - 1) //the last tab
                MessageBox.Show("Please select a tab with needed measurement", strError, MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
            else if (!meas_params.IsReady())
            {
                MessageBox.Show("Entered values are invalid, please correct them and try again", strError, MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
            }
            else
                meas_params.StartMeasurement();
        }

        private void SaveSettings()
        {
            meas_params.FlushCurrentTabSettings(); //save currently active tab settings

            Settings sett = new Settings();
            sett.SaveSetting(strSettingsTab, tabControl1.SelectedIndex);
            sett.SaveSetting(strSampleName, txtSampleName.Text);

            sett.SaveSetting(strYokRead, nYokRead);
            sett.SaveSetting(strYokWrite, nYokWrite);
            sett.SaveSetting(strLakeShore, nLakeShore);

            SaveShapiroSettings(cboShapiroType.SelectedIndex);
        }

        private void LoadSettings()
        {
            Settings sett = new Settings();
            int nCurrentTab = 0;
            int settYokRead = 3, settYokWrite = 6, settLakeShore = 17;

            String strSampName="Sample 1";
            sett.TryLoadSetting(strSettingsTab, ref nCurrentTab); //default value is 0, so the first tab will be opened if there is no settings
            sett.TryLoadSetting(strSampleName, ref strSampName);

            sett.TryLoadSetting(strYokRead, ref settYokRead);
            sett.TryLoadSetting(strYokWrite, ref settYokWrite);
            sett.TryLoadSetting(strLakeShore, ref settLakeShore);

            nYokRead = settYokRead; nYokWrite = settYokWrite; nLakeShore = settLakeShore;
            meas_params.SetEquipment(nYokRead, nYokWrite, nLakeShore);
            txtExcitationDevice.Text = nYokWrite.ToString();
            txtReadoutDevice.Text = nYokRead.ToString();
            txtLakeShoreID.Text = nLakeShore.ToString();

            tabControl1.SelectedIndex = nCurrentTab;
            txtSampleName.Text = strSampName;
            meas_params.SetSampleName(strSampName);
            UpdateCurrentTab();
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            LoadSettings();
            bFullInitialized = true;
        }


        private void Form1_FormClosing(object sender, FormClosingEventArgs e)
        {
            SaveSettings();
        }

        //called when this tab is being loaded or opened by a user
        private void LoadTabSpecialSettings(int nTab)
        {
            Settings sett = new Settings();
            String strRead="";
            switch (nTab)
            {
                case tabIVTAuto: //I-V-T auto
                    if (sett.TryLoadSetting("I_V_T_auto_param0", ref strRead))
                    {
                        chkIVTA_FromCurrent.Checked = (strRead == "0");
                        txtIVTA_SweepFrom.Enabled = (strRead != "0");
                        txtIVTA_SweepFrom.Text = strRead;
                    }
                    if (sett.TryLoadSetting("I_V_T_auto_param1", ref strRead))
                    {
                        txtIVTA_SweepTo.Text = strRead;
                    }
                    if (sett.TryLoadSetting("I_V_T_auto_param2", ref strRead))
                    {
                        txtIVTA_SweepStep.Text = strRead;
                    }
                    meas_params.SetParameters(txtIVTA_SweepFrom.Text, txtIVTA_SweepTo.Text, txtIVTA_SweepStep.Text);
                    break;
                case tabIVB: //I-V-B 
                    if (sett.TryLoadSetting("I_V_B_param0", ref strRead))
                    {
                        txtIVB_FieldRange.Text = strRead;
                    }
                    if (sett.TryLoadSetting("I_V_B_param1", ref strRead))
                    {
                        txtIVB_FieldStep.Text = strRead;
                    }
                    meas_params.SetParameters(txtIVB_FieldRange.Text, txtIVB_Step.Text);
                    break;
                case tabVB: //V-B 
                    if (sett.TryLoadSetting("V_B_param0", ref strRead))
                    {
                        txtVB_FieldRange.Text = strRead;
                    }
                    if (sett.TryLoadSetting("V_B_param1", ref strRead))
                    {
                        txtVB_FieldStep.Text = strRead;
                    }
                    if (sett.TryLoadSetting("V_B_param2", ref strRead))
                    {
                        txtVB_BiasStart.Text = strRead;
                    }
                    if (sett.TryLoadSetting("V_B_param3", ref strRead))
                    {
                        txtVB_BiasEnd.Text = strRead;
                    }
                    if (sett.TryLoadSetting("V_B_param4", ref strRead))
                    {
                        txtVB_BiasStep.Text = strRead;
                    }
                    meas_params.SetParameters(txtVB_FieldRange.Text, txtVB_Step.Text, txtVB_BiasStart.Text, txtVB_BiasEnd.Text, txtVB_BiasStep.Text);
                    break;
                case tabCritStats: //critical current distribution
                    if (sett.TryLoadSetting("I_V_crit_stats_param0", ref strRead))
                    {
                        txtStats_nCurves.Text = strRead;
                    }
                    meas_params.SetParameters(txtStats_nCurves.Text);
                    break;
                case tabRT: //R-T
                    if (sett.TryLoadSetting("R_T_param0", ref strRead))
                    {
                        txtRT_TempLimit.Text = strRead;
                    }
                    meas_params.SetParameters(strRead);
                    break;
                case tabRTGate:
                    if (sett.TryLoadSetting("R_T_Gate_param0", ref strRead))
                    {
                        txtRTGate_SweepFrom.Text = strRead;
                        chkRTGate_FromStart.Checked = (strRead == "0");
                        txtRTGate_SweepFrom.Enabled = (strRead != "0");
                    }
                    if (sett.TryLoadSetting("R_T_Gate_param1", ref strRead))
                    {
                        txtRTGate_SweepTo.Text = strRead;
                    }
                    if (sett.TryLoadSetting("R_T_Gate_param2", ref strRead))
                    {
                        txtRTGate_SweepStep.Text = strRead;
                    }
                    if (sett.TryLoadSetting("R_T_Gate_param3", ref strRead))
                    {
                        txtRTGate_GateRange.Text = strRead;
                    }
                    if (sett.TryLoadSetting("R_T_Gate_param4", ref strRead))
                    {
                        txtRTGate_GatePoints.Text = strRead;
                    }

                    meas_params.SetParameters(txtRTGate_SweepFrom.Text, txtRTGate_SweepTo.Text, txtRTGate_SweepStep.Text, txtRTGate_GateRange.Text, txtRTGate_GatePoints.Text);
                    break;
                case tabGate: //I-V with gate
                    if (sett.TryLoadSetting("I_V_Gate_param0", ref strRead))
                    {
                        txtGate_VoltRange.Text = strRead;
                    }
                    if (sett.TryLoadSetting("I_V_Gate_param1", ref strRead))
                    {
                        txtGate_VoltStep.Text = strRead;
                    }
                    meas_params.SetParameters(txtGate_VoltRange.Text, txtGate_VoltStep.Text);
                    break;
                case tabGateT: //I-V with gate and T sweep
                    if (sett.TryLoadSetting("I_V_Gate_T_param0", ref strRead))
                    {
                        txtGateT_VoltRange.Text = strRead;
                    }
                    if (sett.TryLoadSetting("I_V_Gate_T_param1", ref strRead))
                    {
                        txtGateT_VoltStep.Text = strRead;
                    }
                    if (sett.TryLoadSetting("I_V_Gate_T_param2", ref strRead))
                    {
                        txtGateT_TempStart.Text = strRead;
                        chkGateT_FromCurrent.Checked = (strRead == "0");
                        txtGateT_TempStart.Enabled = (strRead != "0");
                    }
                    if (sett.TryLoadSetting("I_V_Gate_T_param3", ref strRead))
                    {
                        txtGateT_TempEnd.Text = strRead;
                    }
                    if (sett.TryLoadSetting("I_V_Gate_T_param4", ref strRead))
                    {
                        txtGateT_TempStep.Text = strRead;
                    }
                    meas_params.SetParameters(txtGateT_VoltRange.Text, txtGateT_VoltStep.Text, txtGateT_TempStart.Text, txtGateT_TempEnd.Text, txtGateT_TempStep.Text);
                    break;
                case tabGateB: //I-V with gate and B sweep
                    if (sett.TryLoadSetting("I_V_Gate_B_param0", ref strRead))
                    {
                        txtgateB_GateSweep.Text = strRead;
                    }
                    if (sett.TryLoadSetting("I_V_Gate_B_param1", ref strRead))
                    {
                        txtgateB_GatePoints.Text = strRead;
                    }
                    if (sett.TryLoadSetting("I_V_Gate_B_param2", ref strRead))
                    {
                        txtgateB_FieldSweep.Text = strRead;
                    }
                    if (sett.TryLoadSetting("I_V_Gate_B_param3", ref strRead))
                    {
                        txtgateB_FieldPoints.Text = strRead;
                    }
                    meas_params.SetParameters(txtgateB_GateSweep.Text, txtgateB_GatePoints.Text, txtgateB_FieldSweep.Text, txtgateB_FieldPoints.Text);
                    break;
                case tabShapiro: //Shapiro steps
                    bFullInitialized = false;
                    LoadShapiroSettings();
                    bFullInitialized = true;
                    break;
                case tabGatePulse:
                    if (sett.TryLoadSetting("Gate_pulse_param0", ref strRead))
                    {
                        txtGatePulses_SweepFrom.Text = strRead;
                    }
                    if (sett.TryLoadSetting("Gate_pulse_param1", ref strRead))
                    {
                        txtGatePulses_SweepTo.Text = strRead;
                    }
                    if (sett.TryLoadSetting("Gate_pulse_param2", ref strRead))
                    {
                        txtGatePulses_SweepStep.Text = strRead;
                    }
                    if (sett.TryLoadSetting("Gate_pulse_param3", ref strRead))
                    {
                        txtGatePulses_Repeat.Text = strRead;
                    }
                    if (sett.TryLoadSetting("Gate_pulse_param4", ref strRead))
                    {
                        txtGatePulses_Amplitude.Text = strRead;
                    }
                    if (sett.TryLoadSetting("Gate_pulse_param5", ref strRead))
                    {
                        txtGatePulses_BiasCurrent.Text = strRead;
                    }
                    if (sett.TryLoadSetting("Gate_pulse_param6", ref strRead))
                    {
                        txtGatePulses_DeviceID.Text = strRead;
                    }
                    meas_params.SetParameters(txtGatePulses_SweepFrom.Text, txtGatePulses_SweepTo.Text, txtGatePulses_SweepStep.Text, txtGatePulses_Repeat.Text,
                        txtGatePulses_Amplitude.Text, txtGatePulses_BiasCurrent.Text, txtGatePulses_DeviceID.Text);
                    break;
            }
        }

        private String FieldToCurrent(String field)
        {
            NumberFormatInfo f = new NumberFormatInfo();
            f.NumberDecimalSeparator = ".";
            float fField = float.Parse(field, f);
            return (fField * 10).ToString();
        }

        private void UpdateCurrentTab()
        {
            int i = tabControl1.SelectedIndex;
            int i_old = meas_params.CurrentTab;

            if (i_old == 10)
                SaveShapiroSettings(cboShapiroType.SelectedIndex);

            switch (i)
            {
                case tabIV: //I-V
                    meas_params.UpdateControls(i, btnIV_MkV, btnIV_mV, btnIV_nA, btnIV_mkA, btnIV_mA, txtIV_Resistance, btnIV_kOhm, btnIV_mOhm,
                        txtIV_Range, txtIV_Step, txtIV_RangeI, txtIV_StepI, txtIV_Gain, txtIV_Delay, txtIV_Samples);
                    break;
                case tabIVTManual: //I-V-T manual
                    meas_params.UpdateControls(i, btnIVTM_mkV, btnIVTM_mV, btnIVTM_nA, btnIVTM_mkA, btnIVTM_mA, txtIVTM_Resistance, btnIVTM_KOhm, btnIVTM_MOhm,
                        txtIVTM_Range, txtIVTM_Step, txtIVTM_RangeI, txtIVTM_StepI, txtIVTM_Gain, txtIVTM_Delay, txtIVTM_Samples);
                    break;
                case tabIVTAuto: //I-V-T auto
                    meas_params.UpdateControls(i, btnIVTA_mkV, btnIVTA_mV, btnIVTA_nA, btnIVTA_mkA, btnIVTA_mA, txtIVTA_Resistance, btnIVTA_KOhm, btnIVTA_MOhm,
                        txtIVTA_Range, txtIVTA_Step, txtIVTA_RangeI, txtIVTA_StepI, txtIVTA_Gain, txtIVTA_Delay, txtIVTA_Samples);
                    meas_params.SetParameters(txtIVTA_SweepFrom.Text, txtIVTA_SweepTo.Text, txtIVTA_SweepStep.Text);
                    break;
                case tabIVB: //I-V-B 
                    meas_params.UpdateControls(i, btnIVB_mkV, btnIVB_mV, btnIVB_nA, btnIVB_mkA, btnIVB_mA, txtIVB_Resistance, btnIVB_KOhm, btnIVB_MOhm,
                        txtIVB_Range, txtIVB_Step, txtIVB_RangeI, txtIVB_StepI, txtIVB_Gain, txtIVB_Delay, txtIVB_Samples);
                    meas_params.SetParameters(txtIVB_FieldRange.Text, txtIVB_FieldStep.Text);  
                    break;
                case tabVB: //V-B 
                    meas_params.UpdateControls(i, btnVB_mkV, btnVB_mV, btnVB_nA, btnVB_mkA, btnVB_mA, txtVB_Resistance, btnVB_KOhm, btnVB_MOhm,
                        txtVB_Range, txtVB_Step, txtVB_RangeI, txtVB_StepI, txtVB_Gain, txtVB_Delay, txtVB_Samples);
                    meas_params.SetParameters(FieldToCurrent(txtVB_FieldRange.Text), FieldToCurrent(txtVB_FieldStep.Text), txtVB_BiasStart.Text, txtVB_BiasEnd.Text, txtVB_BiasStep.Text);
                    break;
                case tabCritStats: //critical current distribution
                    meas_params.UpdateControls(i, btnStats_mkV, btnStats_mV, btnStats_nA, btnStats_mkA, btnStats_mA, txtStats_Resistance, btnStats_KOhm, btnStats_MOhm,
                        txtStats_Range, txtStats_Step, txtStats_RangeI, txtStats_StepI, txtStats_Gain, txtStats_Delay, txtStats_Samples);
                    meas_params.SetParameters(txtStats_nCurves.Text);
                    break;
                case tabRT: //R-T
                    meas_params.UpdateControls(i, btnRT_mkV, btnRT_mV, btnRT_nA, btnRT_mkA, btnRT_mA, txtRT_Resistance, btnRT_KOhm, btnRT_MOhm,
                        txtRT_Range, txtRT_Step, txtRT_RangeI, txtRT_StepI, txtRT_Gain, txtRT_Delay, txtRT_Samples);
                    meas_params.SetParameters(txtRT_TempLimit.Text);
                    break;
                case tabRTGate:
                    meas_params.UpdateControls(i, btnRTGate_mkV, btnRTGate_mV, btnRT_nA, btnRTGate_mkA, btnRTGate_mA, txtRTGate_Resistance, btnRTGate_KOhm, btnRTGate_MOhm,
                        txtRTGate_Range, txtRTGate_Step, txtRTGate_RangeI, txtRTGate_StepI, txtRTGate_Gain, txtRTGate_Delay, txtRTGate_Samples);
                    meas_params.SetParameters(txtRTGate_SweepFrom.Text, txtRTGate_SweepTo.Text, txtRTGate_SweepStep.Text, txtRTGate_GateRange.Text, txtRTGate_GatePoints.Text);
                    break;
                case tabGate: //I-V with gate
                    meas_params.UpdateControls(i, btnGate_mkV, btnGate_mV, btnGate_nA, btnGate_mkA, btnGate_mA, txtGate_Resistance, btnGate_KOhm, btnGate_MOhm,
                        txtGate_Range, txtGate_Step, txtGate_RangeI, txtGate_StepI, txtGate_Gain, txtGate_Delay, txtGate_Samples);
                    meas_params.SetParameters(txtGate_VoltRange.Text, txtGate_VoltStep.Text);
                    break;
                case tabGateT: //I-V with gate and T sweep
                    meas_params.UpdateControls(i, btngateT_mkV, btngateT_mV, btngateT_nA, btngateT_mkA, btngateT_mA, txtgateT_Resistance, btngateT_KOhm, btngateT_MOhm,
                        txtgateT_Range, txtgateT_Step, txtgateT_RangeI, txtgateT_StepI, txtgateT_Gain, txtgateT_Delay, txtgateT_Samples);
                    meas_params.SetParameters(txtGateT_VoltRange.Text, txtGateT_VoltStep.Text, txtGateT_TempStart.Text, txtGateT_TempEnd.Text, txtGateT_TempStep.Text);
                    break;
                case tabGateB: //I-V with gate and B sweep
                    meas_params.UpdateControls(i, btngateB_mkV, btngateB_mV, btngateB_nA, btngateB_mkA, btngateB_mA, txtgateB_Resistance, btngateB_KOhm, btngateB_MOhm,
                        txtgateB_Range, txtgateB_Step, txtgateB_RangeI, txtgateB_StepI, txtgateB_Gain, txtgateB_Delay, txtgateB_Samples);
                    meas_params.SetParameters(txtgateB_GateSweep.Text, txtgateB_GatePoints.Text, txtgateB_FieldSweep.Text, txtgateB_FieldPoints.Text);
                    break;
                case tabShapiro:  //Shapiro steps
                    meas_params.UpdateControls(i, btnShapiro_mkV, btnShapiro_mV, btnShapiro_nA, btnShapiro_mkA, btnShapiro_mA, txtShapiro_Resistance, btnShapiro_KOhm, btnShapiro_MOhm,
                        txtShapiro_Range, txtShapiro_Step, txtShapiro_RangeI, txtShapiro_StepI, txtShapiro_Gain, txtShapiro_Delay, txtShapiro_Samples);
                    //meas_params will be set in another procedures called from combo box change event handler or on tab initialization
                    break;
                case tabGatePulse: //Gate pulses
                    meas_params.UpdateControls(i, btnGatePulses_mkV, btnGatePulses_mV, btnGatePulses_nA, btnGatePulses_mkA, btnGatePulses_mA, txtGatePulses_Resistance,
                        btnGatePulses_KOhm, btnGatePulses_MOhm, txtGatePulses_Range, txtGatePulses_Step, txtGatePulses_RangeI, txtGatePulses_StepI,
                            txtGatePulses_Gain, txtGatePulses_Delay, txtGatePulses_Samples);
                    meas_params.SetParameters(txtGatePulses_SweepFrom.Text, txtGatePulses_SweepTo.Text, txtGatePulses_SweepStep.Text, txtGatePulses_Repeat.Text,
                        txtGatePulses_Amplitude.Text, txtGatePulses_BiasCurrent.Text, txtGatePulses_DeviceID.Text);
                    break;
            }
            LoadTabSpecialSettings(i);
        }

        private void tabControl1_SelectedIndexChanged(object sender, EventArgs e)
        {
            UpdateCurrentTab();
        }

        private void txtSampleName_TextChanged(object sender, EventArgs e)
        {
            meas_params.SetSampleName(txtSampleName.Text);
        }

        private void txtReadoutDevice_TextChanged(object sender, EventArgs e)
        {
            nYokRead = Int32.Parse(txtReadoutDevice.Text);
            meas_params.SetReadDevice(nYokRead);
        }

        private void txtExcitationDevice_TextChanged(object sender, EventArgs e)
        {
            nYokWrite = Int32.Parse(txtExcitationDevice.Text);
            meas_params.SetWriteDevice(nYokWrite);
        }

        private void txtLakeShoreID_TextChanged(object sender, EventArgs e)
        {
            nLakeShore = Int32.Parse(txtLakeShoreID.Text);
            meas_params.SetLakeShore(nLakeShore);
        }

        private void txtReadoutDevice_KeyPress(object sender, KeyPressEventArgs e)
        {
            InputValidator.HandleKeyEvent(e, false, false);
        }

        private void txtExcitationDevice_KeyPress(object sender, KeyPressEventArgs e)
        {
            InputValidator.HandleKeyEvent(e, false, false);
        }

        private void txtLakeShoreID_KeyPress(object sender, KeyPressEventArgs e)
        {
            InputValidator.HandleKeyEvent(e, false, false);
        }
        //
        private void chkSaveData_CheckedChanged(object sender, EventArgs e)
        {
            meas_params.SetSaveData(chkSaveData.Checked);
        }

        private void chkIVTA_FromCurrent_CheckedChanged(object sender, EventArgs e)
        {
            if (!bFullInitialized) return;
            txtIVTA_SweepFrom.Enabled = !chkIVTA_FromCurrent.Checked;
            if(chkIVTA_FromCurrent.Checked)
                meas_params.UpdateParameter(0, "0");  // If "from current temp." is checked, the swept range start must be zero
            else
                meas_params.UpdateParameter(0, txtIVTA_SweepFrom.Text);
        }

        private void txtIVTA_SweepFrom_TextChanged(object sender, EventArgs e)
        {
            if (!bFullInitialized) return;
            meas_params.UpdateParameter(0, txtIVTA_SweepFrom.Text);
        }

        private void txtIVTA_SweepTo_TextChanged(object sender, EventArgs e)
        {
            if (!bFullInitialized) return;
            meas_params.UpdateParameter(1, txtIVTA_SweepTo.Text);
        }

        private void txtIVTA_SweepStep_TextChanged(object sender, EventArgs e)
        {
            if (!bFullInitialized) return;
            meas_params.UpdateParameter(2, txtIVTA_SweepStep.Text);
        }

        private void txtIVTA_SweepFrom_KeyPress(object sender, KeyPressEventArgs e)
        {
            if (!bFullInitialized) return;
            InputValidator.HandleKeyEvent(e, true, false);
        }

        private void txtIVTA_SweepTo_KeyPress(object sender, KeyPressEventArgs e)
        {
            InputValidator.HandleKeyEvent(e, true, false);
        }

        private void txtIVTA_SweepStep_KeyPress(object sender, KeyPressEventArgs e)
        {
            InputValidator.HandleKeyEvent(e, true, false);
        }
        //
        private void txtIVB_FieldRange_KeyPress(object sender, KeyPressEventArgs e)
        {
            if (!bFullInitialized) return;
            InputValidator.HandleKeyEvent(e, true, false);
        }

        private void txtIVB_FieldStep_KeyPress(object sender, KeyPressEventArgs e)
        {
            if (!bFullInitialized) return;
            InputValidator.HandleKeyEvent(e, true, false);
        }

        private void txtIVB_FieldRange_TextChanged(object sender, EventArgs e)
        {
            if (!bFullInitialized) return;
            meas_params.UpdateParameter(0, txtIVB_FieldRange.Text);
        }

        private void txtIVB_FieldStep_TextChanged(object sender, EventArgs e)
        {
            if (!bFullInitialized) return;
            meas_params.UpdateParameter(1, txtIVB_FieldStep.Text);
        }
        //
        private void txtVB_FieldRange_KeyPress(object sender, KeyPressEventArgs e)
        {
            if (!bFullInitialized) return;
            InputValidator.HandleKeyEvent(e, true, false);
        }

        private void txtVB_FieldStep_KeyPress(object sender, KeyPressEventArgs e)
        {
            if (!bFullInitialized) return;
            InputValidator.HandleKeyEvent(e, true, false);
        }

        private void txtVB_BiasStart_KeyPress(object sender, KeyPressEventArgs e)
        {
            if (!bFullInitialized) return;
            InputValidator.HandleKeyEvent(e, true, false);
        }

        private void txtVB_BiasEnd_KeyPress(object sender, KeyPressEventArgs e)
        {
            if (!bFullInitialized) return;
            InputValidator.HandleKeyEvent(e, true, false);
        }

        private void txtVB_BiasStep_KeyPress(object sender, KeyPressEventArgs e)
        {
            if (!bFullInitialized) return;
            InputValidator.HandleKeyEvent(e, true, false);
        }

        private void txtVB_FieldRange_TextChanged(object sender, EventArgs e)
        {
            if (!bFullInitialized) return;
            meas_params.UpdateParameter(0, txtVB_FieldRange.Text);
        }

        private void txtVB_FieldStep_TextChanged(object sender, EventArgs e)
        {
            if (!bFullInitialized) return;
            meas_params.UpdateParameter(1, txtVB_FieldStep.Text);
        }

        private void txtVB_BiasStart_TextChanged(object sender, EventArgs e)
        {
            if (!bFullInitialized) return;
            meas_params.UpdateParameter(2, txtVB_BiasStart.Text);
        }

        private void txtVB_BiasEnd_TextChanged(object sender, EventArgs e)
        {
            if (!bFullInitialized) return;
            meas_params.UpdateParameter(3, txtVB_BiasEnd.Text);
        }

        private void txtVB_BiasStep_TextChanged(object sender, EventArgs e)
        {
            if (!bFullInitialized) return;
            meas_params.UpdateParameter(4, txtVB_BiasStep.Text);
        }
        //
        private void txtStats_nCurves_KeyPress(object sender, KeyPressEventArgs e)
        {
            if (!bFullInitialized) return;
            InputValidator.HandleKeyEvent(e, false, false);
        }

        private void txtStats_nCurves_TextChanged(object sender, EventArgs e)
        {
            if (!bFullInitialized) return;
            meas_params.UpdateParameter(0, txtStats_nCurves.Text);
        }
        //
        private void txtGate_VoltRange_KeyPress(object sender, KeyPressEventArgs e)
        {
            if (!bFullInitialized) return;
            InputValidator.HandleKeyEvent(e, true, false);
        }

        private void txtGate_VoltStep_KeyPress(object sender, KeyPressEventArgs e)
        {
            if (!bFullInitialized) return;
            InputValidator.HandleKeyEvent(e, false, false);
        }

        private void txtGate_VoltRange_TextChanged(object sender, EventArgs e)
        {
            if (!bFullInitialized) return;
            meas_params.UpdateParameter(0, txtGate_VoltRange.Text);
        }

        private void txtGate_VoltStep_TextChanged(object sender, EventArgs e)
        {
            if (!bFullInitialized) return;
            meas_params.UpdateParameter(1, txtGate_VoltStep.Text);
        }
        //
        private void txtGateT_VoltRange_KeyPress(object sender, KeyPressEventArgs e)
        {
            if (!bFullInitialized) return;
            InputValidator.HandleKeyEvent(e, true, false);
        }

        private void txtGateT_VoltStep_KeyPress(object sender, KeyPressEventArgs e)
        {
            if (!bFullInitialized) return;
            InputValidator.HandleKeyEvent(e, false, false);
        }

        private void txtGateT_VoltRange_TextChanged(object sender, EventArgs e)
        {
            if (!bFullInitialized) return;
            meas_params.UpdateParameter(0, txtGateT_VoltRange.Text);
        }

        private void txtGateT_VoltStep_TextChanged(object sender, EventArgs e)
        {
            if (!bFullInitialized) return;
            meas_params.UpdateParameter(1, txtGateT_VoltStep.Text);
        }

        private void txtGateT_TempStart_TextChanged(object sender, EventArgs e)
        {
            if (!bFullInitialized) return;
            meas_params.UpdateParameter(2, txtGateT_TempStart.Text);
        }

        private void txtGateT_TempEnd_TextChanged(object sender, EventArgs e)
        {
            if (!bFullInitialized) return;
            meas_params.UpdateParameter(3, txtGateT_TempEnd.Text);
        }

        private void txtGateT_TempStep_TextChanged(object sender, EventArgs e)
        {
            if (!bFullInitialized) return;
            meas_params.UpdateParameter(4, txtGateT_TempStep.Text);
        }

        private void chkGateT_FromCurrent_CheckedChanged(object sender, EventArgs e)
        {
            if (!bFullInitialized) return;
            txtGateT_TempStart.Enabled = !chkGateT_FromCurrent.Checked;
            if (chkGateT_FromCurrent.Checked)
                meas_params.UpdateParameter(2, "0");
            else
                meas_params.UpdateParameter(2, txtGateT_TempStart.Text);
        }
        //
        private void SaveShapiroSettings(int nSelected)
        { 
            Settings ss = new Settings();
            String sSettingStart = nSelected == SHAPIRO_POWER ? sShapiroStartPower : sShapiroStartFreq;
            String sSettingEnd = nSelected == SHAPIRO_POWER ? sShapiroEndPower : sShapiroEndFreq;
            String sSettingStep = nSelected == SHAPIRO_POWER ? sShapiroStepPower : sShapiroStepFreq;
            String sSettingFixed = nSelected == SHAPIRO_POWER ? sShapiroFixedPower : sShapiroFixedFreq;

            ss.SaveSetting(sSettingStart, txtShapiroStart.Text);
            ss.SaveSetting(sSettingEnd, txtShapiroEnd.Text);
            ss.SaveSetting(sSettingStep, txtShapiroStep.Text);
            ss.SaveSetting(sSettingFixed, txtShapiro_Fixed.Text);

            ss.SaveSetting(sShapiroSelected, nSelected);
        }

        private void LoadShapiroSettings()
        {
            Settings ss = new Settings();

            int nListSelected = 0;
            ss.TryLoadSetting(sShapiroSelected, ref nListSelected);

            UpdateShapiroSettings(nListSelected);
            cboShapiroType.SelectedIndex = nListSelected; // select an item from a list and update labels (an event handler will be called)
        }

        private void UpdateShapiroSettings(int nSelected)
        {
            Settings ss = new Settings();

            // settings registry keys
            String sSettingStart = nSelected == SHAPIRO_POWER ? sShapiroStartPower : sShapiroStartFreq;
            String sSettingEnd = nSelected == SHAPIRO_POWER ? sShapiroEndPower : sShapiroEndFreq;
            String sSettingStep = nSelected == SHAPIRO_POWER ? sShapiroStepPower : sShapiroStepFreq;
            String sSettingFixed = nSelected == SHAPIRO_POWER ? sShapiroFixedPower : sShapiroFixedFreq;

            // settings default values
            String sDefaultStart = nSelected == SHAPIRO_POWER ? "-50" : "1";
            String sDefaultEnd = nSelected == SHAPIRO_POWER ? "-30" : "4";
            String sDefaultStep = nSelected == SHAPIRO_POWER ? "1" : "0.25";
            String sDefaultFixed = nSelected == SHAPIRO_POWER ? "1" : "-50";


            String sRead = sDefaultStart;
            ss.TryLoadSetting(sSettingStart, ref sRead);
            txtShapiroStart.Text = sRead;
            sRead = sDefaultEnd;
            ss.TryLoadSetting(sSettingEnd, ref sRead);
            txtShapiroEnd.Text = sRead;
            sRead = sDefaultStep;
            ss.TryLoadSetting(sSettingStep, ref sRead);
            txtShapiroStep.Text = sRead;
            sRead = sDefaultFixed;
            ss.TryLoadSetting(sSettingFixed, ref sRead);
            txtShapiro_Fixed.Text = sRead;

            meas_params.SetParameters(nSelected.ToString(), txtShapiroStart.Text, txtShapiroEnd.Text, txtShapiroStep.Text, txtShapiro_Fixed.Text);
        }

        private void UpdateShapiroUI(int i)
        {
            String[] strLabels = new String[] { "Power", "Freq." };
            String[] strUnits = new String[] { "dBm", "GHz" };
            String nowLabel = strLabels[i];
            String nowUnit = strUnits[i];

            lblShapiro_From.Text = nowLabel + " from:";
            lblShapiro_To.Text = nowLabel + " to:";
            lblShapiro_Step.Text = nowLabel + " step:";
            lblShapiro_Fixed.Text = strLabels[strLabels.Count() - i - 1] + ":";

            lblShapiro_UnitsFrom.Text = lblShapiro_UnitsTo.Text = lblShapiro_UnitsStep.Text = nowUnit;
            lblShapiro_UnitsFixed.Text = strUnits[strUnits.Count() - i - 1];
        }

        private void cboShapiroType_SelectedIndexChanged(object sender, EventArgs e)
        {
            int i = cboShapiroType.SelectedIndex;
            UpdateShapiroUI(i);

            // if it is not a first (programmatic) list item set, save current values and load new ones
            if (bFullInitialized)
            {
                SaveShapiroSettings(2 - i - 1); //save settings of previous values, not current
                UpdateShapiroSettings(i); //load new values
            }

            meas_params.SetParameters(i.ToString(), txtShapiroStart.Text, txtShapiroEnd.Text, txtShapiroStep.Text, txtShapiro_Fixed.Text); 
        }

        private void txtShapiroStart_TextChanged(object sender, EventArgs e)
        {
            if (!bFullInitialized) return;
            meas_params.UpdateParameter(1, txtShapiroStart.Text);
        }

        private void txtShapiroEnd_TextChanged(object sender, EventArgs e)
        {
            if (!bFullInitialized) return;
            meas_params.UpdateParameter(2, txtShapiroEnd.Text);
        }

        private void txtShapiroStep_TextChanged(object sender, EventArgs e)
        {
            if (!bFullInitialized) return;
            meas_params.UpdateParameter(3, txtShapiroStep.Text);
        }

        private void txtShapiro_Fixed_TextChanged(object sender, EventArgs e)
        {
            if (!bFullInitialized) return;
            meas_params.UpdateParameter(4, txtShapiro_Fixed.Text);
        }

        private void txtShapiroStart_KeyPress(object sender, KeyPressEventArgs e)
        {
            InputValidator.HandleKeyEvent(e, true, false);
        }

        private void txtShapiroEnd_KeyPress(object sender, KeyPressEventArgs e)
        {
            InputValidator.HandleKeyEvent(e, true, false);
        }

        private void txtShapiroStep_KeyPress(object sender, KeyPressEventArgs e)
        {
            InputValidator.HandleKeyEvent(e, true, false);
        }

        private void txtShapiro_Fixed_KeyPress(object sender, KeyPressEventArgs e)
        {
            InputValidator.HandleKeyEvent(e, true, false);
        }
        //
        private void txtgateB_GateSweep_KeyPress(object sender, KeyPressEventArgs e)
        {
            InputValidator.HandleKeyEvent(e, true, false);
        }

        private void txtgateB_GatePoints_KeyPress(object sender, KeyPressEventArgs e)
        {
            InputValidator.HandleKeyEvent(e, true, false);
        }

        private void txtgateB_FieldSweep_KeyPress(object sender, KeyPressEventArgs e)
        {
            InputValidator.HandleKeyEvent(e, true, false);
        }

        private void txtgateB_FieldPoints_KeyPress(object sender, KeyPressEventArgs e)
        {
            InputValidator.HandleKeyEvent(e, true, false);
        }
        //
        private void txtRT_TempLimit_KeyPress(object sender, KeyPressEventArgs e)
        {
            InputValidator.HandleKeyEvent(e, true, false);
        }

        private void txtRT_TempLimit_TextChanged(object sender, EventArgs e)
        {
            meas_params.UpdateParameter(0, txtRT_TempLimit.Text);
        }
        //
        private void txtRTGate_SweepFrom_TextChanged(object sender, EventArgs e)
        {
            meas_params.UpdateParameter(0, txtRTGate_SweepFrom.Text);
        }

        private void txtRTGate_SweepTo_TextChanged(object sender, EventArgs e)
        {
            meas_params.UpdateParameter(1, txtRTGate_SweepTo.Text);
        }

        private void txtRTGate_SweepStep_TextChanged(object sender, EventArgs e)
        {
            meas_params.UpdateParameter(2, txtRTGate_SweepStep.Text);
        }

        private void txtRTGate_GateRange_TextChanged(object sender, EventArgs e)
        {
            meas_params.UpdateParameter(3, txtRTGate_GateRange.Text);
        }

        private void txtRTGate_GatePoints_TextChanged(object sender, EventArgs e)
        {
            meas_params.UpdateParameter(4, txtRTGate_GatePoints.Text);
        }

        private void txtRTGate_GateRange_KeyPress(object sender, KeyPressEventArgs e)
        {
            InputValidator.HandleKeyEvent(e, true, false);
        }

        private void txtRTGate_GatePoints_KeyPress(object sender, KeyPressEventArgs e)
        {
            InputValidator.HandleKeyEvent(e, true, false);
        }

        private void txtRTGate_SweepFrom_KeyPress(object sender, KeyPressEventArgs e)
        {
            InputValidator.HandleKeyEvent(e, true, false);
        }

        private void txtRTGate_SweepTo_KeyPress(object sender, KeyPressEventArgs e)
        {
            InputValidator.HandleKeyEvent(e, true, false);
        }

        private void txtRTGate_SweepStep_KeyPress(object sender, KeyPressEventArgs e)
        {
            InputValidator.HandleKeyEvent(e, true, false);
        }

        private void chkRTGate_FromStart_CheckedChanged(object sender, EventArgs e)
        {
            if (!bFullInitialized) return;
            txtRTGate_SweepFrom.Enabled = !chkRTGate_FromStart.Checked;
            if (chkRTGate_FromStart.Checked)
                meas_params.UpdateParameter(0, "0");  // If "from current temp." is checked, the swept range start must be zero
            else
                meas_params.UpdateParameter(0, txtRTGate_SweepFrom.Text);
        }

        //

        private void txtGatePulses_SweepFrom_TextChanged(object sender, EventArgs e)
        {
            meas_params.UpdateParameter(0, txtGatePulses_SweepFrom.Text);
        }

        private void txtGatePulses_SweepTo_TextChanged(object sender, EventArgs e)
        {
            meas_params.UpdateParameter(1, txtGatePulses_SweepTo.Text);
        }

        private void txtGatePulses_SweepStep_TextChanged(object sender, EventArgs e)
        {
            meas_params.UpdateParameter(2, txtGatePulses_SweepStep.Text);
        }

        private void txtGatePulses_Repeat_TextChanged(object sender, EventArgs e)
        {
            meas_params.UpdateParameter(3, txtGatePulses_Repeat.Text);
        }

        private void txtGatePulses_Amplitude_TextChanged(object sender, EventArgs e)
        {
            meas_params.UpdateParameter(4, txtGatePulses_Amplitude.Text);
        }

        private void txtGatePulses_BiasCurrent_TextChanged(object sender, EventArgs e)
        {
            meas_params.UpdateParameter(5, txtGatePulses_BiasCurrent.Text);
        }

        private void txtGatePulses_DeviceID_TextChanged(object sender, EventArgs e)
        {
            meas_params.UpdateParameter(6, txtGatePulses_DeviceID.Text);
        }

        private void txtGatePulses_SweepFrom_KeyPress(object sender, KeyPressEventArgs e)
        {
            InputValidator.HandleKeyEvent(e, true, true);
        }

        private void txtGatePulses_SweepTo_KeyPress(object sender, KeyPressEventArgs e)
        {
            InputValidator.HandleKeyEvent(e, true, true);
        }

        private void txtGatePulses_SweepStep_KeyPress(object sender, KeyPressEventArgs e)
        {
            InputValidator.HandleKeyEvent(e, true, true);
        }

        private void txtGatePulses_Repeat_KeyPress(object sender, KeyPressEventArgs e)
        {
            InputValidator.HandleKeyEvent(e, false, false);
        }

        private void txtGatePulses_Amplitude_KeyPress(object sender, KeyPressEventArgs e)
        {
            InputValidator.HandleKeyEvent(e, true, false);
        }

        private void txtGatePulses_BiasCurrent_KeyPress(object sender, KeyPressEventArgs e)
        {
            InputValidator.HandleKeyEvent(e, true, true);
        }

        private void txtGatePulses_DeviceID_KeyPress(object sender, KeyPressEventArgs e)
        {
            InputValidator.HandleKeyEvent(e, false, false);
        }

        private void btnIV_kOhm_CheckedChanged(object sender, EventArgs e)
        {

        }

        private void btnIV_mOhm_CheckedChanged(object sender, EventArgs e)
        {

        }

        private void txtIV_Resistance_TextChanged(object sender, EventArgs e)
        {

        }




        
    }
}

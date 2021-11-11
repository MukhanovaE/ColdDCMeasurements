using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using System.IO;
using Microsoft.Win32;
using System.Globalization;
using Microsoft.VisualBasic;

namespace ExperimentRunner
{
    public partial class Form1 : Form
    {
        private RunParams meas_params = new RunParams();

        // Device IDs
        private int nIDDeviceSweep, nIDDeviceFieldGate, nIDDeviceReadout, nIDLakeShore;
        private String strAMI;
        private int nGeneratorID;
        private int nLakeShoreModel;
        private double fCoilConstant;

        // Settings names in Windows registry
        private const String strSettingsTab = "ActiveTab";
        private const String strSampleName = "SampleName";
        private const String strStructureName = "StructureName";

        private const String strSweepDeviceID = "SourceSweep";
        private const String strFieldGateDeviceID = "SourceExcitation";
        private const String strLakeShoreID = "LakeShore";
        private const String strReadoutDeviceID = "SourceReadout";
        // private const String strFieldGateDeviceType = "FieldGateDevice";
        private const String strSweepDeviceType = "SweepDevice";
        private const String strReadoutDeviceType = "ReadoutDevice";
        private const String strAMIController = "AMI_controller";
        private const String strGeneratorID = "Signal_generator";
        private const String strLakeShoreModel = "LakeShoreModel";
        private const String strCoilConstant = "CoilConstant";

        private const String sShapiroStartPower = "Shapiro_power_start";
        private const String sShapiroEndPower = "Shapiro_power_end";
        private const String sShapiroStepPower = "Shapiro_power_step";
        private const String sShapiroFixedPower = "Shapiro_const_freq";
        private const String sShapiroStartFreq = "Shapiro_freq_start";
        private const String sShapiroEndFreq = "Shapiro_freq_end";
        private const String sShapiroStepFreq = "Shapiro_freq_step";
        private const String sShapiroFixedFreq = "Shapiro_const_power";
        private const String sShapiroSelected = "Shapiro_type";

        private const String sAMIUsed_IVB = "AMI_used_IVB";
        private const String sAMIUsed_VB = "AMI_used_VB";

        //Shapiro steps masurement sweep modes
        private const int SHAPIRO_POWER = 0;
        private const int SHAPIRO_FREQ = 1;

        private const String strError = "Error";

        //Maximum parameter values which are allowed
        private const double MAX_TEMP = 1.7; //K
        private const float MAX_FIELD = 60; //G, only for Yokogawa field control
        private const float MAX_CURR = 200; //mA
        private const float MAX_GATE = 4; //V
        private const float MAX_FREQ = 6; //GHz
        private const float MAX_POWER = 0; //dBm

        // Field sweep modes (for V-B measurement)
        private const String SWEEP_MODE_INCR = "0";
        private const String SWEEP_MODE_DECR = "1";
        private const String SWEEP_MODE_INCR_DECR = "2";
        private const String SWEEP_MODE_DECR_INCR = "3";
        private const String SWEEP_MODE_INCR_DECR_ONE_CURVE = "4";
        private const String SWEEP_MODE_DECR_INCR_ONE_CURVE = "5";

        //tabs numbers
        public const int tabIV = 0;
        public const int tabIVTAuto = 1;
        public const int tabIVB = 2;
        public const int tabVB = 3;
        public const int tabCritStats = 4;
        public const int tabRTCooldown = 5;
        public const int tabEquipmentSetup = 7;
        public const int tabRTHeat = 6;

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
            // float eps = 0.001F;

            if (fNew < fInitial && fStep>0)
            {
                MessageBox.Show(String.Format("Final temperature value {0} mK is less than a starter value {1} mK!", fNew*1000, fInitial),
                    strError, MessageBoxButtons.OK, MessageBoxIcon.Stop);
                return false;
            }
            /*if (fNew - eps > MAX_TEMP)
            {
                DialogResult ret = MessageBox.Show("Warning. a temperature is > 1.7K.\nYou are performing this measurement on your own risk.\nAreYouSure?",
                    strError, MessageBoxButtons.YesNo, MessageBoxIcon.Stop);
                return (ret == DialogResult.Yes);
            }*/
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

        private bool CheckField(float fRange, bool fYokogawa = true)
        {
            return true;
            /* if (!fYokogawa) return true;
            return CheckOneValue(Math.Abs(fRange), MAX_FIELD, "field", "G");  //negative fields are possible */
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
            return true; // CheckOneValue(freq, MAX_FREQ, "frequency", "GHz");
        }

        private bool CheckPower(float power)
        {
            return true; //  CheckOneValue(power, MAX_POWER, "power", "dBm");
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
                    return CheckField(fRange, btnIVB_Yokogawa.Checked);
                case tabVB: //U-B
                    fStart = RunParams.GetValueFromField(txtVB_FieldFrom);
                    fEnd = RunParams.GetValueFromField(txtVB_FieldTo);
                    fCurr1 = RunParams.GetValueFromField(txtVB_BiasStart);
                    fCurr2 = RunParams.GetValueFromField(txtVB_BiasEnd);
                    fCurr3 = RunParams.GetValueFromField(txtVB_BiasStep);
                    return CheckCurrents(new float[] { fCurr1, fCurr2, fCurr3 }) && CheckField(fStart, btnVB_Yokogawa.Checked) && CheckField(fEnd, btnVB_Yokogawa.Checked);
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

        private void SaveContactsSettings()
        {
            meas_params.SaveContactSettings();
        }

        private void InitContactsSettings()
        {
            meas_params.LoadContactSettings();
            int[] nConts = meas_params.ContactNumbers;
            txtContactsI1.Text = nConts[RunParams.CONTACT_I1].ToString();
            txtContactsI2.Text = nConts[RunParams.CONTACT_I2].ToString();
            txtContactsU1.Text = nConts[RunParams.CONTACT_V1].ToString();
            txtContactsU2.Text = nConts[RunParams.CONTACT_V2].ToString();
        }

        private void SaveAMISettings(int nTab)
        {
            Settings ss = new Settings();

            String sRequiredSetting = (nTab == tabIVB) ? sAMIUsed_IVB : sAMIUsed_VB;
            RadioButton btnRequired = (nTab == tabIVB) ? btnIVB_AMI : btnVB_AMI;

            ss.SaveSetting(sRequiredSetting, btnRequired.Checked ? 1:0);
        }


        private void SaveSettings()
        {
            NumberFormatInfo f = new NumberFormatInfo
            {
                NumberDecimalSeparator = "."
            };

            meas_params.FlushCurrentTabSettings(); //save currently active tab settings

            Settings sett = new Settings();
            int nCurrentTab = tabControl1.SelectedIndex;

            sett.SaveSetting(strSettingsTab, nCurrentTab);
            sett.SaveSetting(strSampleName, txtSampleName.Text);
            sett.SaveSetting(strStructureName, txtStructureName.Text);
            SaveContactsSettings();

            sett.SaveSetting(strSweepDeviceID, nIDDeviceSweep);
            sett.SaveSetting(strFieldGateDeviceID, nIDDeviceFieldGate);
            sett.SaveSetting(strLakeShoreID, nIDLakeShore);
            sett.SaveSetting(strReadoutDeviceID, nIDDeviceReadout);

            sett.SaveSetting(strAMIController, strAMI);
            sett.SaveSetting(strGeneratorID, nGeneratorID);
            sett.SaveSetting(strLakeShoreModel, nLakeShoreModel);
            sett.SaveSetting(strCoilConstant, fCoilConstant.ToString(f));
            
            // sett.SaveSetting(strFieldGateDevice, cboFieldGateDevice.SelectedIndex);
            sett.SaveSetting(strSweepDeviceType, cboCurrentSweepDeviceType.SelectedIndex);
            sett.SaveSetting(strReadoutDeviceType, cboReadoutDevice.SelectedIndex);

            // advanced settings for some tabs
            SaveAMISettings(nCurrentTab);
            
        }

        private void LoadSettings()
        {
            NumberFormatInfo f = new NumberFormatInfo
            {
                NumberDecimalSeparator = "."
            };
            Settings sett = new Settings();
            int nCurrentTab = 0;

            // Default values
            int settDevSweep = 3, settDevFieldGate = 6, settDevReadout = 9, settDevLakeShore = 17;
            int settSweepDeviceType = RunParams.EXCITATION_YOKOGAWA, settReadoutDeviceType = RunParams.READOUT_LEONARDO;
            int nLakeShoreModel = 0;

            String settAMI = txtAMIAddress.Text;
            int settGenID = 18;

            String strSampName="Sample 1";
            String strStructureNameSetting = "Structure 1";
            String sCoilConstant = "1";
            sett.TryLoadSetting(strSettingsTab, ref nCurrentTab); //default value is 0, so the first tab will be opened if there is no settings
            sett.TryLoadSetting(strSampleName, ref strSampName);
            sett.TryLoadSetting(strStructureName, ref strStructureNameSetting);

            sett.TryLoadSetting(strSweepDeviceID, ref settDevSweep);
            sett.TryLoadSetting(strFieldGateDeviceID, ref settDevFieldGate);
            sett.TryLoadSetting(strLakeShoreID, ref settDevLakeShore);
            sett.TryLoadSetting(strReadoutDeviceID, ref settDevReadout);

            sett.TryLoadSetting(strAMIController, ref settAMI);
            sett.TryLoadSetting(strGeneratorID, ref settGenID);
            sett.TryLoadSetting(strLakeShoreModel, ref nLakeShoreModel);

            sett.TryLoadSetting(strSweepDeviceType, ref settSweepDeviceType);
            sett.TryLoadSetting(strReadoutDeviceType, ref settReadoutDeviceType);
            sett.TryLoadSetting(strCoilConstant, ref sCoilConstant);

            nIDDeviceSweep = settDevSweep; nIDDeviceFieldGate = settDevFieldGate; nIDLakeShore = settDevLakeShore; nIDDeviceReadout = settDevReadout;
            strAMI = settAMI;
            nGeneratorID = settGenID;
            fCoilConstant = double.Parse(sCoilConstant, f);
            meas_params.SetEquipmentIDs(nIDDeviceSweep, nIDDeviceFieldGate, nIDLakeShore);
            meas_params.SetSweepDeviceType(settSweepDeviceType);
            meas_params.SetReadoutDeviceType(settReadoutDeviceType);
            meas_params.SetCoilConstant(fCoilConstant);

            txtFieldOrGateDevice.Text = nIDDeviceFieldGate.ToString();
            txtCurrentSweepDevice.Text = nIDDeviceSweep.ToString();
            txtLakeShoreID.Text = nIDLakeShore.ToString();
            txtVoltageReadout.Text = nIDDeviceReadout.ToString();

            txtAMIAddress.Text = strAMI;
            txtGeneratorID.Text = nGeneratorID.ToString();
            cboLakeShoreModel.SelectedIndex = nLakeShoreModel;

            cboCurrentSweepDeviceType.SelectedIndex = settSweepDeviceType;
            cboReadoutDevice.SelectedIndex = settReadoutDeviceType;
            cboFieldGateDevice.SelectedIndex = 0;
            txtCoilConstant.Text = sCoilConstant;

            tabControl1.SelectedIndex = nCurrentTab;
            txtSampleName.Text = strSampName;
            txtStructureName.Text = strStructureNameSetting;
            meas_params.SetSampleName(strSampName);
            InitContactsSettings();
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
            String strFieldType="";
            String sSweepType = "0";
            meas_params.SetAMI("");
            switch (nTab)
            {
                case tabIVTAuto: //I-V-T auto
                    strRead = "1";
                    if (sett.TryLoadSetting("I_V_T_auto_param0", ref strRead))
                    {
                        chkIVTA_FromCurrent.Checked = (strRead == "0");
                        txtIVTA_SweepFrom.Enabled = (strRead != "0");
                        txtIVTA_SweepFrom.Text = strRead;
                    }
                    strRead = "5";
                    if (sett.TryLoadSetting("I_V_T_auto_param1", ref strRead))
                    {
                        txtIVTA_SweepTo.Text = strRead;
                    }
                    strRead = "0.5";
                    if (sett.TryLoadSetting("I_V_T_auto_param2", ref strRead))
                    {
                        txtIVTA_SweepStep.Text = strRead;
                    }
                    strRead = "1";
                    if (sett.TryLoadSetting("I_V_T_auto_param3", ref strRead))
                    {
                        try
                        {
                            txtIVTA_OneCurveTimes.Value = Int32.Parse(strRead);
                        }
                        catch
                        {
                            txtIVTA_OneCurveTimes.Value = 1;
                        }
                    }
                    meas_params.SetParameters(txtIVTA_SweepFrom.Text, txtIVTA_SweepTo.Text, txtIVTA_SweepStep.Text, strRead);
                    break;
                case tabIVB: //I-V-B 
                    strRead = "40";
                    if (sett.TryLoadSetting("I_V_B_param0", ref strRead))
                    {
                        txtIVB_FieldRange.Text = strRead;
                    }
                    strRead = "1";
                    if (sett.TryLoadSetting("I_V_B_param1", ref strRead))
                    {
                        txtIVB_FieldStep.Text = strRead;
                    }
                    strFieldType = "Y";
                    if (sett.TryLoadSetting("I_V_B_param2", ref strRead))
                    {
                        strFieldType = strRead;
                    }
                    if (strFieldType == "Y")
                        btnIVB_Yokogawa.Checked = true;
                    else
                        btnIVB_AMI.Checked = true;
                    LoadAMISettings(tabIVB);
                    meas_params.SetAMI(btnIVB_AMI.Checked ? txtAMIAddress.Text : "");
                    meas_params.SetParameters(txtIVB_FieldRange.Text, txtIVB_FieldStep.Text);

                    break;
                case tabVB: //V-B 
                    if (sett.TryLoadSetting("V_B_param0", ref strRead))
                    {
                        txtVB_FieldFrom.Text = strRead;
                    }
                    if (sett.TryLoadSetting("V_B_param1", ref strRead))
                    {
                        txtVB_FieldTo.Text = strRead;
                    }
                    if (sett.TryLoadSetting("V_B_param2", ref strRead))
                    {
                        txtVB_FieldStep.Text = strRead;
                    }
                    if (sett.TryLoadSetting("V_B_param3", ref strRead))
                    {
                        txtVB_BiasStart.Text = strRead;
                    }
                    if (sett.TryLoadSetting("V_B_param4", ref strRead))
                    {
                        txtVB_BiasEnd.Text = strRead;
                    }
                    if (sett.TryLoadSetting("V_B_param5", ref strRead))
                    {
                        txtVB_BiasStep.Text = strRead;
                    }
                    if (sett.TryLoadSetting("V_B_param6", ref sSweepType))
                    {
                        switch (sSweepType)
                        {
                            case SWEEP_MODE_INCR:
                                btnVB_F.Checked = true;
                                break;
                            case SWEEP_MODE_DECR:
                                btnVB_R.Checked = true;
                                break;
                            case SWEEP_MODE_INCR_DECR:
                                btnVB_FR.Checked = true;
                                break;
                            case SWEEP_MODE_DECR_INCR:
                                btnVB_RF.Checked = true;
                                break;
                            case SWEEP_MODE_INCR_DECR_ONE_CURVE:
                                btnVB_FR_one.Checked = true;
                                break;
                            case SWEEP_MODE_DECR_INCR_ONE_CURVE:
                                btnVB_RF_one.Checked = true;
                                break;
                        }
                    }

                    meas_params.SetParameters(txtVB_FieldFrom.Text, txtVB_FieldTo.Text, txtVB_FieldStep.Text,
                        txtVB_BiasStart.Text, txtVB_BiasEnd.Text, txtVB_BiasStep.Text, sSweepType);
                    LoadAMISettings(tabVB);
                    meas_params.SetAMI(btnVB_AMI.Checked ? txtAMIAddress.Text : "");
                    break;

                case tabCritStats: //critical current distribution
                    if (sett.TryLoadSetting("I_V_crit_stats_param0", ref strRead))
                    {
                        txtStats_nCurves.Text = strRead;
                    }
                    meas_params.SetParameters(txtStats_nCurves.Text);
                    break;
                case tabRTCooldown: //R-T
                    if (sett.TryLoadSetting("R_T_param0", ref strRead))
                    {
                        txtRT_TempLimit.Text = strRead;
                        btnRT_MeasUntilTemperature.Checked = (strRead != "0");
                    }
                    meas_params.UpdateParameter(0, txtRT_TempLimit.Text);
                    if (sett.TryLoadSetting("R_T_param1", ref strRead))
                    {
                        txtRT_WaitTime.Text = strRead;
                    }
                    break;
                case tabRTHeat:
                    strRead = "5.2";
                    if (sett.TryLoadSetting("R_T_Heat_param0", ref strRead))
                    {
                        txtRTHeat_TempFrom.Text = strRead;
                    }
                    strRead = "9";
                    if (sett.TryLoadSetting("R_T_Heat_param1", ref strRead))
                    {
                        txtRTHeat_TempTo.Text = strRead;
                    }
                    strRead = "1";
                    if (sett.TryLoadSetting("R_T_Heat_param2", ref strRead))
                    {
                        SetRtHeatCurrentsList(strRead);
                    }
                    meas_params.SetParameters(txtRTHeat_TempFrom.Text, txtRTHeat_TempTo.Text, strRead);
                    break;
                   
            }
        }

        /*private String FieldToCurrent(String field)
        {
            NumberFormatInfo f = new NumberFormatInfo();
            f.NumberDecimalSeparator = ".";
            float fField = float.Parse(field, f);
            return (fField * 10).ToString();
        }
        */

        private String GetVBSweepType()
        {
            if (btnVB_F.Checked)
                return SWEEP_MODE_INCR;
            if (btnVB_R.Checked)
                return SWEEP_MODE_DECR;
            if (btnVB_FR.Checked)
                return SWEEP_MODE_INCR_DECR;
            if (btnVB_RF.Checked)
                return SWEEP_MODE_DECR_INCR;
            if (btnVB_FR_one.Checked)
                return SWEEP_MODE_INCR_DECR_ONE_CURVE;
            if (btnVB_RF_one.Checked)
                return SWEEP_MODE_DECR_INCR_ONE_CURVE;
            return SWEEP_MODE_INCR_DECR;
        }

        private void UpdateVBSweepMode()
        {
            if (!bFullInitialized)
                return;
            meas_params.UpdateParameter(6, GetVBSweepType());
        }

        private void btnVB_F_CheckedChanged(object sender, EventArgs e)
        {
            UpdateVBSweepMode();
        }

        private void btnVB_R_CheckedChanged(object sender, EventArgs e)
        {
            UpdateVBSweepMode();
        }

        private void btnVB_FR_CheckedChanged(object sender, EventArgs e)
        {
            UpdateVBSweepMode();
        }

        private void btnVB_RF_CheckedChanged(object sender, EventArgs e)
        {
            UpdateVBSweepMode();
        }

        private void btnVB_F_one_CheckedChanged(object sender, EventArgs e)
        {
            UpdateVBSweepMode();
        }

        private void btnVB_RF_one_CheckedChanged(object sender, EventArgs e)
        {
            UpdateVBSweepMode();
        }

        private String GetRtHeatCurrentsFromList()
        {
            return String.Join("!", lstRTHeatCurrents.Items.OfType<string>().ToArray());
        }

        private void SetRtHeatCurrentsList(String input_list)
        {
            lstRTHeatCurrents.Items.Clear();
            if (input_list.Length == 0)
                return;
            foreach (String i in input_list.Split('!'))
                lstRTHeatCurrents.Items.Add(i);
        }

        // Called when users switches a tab
        private void UpdateCurrentTab()
        {
            int i = tabControl1.SelectedIndex;
            //tabControl1.SelectedTab.
            int i_old = meas_params.CurrentTab;

            if (i_old == tabIVB || i_old==tabVB)
                SaveAMISettings(i_old);

            switch (i)
            {
                case tabIV: //I-V
                    meas_params.UpdateControls(i, btnIV_MkV, btnIV_mV, btnIV_nA, btnIV_mkA, btnIV_mA, txtIV_Resistance, btnIV_kOhm, btnIV_mOhm,
                        txtIV_Range, txtIV_Step, txtIV_RangeI, txtIV_StepI, txtIV_Gain, txtIV_Delay, txtIV_Samples);
                    break;
                case tabIVTAuto: //I-V-T auto
                    meas_params.UpdateControls(i, btnIVTA_mkV, btnIVTA_mV, btnIVTA_nA, btnIVTA_mkA, btnIVTA_mA, txtIVTA_Resistance, btnIVTA_KOhm, btnIVTA_MOhm,
                        txtIVTA_Range, txtIVTA_Step, txtIVTA_RangeI, txtIVTA_StepI, txtIVTA_Gain, txtIVTA_Delay, txtIVTA_Samples);
                    meas_params.SetParameters(txtIVTA_SweepFrom.Text, txtIVTA_SweepTo.Text, txtIVTA_SweepStep.Text, txtIVTA_OneCurveTimes.Value.ToString());
                    break;
                case tabIVB: //I-V-B 
                    meas_params.UpdateControls(i, btnIVB_mkV, btnIVB_mV, btnIVB_nA, btnIVB_mkA, btnIVB_mA, txtIVB_Resistance, btnIVB_KOhm, btnIVB_MOhm,
                        txtIVB_Range, txtIVB_Step, txtIVB_RangeI, txtIVB_StepI, txtIVB_Gain, txtIVB_Delay, txtIVB_Samples);
                    meas_params.SetParameters(txtIVB_FieldRange.Text, txtIVB_FieldStep.Text);  
                    break;
                case tabVB: //V-B 
                    meas_params.UpdateControls(i, btnVB_mkV, btnVB_mV, btnVB_nA, btnVB_mkA, btnVB_mA, txtVB_Resistance, btnVB_KOhm, btnVB_MOhm,
                        txtVB_Range, txtVB_Step, txtVB_RangeI, txtVB_StepI, txtVB_Gain, txtVB_Delay, txtVB_Samples);
                    meas_params.SetParameters(txtVB_FieldFrom.Text, txtVB_FieldTo.Text, txtVB_Step.Text,
                       txtVB_BiasStart.Text, txtVB_BiasEnd.Text, txtVB_BiasStep.Text, GetVBSweepType());
                    break;
                case tabCritStats: //critical current distribution
                    meas_params.UpdateControls(i, btnStats_mkV, btnStats_mV, btnStats_nA, btnStats_mkA, btnStats_mA, txtStats_Resistance, btnStats_KOhm, btnStats_MOhm,
                        txtStats_Range, txtStats_Step, txtStats_RangeI, txtStats_StepI, txtStats_Gain, txtStats_Delay, txtStats_Samples);
                    meas_params.SetParameters(txtStats_nCurves.Text);
                    break;
                case tabRTCooldown: //R-T
                    meas_params.UpdateControls(i, btnRT_mkV, btnRT_mV, btnRT_nA, btnRT_mkA, btnRT_mA, txtRT_Resistance, btnRT_KOhm, btnRT_MOhm,
                        txtRT_Range, txtRT_Step, txtRT_RangeI, txtRT_StepI, txtRT_Gain, txtRT_Delay, txtRT_Samples);
                    meas_params.SetParameters(txtRT_TempLimit.Text, txtRT_WaitTime.Text);
                    break;
                case tabRTHeat:
                    meas_params.UpdateControls(i, btnRTHeat_mkV, btnRTHeat_mV, btnRTHeat_nA, btnRTHeat_mkA, btnRTHeat_mA, txtRTHeat_Resistance, btnRTHeat_KOhm, btnRTHeat_MOhm,
                        txtRTHeat_Range, txtRTHeat_Step, txtRTHeat_RangeI, txtRTHeat_StepI, txtRTHeat_Gain, txtRTHeat_Delay, txtRTHeat_Samples);
                    meas_params.SetParameters(txtRTHeat_TempFrom.Text, txtRTHeat_TempTo.Text, GetRtHeatCurrentsFromList());
                    break;
                case tabEquipmentSetup:
                    meas_params.UpdateControls(i);
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

        private T HandleTextFieldChange<T>(TextBox field) where T: IComparable, IComparable<T>, IConvertible, IEquatable<T>, IFormattable
        {
            T nValue;
            CultureInfo myCIintl = new CultureInfo("en-US", false);
            try
            {
                nValue = (T)TypeDescriptor.GetConverter(typeof(T)).ConvertFromString(null, myCIintl, field.Text);  // convert to numeric type
                field.BackColor = SystemColors.Window;
                return nValue;
            }
            catch
            {
                field.BackColor = Color.Red;
                
                return (T)TypeDescriptor.GetConverter(typeof(T)).ConvertTo(-1, typeof(T)); //(object)(-1);
            }
        }

        private void txtCurrentSweepDevice_TextChanged(object sender, EventArgs e)
        {
            int nDevSweep = HandleTextFieldChange<int>(txtCurrentSweepDevice);
            if (nDevSweep != -1)
            {
                nIDDeviceSweep = nDevSweep;
                meas_params.SetIVSweepDeviceID(nDevSweep);
            }
        }

        private void txtExcitationDevice_TextChanged(object sender, EventArgs e)
        {
            nIDDeviceFieldGate = Int32.Parse(txtFieldOrGateDevice.Text);
            meas_params.SetGateOrFieldDeviceID(nIDDeviceFieldGate);
        }

        private void txtLakeShoreID_TextChanged(object sender, EventArgs e)
        {
            int nInput = HandleTextFieldChange<int>(txtLakeShoreID);
            if (nInput == -1) return;
            nIDLakeShore = nInput;
            meas_params.SetLakeShoreID(nIDLakeShore);
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

        private void txtAMIAddress_TextChanged(object sender, EventArgs e)
        {
            strAMI = txtAMIAddress.Text;
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
        private void UpdateAMIButton(int nCurrentTab)
        {
            RadioButton btnRequired = null;
            if (nCurrentTab == tabIVB)
                btnRequired = btnIVB_AMI;
            else if (nCurrentTab == tabVB)
                btnRequired = btnVB_AMI;
            //to be continued
            meas_params.SetAMI(btnRequired.Checked ? txtAMIAddress.Text : "");
        }

        private void btnIVB_Yokogawa_CheckedChanged(object sender, EventArgs e)
        {
            UpdateAMIButton(tabControl1.SelectedIndex);
        }

        private void btnIVB_AMI_CheckedChanged(object sender, EventArgs e)
        {
            UpdateAMIButton(tabControl1.SelectedIndex);
        }

        private void btnVB_AMI_CheckedChanged(object sender, EventArgs e)
        {
            UpdateAMIButton(tabControl1.SelectedIndex);
        }

        private void btnVB_Yokogawa_CheckedChanged(object sender, EventArgs e)
        {
            UpdateAMIButton(tabControl1.SelectedIndex);
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
            InputValidator.HandleKeyEvent(e, true, true);
        }

        private void txtVB_BiasEnd_KeyPress(object sender, KeyPressEventArgs e)
        {
            if (!bFullInitialized) return;
            InputValidator.HandleKeyEvent(e, true, true);
        }

        private void txtVB_BiasStep_KeyPress(object sender, KeyPressEventArgs e)
        {
            if (!bFullInitialized) return;
            InputValidator.HandleKeyEvent(e, true, false);
        }

        private void txtVB_FieldFrom_TextChanged(object sender, EventArgs e)
        {
            if (!bFullInitialized) return;
            meas_params.UpdateParameter(0, txtVB_FieldFrom.Text);
        }

        private void txtVB_FieldTo_TextChanged(object sender, EventArgs e)
        {
            meas_params.UpdateParameter(1, txtVB_FieldTo.Text);
        }

        private void txtVB_FieldStep_TextChanged(object sender, EventArgs e)
        {
            if (!bFullInitialized) return;
            meas_params.UpdateParameter(2, txtVB_FieldStep.Text);
        }

        private void txtVB_BiasStart_TextChanged(object sender, EventArgs e)
        {
            if (!bFullInitialized) return;
            meas_params.UpdateParameter(3, txtVB_BiasStart.Text);
        }

        private void txtVB_BiasEnd_TextChanged(object sender, EventArgs e)
        {
            if (!bFullInitialized) return;
            meas_params.UpdateParameter(4, txtVB_BiasEnd.Text);
        }

        private void txtVB_BiasStep_TextChanged(object sender, EventArgs e)
        {
            if (!bFullInitialized) return;
            meas_params.UpdateParameter(5, txtVB_BiasStep.Text);
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





        private void LoadAMISettings(int nTab)
        {
            Settings ss = new Settings();

            String sRequiredSetting = (nTab == tabIVB) ? sAMIUsed_IVB : sAMIUsed_VB;
            RadioButton btnRequired = (nTab == tabIVB) ? btnIVB_AMI : btnVB_AMI;

            int iAMIUSed = 0;

            if(ss.TryLoadSetting(sRequiredSetting, ref iAMIUSed))
                btnRequired.Checked = (iAMIUSed==1);
        }


         private void txtRT_TempLimit_KeyPress(object sender, KeyPressEventArgs e)
        {
            InputValidator.HandleKeyEvent(e, true, false);
        }

        private void txtRT_TempLimit_TextChanged(object sender, EventArgs e)
        {
            meas_params.UpdateParameter(0, txtRT_TempLimit.Text);
        }
        //
        

        
       


        private void btnStartTempObserver_Click(object sender, EventArgs e)
        {
            System.Diagnostics.Process.Start("python.exe", String.Format("Temperature.py -LT {0} -L {1}", nLakeShoreModel, txtLakeShoreID.Text));
        }

        private void txtIVTA_OneCurveTimes_KeyPress(object sender, KeyPressEventArgs e)
        {
            InputValidator.HandleKeyEvent(e, false, false);
        }

        private void TxtStats_Resistance_TextChanged(object sender, EventArgs e)
        {

        }

        private void CmdExploreData_Click(object sender, EventArgs e)
        {
            String strCurrDir = System.IO.Directory.GetCurrentDirectory();
            String strDataFolder = System.IO.Path.Combine(strCurrDir, "Data");
            System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo()
            {
                FileName = strDataFolder,
                UseShellExecute = true,
                Verb = "open"
            });
        }

        private void cboCurrentSweep_SelectedIndexChanged(object sender, EventArgs e)

        {
            int nSelected = cboCurrentSweepDeviceType.SelectedIndex;
            meas_params.SetSweepDeviceType(nSelected);

            //2400 devices must be selected in both lists or not selected in any of them
            /*if (nSelected == RunParams.EXCITATION_KEITHLEY_2400)
                cboReadoutDevice.SelectedIndex = RunParams.READOUT_KEITHLEY_2400;
            else
            { 
                if (cboReadoutDevice.SelectedIndex == RunParams.READOUT_KEITHLEY_2400)
                {
                    cboReadoutDevice.SelectedIndex = 0;
                }
            }*/
        }

        private void CboReadoutDevice_SelectedIndexChanged(object sender, EventArgs e)
        {
            int nSelected = cboReadoutDevice.SelectedIndex;
            meas_params.SetReadoutDeviceType(nSelected);

            // Readout device ID is meaningless if Leonardo is selected
            txtVoltageReadout.Enabled = (cboReadoutDevice.SelectedIndex != 0);

            //2400 devices must be selected in both lists  or not selected in any of them
            /*if (nSelected == RunParams.READOUT_KEITHLEY_2400)
                cboCurrentSweepDeviceType.SelectedIndex = RunParams.EXCITATION_KEITHLEY_2400;
            else
            { 
                if (cboCurrentSweepDeviceType.SelectedIndex == RunParams.EXCITATION_KEITHLEY_2400)
                {
                    cboCurrentSweepDeviceType.SelectedIndex = 0;
                }
            }*/
        }

        private void CboFieldGateDevice_SelectedIndexChanged(object sender, EventArgs e)
        {

        }

        private void TxtVoltageReadout_TextChanged(object sender, EventArgs e)
        {
            int nReadoutDevID = HandleTextFieldChange<int>(txtVoltageReadout);
            if (nReadoutDevID != -1)
            {
                meas_params.SetReadoutDeviceID(nReadoutDevID);
                nIDDeviceReadout = nReadoutDevID;
            }
        }

        private void Label104_Click(object sender, EventArgs e)
        {

        }

        private void TxtGeneratorID_TextChanged(object sender, EventArgs e)
        {
            int nGenID = HandleTextFieldChange<int>(txtGeneratorID);
            if (nGenID != -1) nGeneratorID = nGenID;
            if (!bFullInitialized)
                return;
            meas_params.UpdateParameter(5, txtGeneratorID.Text);
        }

        private void CboLakeShoreModel_SelectedIndexChanged(object sender, EventArgs e)
        {
            nLakeShoreModel = cboLakeShoreModel.SelectedIndex;
            meas_params.SetLakeShoreModel(nLakeShoreModel);
        }

        private void UpdateRTOption()
        {
            if (btnRT_MeasUntilEnd.Checked)
                meas_params.UpdateParameter(0, "0");
            else
                meas_params.UpdateParameter(0, txtRT_TempLimit.Text);
        }

        private void BtnRT_MeasUntilTemperature_CheckedChanged(object sender, EventArgs e)
        {
            UpdateRTOption();
        }

        private void BtnRT_MeasUntilEnd_CheckedChanged(object sender, EventArgs e)
        {
            UpdateRTOption();
        }

        private void TxtRT_WaitTime_KeyPress(object sender, KeyPressEventArgs e)
        {
            InputValidator.HandleKeyEvent(e, false, false);
        }

        private void TxtRT_WaitTime_TextChanged(object sender, EventArgs e)
        {
            meas_params.UpdateParameter(1, txtRT_WaitTime.Text);
        }


        private void TxtStructureName_TextChanged(object sender, EventArgs e)
        {
            meas_params.SetStructureName(txtStructureName.Text);
        }

        private void UpdateContact(int nc, TextBox field)
        {
            int number = HandleTextFieldChange<int>(field);
            if(number != -1) meas_params.SetContact(nc, number);
        }

        private void TxtContactsI1_KeyPress(object sender, KeyPressEventArgs e)
        {
            InputValidator.HandleKeyEvent(e, false, false);
        }

        private void TxtContactsI1_TextChanged(object sender, EventArgs e)
        {
            UpdateContact(RunParams.CONTACT_I1, txtContactsI1);
        }

        private void TxtContactsI2_KeyPress(object sender, KeyPressEventArgs e)
        {
            InputValidator.HandleKeyEvent(e, false, false);
        }

        private void TxtContactsI2_TextChanged(object sender, EventArgs e)
        {
            UpdateContact(RunParams.CONTACT_I2, txtContactsI2);
        }

        private void TxtContactsU1_KeyPress(object sender, KeyPressEventArgs e)
        {
            InputValidator.HandleKeyEvent(e, false, false);
        }

        private void TxtContactsU1_TextChanged(object sender, EventArgs e)
        {
            UpdateContact(RunParams.CONTACT_V1, txtContactsU1);
        }

        private void TxtContactsU2_KeyPress(object sender, KeyPressEventArgs e)
        {
            InputValidator.HandleKeyEvent(e, false, false);
        }

        private void TxtContactsU2_TextChanged(object sender, EventArgs e)
        {
            UpdateContact(RunParams.CONTACT_V2, txtContactsU2);
        }

        private void TxtCoilConstant_KeyPress(object sender, KeyPressEventArgs e)
        {
            InputValidator.HandleKeyEvent(e, true, true);
        }

        private void TxtCoilConstant_TextChanged(object sender, EventArgs e)
        {
            NumberFormatInfo f = new NumberFormatInfo
            {
                NumberDecimalSeparator = "."
            };
            try
            { 
                fCoilConstant = double.Parse(txtCoilConstant.Text, f);
                txtCoilConstant.BackColor = SystemColors.Window;
                meas_params.SetCoilConstant(fCoilConstant);
            }
            #pragma warning disable CS0168 // Переменная объявлена, но не используется
            catch(FormatException ex)
            #pragma warning restore CS0168 // Переменная объявлена, но не используется
            {
                txtCoilConstant.BackColor = RunParams.cError;
            }
        }

        private void TextBox3_TextChanged(object sender, EventArgs e)
        {

        }

        private void HandleRTHeatListChanged()
        {
            meas_params.UpdateParameter(2, GetRtHeatCurrentsFromList());
        }

        private void CmdRTHeatAddCurrent_Click(object sender, EventArgs e)
        {
            // ask user and add item
            double curr;
            String strInput = Interaction.InputBox("Enter current (in mkA)", "Add current");
            if (strInput.Length == 0)
                return;
            if (double.TryParse(strInput, out curr))
                lstRTHeatCurrents.Items.Add(strInput);
            else
                MessageBox.Show("Invalid value for current", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);

            // update experiment parameter
            HandleRTHeatListChanged();
        }

        private void CmdRTHeatRemove_Click(object sender, EventArgs e)
        {
            lstRTHeatCurrents.Items.RemoveAt(lstRTHeatCurrents.SelectedIndex);
            meas_params.UpdateParameter(2, GetRtHeatCurrentsFromList());
            HandleRTHeatListChanged();
        }

        private void TxtRTHeat_TempFrom_TextChanged(object sender, EventArgs e)
        {
            double dValue = HandleTextFieldChange<double>(txtRTHeat_TempFrom);  // check correctness
            meas_params.UpdateParameter(0, txtRTHeat_TempFrom.Text);
        }

        private void TextBox1_TextChanged(object sender, EventArgs e)
        {
            double dValue = HandleTextFieldChange<double>(txtRTHeat_TempTo);  // check correctness
            meas_params.UpdateParameter(1, txtRTHeat_TempTo.Text);
        }

        private void CmdRTHeat_Up_Click(object sender, EventArgs e)
        {
            int iSelected = lstRTHeatCurrents.SelectedIndex;
            String sSelected = lstRTHeatCurrents.SelectedItem.ToString();
            lstRTHeatCurrents.Items.Insert(iSelected - 1, sSelected);
            lstRTHeatCurrents.Items.RemoveAt(iSelected + 1);
            lstRTHeatCurrents.Focus();
            lstRTHeatCurrents.SelectedIndex = iSelected - 1;
            HandleRTHeatListChanged();
        }

        private void CmdRTHeat_Down_Click(object sender, EventArgs e)
        {
            int iSelected = lstRTHeatCurrents.SelectedIndex;
            String sSelected = lstRTHeatCurrents.SelectedItem.ToString();
            lstRTHeatCurrents.Items.Insert(iSelected + 2, sSelected);
            lstRTHeatCurrents.Items.RemoveAt(iSelected);
            lstRTHeatCurrents.Focus();
            lstRTHeatCurrents.SelectedIndex = iSelected + 1;
            HandleRTHeatListChanged();
        }

        private void LstRTHeatCurrents_SelectedIndexChanged(object sender, EventArgs e)
        {
            int idx = lstRTHeatCurrents.SelectedIndex;
            int nItems = lstRTHeatCurrents.Items.Count;
            cmdRTHeat_Up.Enabled = (idx != 0) || (idx == -1);
            cmdRTHeat_Down.Enabled = (idx != nItems - 1) || (idx == -1);
        }

        private void TxtRTHeat_TempFrom_KeyPress(object sender, KeyPressEventArgs e)
        {
            InputValidator.HandleKeyEvent(e, true, false);
        }

        private void TxtRTHeat_TempTo_KeyPress(object sender, KeyPressEventArgs e)
        {
            InputValidator.HandleKeyEvent(e, true, false);
        }

        private void TxtFieldOrGateDevice_TextChanged(object sender, EventArgs e)
        {
            int nFieldGateDevID = HandleTextFieldChange<int>(txtFieldOrGateDevice);
            if (nFieldGateDevID != -1)
            {
                meas_params.SetGateOrFieldDeviceID(nFieldGateDevID);
                nIDDeviceFieldGate = nFieldGateDevID;
            }
        }

        private void txtIVTA_OneCurveTimes_Leave(object sender, EventArgs e)
        {
            if (txtIVTA_OneCurveTimes.Value > 10)
            {
                txtIVTA_OneCurveTimes.Value = 10;
                System.Media.SystemSounds.Beep.Play();
            }
        }

        private void txtIVTA_OneCurveTimes_ValueChanged(object sender, EventArgs e)
        {
            meas_params.UpdateParameter(3, txtIVTA_OneCurveTimes.Value.ToString());
        }

    }
}

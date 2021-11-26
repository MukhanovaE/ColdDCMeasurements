using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using System.Globalization;
using System.Drawing;
using Microsoft.Win32;

namespace ExperimentRunner
{
    class RunParams
    {
        // excitation and readout device types
        // (corresponding to combo boxes element IDs on a form)
        public const int EXCITATION_YOKOGAWA = 0;
        public const int EXCITATION_KEITHLEY_6220 = 1;
        public const int EXCITATION_KEITHLEY_2400 = 2;

        public const int READOUT_LEONARDO = 0;
        public const int READOUT_KEITHLEY_2182 = 1;
        public const int READOUT_KEITHLEY_2400 = 2;

        public const int LAKESHORE_370 = 0;
        public const int LAKESHORE_335 = 1;

        public const int CONTACT_I1 = 0;
        public const int CONTACT_I2 = 1;
        public const int CONTACT_V1 = 2;
        public const int CONTACT_V2 = 3;

        //settings registry key names
        private const string strSettingsIUnits = "_I_units";
        private const string strSettingsVUnits = "_U_units";
        private const string strSettingsRUnits = "_R_units";
        private const string strSettingsResistance = "_Resistance";
        private const string strSettingsRange = "_VoltageRange";
        private const string strSettingsStep = "_VoltageStep";
        private const string strSettingsGain = "_VoltageGain";
        private const string strSettingsDelay = "_TimeStep";
        private const string strSettingsSamples = "_SamplesPerStep";
        private const String strContactNumbers = "ContactNumbers";

        //Color to mark fields with error values
        Color cError = Color.FromArgb(230, 0, 0);

        //Flag are we ready to do measurements, are entered values correct?
        public bool fCurrentsReady = true, fVoltagesReady = true, fResistanceReady = true;

        //Python script names (without .py extension)
        private String[] strScripts = new String[] { "I_V", "I_V_T_manual", "I_V_T_auto", "I_V_B", "V_B", "I_V_crit_stats", "R_T", "R_T_Gate", "I_V_Gate", 
            "I_V_Gate_T", "I_V_Gate_B", "I_V_Shapiro_power", "Gate_pulse" }; //fuck c# arrays initialization

        //public fields - references to controls
        public RadioButton btnmkV, btnmV, btnnA, btnmkA, btnmA;
        public TextBox txtResistance;
        public RadioButton btnMOhm, btnKOhm;
        public TextBox txtRange, txtStep, txtRangeI, txtStepI;
        public TextBox txtGain, txtDelay, txtSamples;

        //local info keepers
        private String strUnitI, strUnitR, strUnitU;
        private bool isFirstUpdate = true;
        private int nCurrentTab;
        private float fResistance;

        //Measurement parameters to be set with methods, manually
        private string strSampleName, strStructureName;
        private int [] nContactIDs = { 1, 1, 1, 1 };
        private int mIDDeviceSweep, mIDDeviceFieldOrGate, mIDLakeShore, mIDDeviceReadout;  //device IDs
        private int mSweepDeviceType, mReadDeviceType;  //device types
        private int mLakeShoreModel;
        private String mAMI;
        private bool fSaveData = true;
        private List<String> UserParams = new List<String>();

        //Gets a floating point value from a text box
        //Always uses "." as a decimal separator
        public static float GetValueFromField(TextBox field)
        {
            NumberFormatInfo f = new NumberFormatInfo();
            f.NumberDecimalSeparator = ".";

            return float.Parse(field.Text, f);
        }

        //Sets a floating point value to a text box
        //Always uses "." as a decimal separator
        public static void SetValueToField(TextBox field, float value)
        {
            NumberFormatInfo f = new NumberFormatInfo();
            f.NumberDecimalSeparator = ".";

            field.Text = value.ToString(f);
        }

        //Gets a resistance value from a number and units
        private float GetResistance(float R_text, String units)
        {
            Dictionary<String, float> measUnits = new Dictionary<String, float>
            {
                {"KOhm", 1000},
                {"MOhm", 1000000},
            };

            return R_text * measUnits[units];
        }

        //Convert voltage to current using values from text fields
        private float U_to_I(float U)
        {
            return (U / fResistance) * 1e+9f;
        }

        //Convert current to voltage using values from text fields
        private float I_to_U(float I)
        {
            return I * 1e-9f  * fResistance;
        }

        // Writes a selected resistance (in Ohms) to a class variable
        private void UpdateResistanceField()
        {
            try
            {
                float fResNow = GetValueFromField(txtResistance);
                fResistance = GetResistance(fResNow, strUnitR);
                if (!fResistanceReady)
                {
                    fResistanceReady = true;
                    txtResistance.BackColor = SystemColors.Window;
                }
            }
            catch
            {
                fResistanceReady = false;
                txtResistance.BackColor = cError;
            }
        }

        //Recounts current ranges from voltage ranges
        private void VoltageChanged()
        {
            try
            {
                float nVoltage = GetValueFromField(txtRange);
                float nStep = GetValueFromField(txtStep);

                float nCurrent = U_to_I(nVoltage);
                float nStepI = U_to_I(nStep);


                txtRangeI.TextChanged -= CurrentSweepHandler;
                txtStepI.TextChanged -= CurrentSweepHandler;

                SetValueToField(txtRangeI, nCurrent);
                SetValueToField(txtStepI, nStepI);

                txtRangeI.TextChanged += CurrentSweepHandler;
                txtStepI.TextChanged += CurrentSweepHandler;

                if (!fVoltagesReady)
                {
                    fVoltagesReady = true;
                    txtRange.BackColor = SystemColors.Window;
                    txtStep.BackColor = SystemColors.Window;
                }
            }
            catch
            {
                fVoltagesReady = false;
                txtRange.BackColor = cError;
                txtStep.BackColor = cError;
            }
        }

        //Recounts voltage ranges from current ranges
        private void CurrentChanged()
        {
            try
            {
                float nCurrent = GetValueFromField(txtRangeI);
                float nStepI = GetValueFromField(txtStepI);

                float nVoltage = I_to_U(nCurrent);
                float nStep = I_to_U(nStepI);


                txtRange.TextChanged -= VoltageSweepHandler;
                txtStep.TextChanged -= VoltageSweepHandler;

                SetValueToField(txtRange, nVoltage);
                SetValueToField(txtStep, nStep);

                txtRange.TextChanged += VoltageSweepHandler;
                txtStep.TextChanged += VoltageSweepHandler;

                if (!fCurrentsReady)
                {
                    fCurrentsReady = true;
                    txtRangeI.BackColor = SystemColors.Window;
                    txtStepI.BackColor = SystemColors.Window;
                }
            }
            catch
            {
                fCurrentsReady = false;
                txtRangeI.BackColor = cError;
                txtStepI.BackColor = cError;
            }
        }

        //values validating function
        private bool ValidateValues()
        {
            String sError = "Invalid input parameters";
            float voltageRange = GetValueFromField(txtRange);
            float voltageStep = GetValueFromField(txtStep);

            if (voltageRange > 32  && mSweepDeviceType == EXCITATION_YOKOGAWA)
            {
                // max 32 V: Yokogawa user manual, p. 2-4
                MessageBox.Show("Voltage range is set more than Yokogawa can give (32 V)", sError, MessageBoxButtons.OK, MessageBoxIcon.Error);
                return false;
            }

            if(voltageStep > voltageRange)
            {
                MessageBox.Show("Voltage step is bigger than voltage range", sError, MessageBoxButtons.OK, MessageBoxIcon.Error);
                return false;
            }
            return true;
        }

        //constructor
        public RunParams(string sample_name="")
        {
            strSampleName = sample_name;
        }

        //event handlers
        private void CurrentHandler(object sender, EventArgs e)
        {
            RadioButton btn = (RadioButton)sender;
            strUnitI = btn.Text;
        }

        private void VoltageHandler(object sender, EventArgs e)
        {
            RadioButton btn = (RadioButton)sender;
            strUnitU = btn.Text;
        }

        // handles resistance unit change (KOhms/MOhms)
        private void ResistanceHandler(object sender, EventArgs e)
        {
            RadioButton btn = (RadioButton)sender;
            strUnitR = btn.Text;
            UpdateResistanceField();
            VoltageChanged();
        }

        private void ResistanceTextboxHandler(object sender, EventArgs e)
        {
            UpdateResistanceField();
            VoltageChanged();  //recalculate U->I
        }

        //Event handlers for automatic I<->U range recalculation
        //sweep current fields edit handler
        private void CurrentSweepHandler(object sender, EventArgs e)
        {
            CurrentChanged();
        }

        //sweep voltage fields edit handler
        private void VoltageSweepHandler(object sender, EventArgs e)
        {
            VoltageChanged();
        }

        //Numeric text box edit handlers
        private void KeyPressWithDecimalsHandler(object sender, KeyPressEventArgs e)
        {
            InputValidator.HandleKeyEvent(e, true, true);
        }

        private void KeyPressWithoutDecimalsHandler(object sender, KeyPressEventArgs e)
        {
            InputValidator.HandleKeyEvent(e, false, false);
        }

        //local keepers updaters for first time
        private void UpdateUnitI()
        {
            if (btnmkA.Checked)
                strUnitI = "mkA";
            else if (btnmA.Checked)
                strUnitI = "mA";
            else
                strUnitI = "nA";
        }
        private void UpdateUnitU()
        {
            if (btnmkV.Checked)
                strUnitU = "mkV";
            else
                strUnitU = "mV";
        }
        private void UpdateUnitR()
        {
            if (btnMOhm.Checked)
                strUnitR = "MOhm";
            else
                strUnitR = "KOhm";
        }

        private void SaveCurrentTabSettings()
        {
            Settings sett = new Settings();
            if (nCurrentTab == Form1.tabEquipmentSetup)
                return;
            String strSettingName = strScripts[nCurrentTab];

            sett.SaveSetting(strSettingName + strSettingsIUnits, strUnitI);
            sett.SaveSetting(strSettingName + strSettingsVUnits, strUnitU);
            sett.SaveSetting(strSettingName + strSettingsRUnits, strUnitR);
            sett.SaveSetting(strSettingName + strSettingsResistance, txtResistance.Text);
            sett.SaveSetting(strSettingName + strSettingsRange, txtRange.Text);
            sett.SaveSetting(strSettingName + strSettingsStep, txtStep.Text);
            sett.SaveSetting(strSettingName + strSettingsGain, txtGain.Text);
            sett.SaveSetting(strSettingName + strSettingsDelay, txtDelay.Text);
            sett.SaveSetting(strSettingName + strSettingsSamples, txtSamples.Text);

            //save user-defined parameters
            
            for(int i=0; i<UserParams.Count; i++)
            {
                sett.SaveSetting(String.Format("{0}_param{1}", strSettingName, i), UserParams[i]);
            }
        }

        private void LoadCurrentTabSettings()
        {
            Settings sett = new Settings();
            String strSettingName = strScripts[nCurrentTab];
            String sRead = "";

            //Read radio button values
            if (sett.TryLoadSetting(strSettingName + strSettingsVUnits, ref sRead))
            {
                if (sRead.Equals("mV"))
                    btnmV.Checked = true;
                else
                    btnmkV.Checked = true;
                strUnitU = sRead;
            }
            else
                UpdateUnitU();
            //
            if (sett.TryLoadSetting(strSettingName + strSettingsIUnits, ref sRead))
            {
                if (sRead.Equals("nA"))
                    btnnA.Checked = true;
                else if (sRead.Equals("mA"))
                    btnmA.Checked = true;
                else
                    btnmkA.Checked = true;
                strUnitI = sRead;
            }
            else
                UpdateUnitI();
            //
            if (sett.TryLoadSetting(strSettingName + strSettingsRUnits, ref sRead))
            {
                if (sRead.Equals("KOhm"))
                    btnKOhm.Checked = true;
                else
                    btnMOhm.Checked = true;
                strUnitR = sRead;
            }
            else
                UpdateUnitR();

            //Read resistance value
            if (sett.TryLoadSetting(strSettingName + strSettingsResistance, ref sRead))
                txtResistance.Text = sRead;

            //Read range value
            if (sett.TryLoadSetting(strSettingName + strSettingsRange, ref sRead))
                txtRange.Text = sRead;

            //Read step value
            if (sett.TryLoadSetting(strSettingName + strSettingsStep, ref sRead))
                txtStep.Text = sRead;

            //Read gain value
            if (sett.TryLoadSetting(strSettingName + strSettingsGain, ref sRead))
                txtGain.Text = sRead;

            //Read time step value
            if (sett.TryLoadSetting(strSettingName + strSettingsDelay, ref sRead))
                txtDelay.Text = sRead;

            //Read time step value
            if (sett.TryLoadSetting(strSettingName + strSettingsSamples, ref sRead))
                txtSamples.Text = sRead;
        }

        //used for equipment settings tab
        public void UpdateControls(int N_tab)
        {
            if (!isFirstUpdate)
                SaveCurrentTabSettings();

            nCurrentTab = N_tab;
        }

        public void UpdateControls(int N_tab, RadioButton btnmkV_, RadioButton btnmV_, RadioButton btnnA_, RadioButton btnmkA_, RadioButton btnmA_,
            TextBox txtResistance_, RadioButton btnKOhm_, RadioButton btnMOhm_, TextBox txtRange_, TextBox txtStep_, TextBox txtRangeI_, TextBox txtStepI_,
                TextBox txtGain_, TextBox txtDelay_, TextBox txtSamples_)
        {
            if (!isFirstUpdate)
            {
                //remove old event handlers (if it is not a first call of this method)
                btnmkV.CheckedChanged -= VoltageHandler;
                btnmV.CheckedChanged -= VoltageHandler;
                btnnA.CheckedChanged -= CurrentHandler;
                btnmkA.CheckedChanged -= CurrentHandler;
                btnmA.CheckedChanged -= CurrentHandler;
                btnKOhm.CheckedChanged -= ResistanceHandler;
                btnMOhm.CheckedChanged -= ResistanceHandler;
                txtRange.TextChanged -= VoltageSweepHandler;
                txtStep.TextChanged -= VoltageSweepHandler;
                txtRangeI.TextChanged -= CurrentSweepHandler;
                txtStepI.TextChanged -= CurrentSweepHandler;
                txtResistance.TextChanged -= ResistanceTextboxHandler;
                txtResistance.KeyPress -= KeyPressWithDecimalsHandler;
                txtRange.KeyPress -= KeyPressWithDecimalsHandler;
                txtStep.KeyPress -= KeyPressWithDecimalsHandler;
                txtRangeI.KeyPress -= KeyPressWithDecimalsHandler;
                txtStepI.KeyPress -= KeyPressWithDecimalsHandler;
                txtGain.KeyPress -= KeyPressWithoutDecimalsHandler;
                txtDelay.KeyPress -= KeyPressWithDecimalsHandler;
                txtSamples.KeyPress -= KeyPressWithoutDecimalsHandler;

                //save current tab settings
                SaveCurrentTabSettings();

                //clear additional parameters from a previous tab
                UserParams.Clear();
            }

            //store a current tab number
            nCurrentTab = N_tab;

            //it is no more first update
            isFirstUpdate = false;

            //update controls references
            btnmkV = btnmkV_; btnmV = btnmV_; btnnA = btnnA_; btnmkA = btnmkA_; btnmA = btnmA_;
            txtResistance = txtResistance_;
            btnKOhm = btnKOhm_;
            btnMOhm = btnMOhm_;
            txtRange = txtRange_; txtStep = txtStep_;
            txtRangeI = txtRangeI_; txtStepI = txtStepI_;
            txtGain = txtGain_; txtDelay = txtDelay_; txtSamples = txtSamples_;

            //Load settings
            LoadCurrentTabSettings();

            //add event handlers
            btnmkV.CheckedChanged += VoltageHandler;
            btnmV.CheckedChanged += VoltageHandler;
            btnnA.CheckedChanged += CurrentHandler;
            btnmkA.CheckedChanged += CurrentHandler;
            btnmA.CheckedChanged += CurrentHandler;
            btnKOhm.CheckedChanged += ResistanceHandler;
            btnMOhm.CheckedChanged += ResistanceHandler;
            txtRange.TextChanged += VoltageSweepHandler;
            txtStep.TextChanged += VoltageSweepHandler;
            txtRangeI.TextChanged += CurrentSweepHandler;
            txtStepI.TextChanged += CurrentSweepHandler;
            txtResistance.TextChanged += ResistanceTextboxHandler;
            txtResistance.KeyPress += KeyPressWithDecimalsHandler;
            txtRange.KeyPress += KeyPressWithDecimalsHandler;
            txtStep.KeyPress += KeyPressWithDecimalsHandler;
            txtRangeI.KeyPress += KeyPressWithDecimalsHandler;
            txtStepI.KeyPress += KeyPressWithDecimalsHandler;
            txtGain.KeyPress += KeyPressWithoutDecimalsHandler;
            txtDelay.KeyPress += KeyPressWithDecimalsHandler;
            txtSamples.KeyPress += KeyPressWithoutDecimalsHandler;

            //Count current range from voltage ranges for a first time
            UpdateResistanceField();
            VoltageChanged();
        }

        public void StartMeasurement()
        {
            NumberFormatInfo f = new NumberFormatInfo
            {
                NumberDecimalSeparator = "."
            };

            if (!ValidateValues())
                return;
           
            String strCurrentScript = strScripts[nCurrentTab];

            String fResistance = txtResistance.Text;
            String fMaxVoltage = txtRange.Text;
            String fStep = txtStep.Text;
            String fGain = txtGain.Text;
            String fDelay = txtDelay.Text;
            String fSamples = txtSamples.Text;

            String strYokWrite = mAMI == "" ? mIDDeviceFieldOrGate.ToString() : mAMI;

            /*
                A Python script is started with the following arguments:
                -R_unit (e.g. MOhm)
                -V_unit (e.g. mkV)
                -I_unit (e.g. nA)
                -R VISA device ID for IV curve current sweep
                -W VISA device ID for field or gate control
                -L VISA device ID of LakeShore temperature controller
                -RR readout device VISA ID, ignored if Leonardo board is used
                -RT readout device type; 0 if Leonardo board, 1 if Keithley nanovoltmeter is used
                -WT IV curve current sweep device type, 0 if Yokogawa, 1 if Keithley
                -LT LakeShore model: 0 if 370, 1 if 335 (to be continued...)
                -C numbers of contacts (separated by comma)
                Resistance (in selected units)
                Voltage sweep range (in volts)
                Voltage sweep step (in volts)
                Voltage amplifier gain
                Sweep step delay (in seconds)
                Number of samples to measure and average at one point (only for Leonardo)
            */

            String strKwargs = String.Format("-{0} -{1} -{2} -R {3} -W {4} -L {5} -RT {6} -WT {7} -RR {8} -LT {9}", strUnitR, strUnitU, strUnitI, 
                mIDDeviceSweep, strYokWrite, mIDLakeShore, mReadDeviceType, mSweepDeviceType, mIDDeviceReadout, mLakeShoreModel);
            if (!fSaveData) strKwargs += " -nosave";

            if (UserParams.Count != 0)
                strKwargs += " -P '" + String.Join(";", UserParams) + "'";

            strKwargs += " -C " + String.Join(",", nContactIDs);
            strKwargs += " -ST \"" + strStructureName + "\"";

            String strCmdLine = String.Format(@"/k python.exe {0}.py {1} {2} {3} {4} {5} {6} {7}",
                strCurrentScript,
                    strKwargs,
                        fResistance, fMaxVoltage, fStep, fGain, fDelay, fSamples);

            if (strSampleName != "")
                strCmdLine += ' ' + strSampleName;

            //MessageBox.Show(strCmdLine); //for debugging on my home PC
            System.Diagnostics.Process.Start("cmd.exe", strCmdLine);
        }

        //force save current tab settings (not when it is switched to another)
        //for example, call this when a program closes
        public void FlushCurrentTabSettings()
        {
            SaveCurrentTabSettings();
        }

        //set new sample name (when it is changed)
        public void SetSampleName(string newName)
        {
            strSampleName = newName;
        }

        public void SetStructureName(string newName)
        {
            strStructureName = newName;
        }

        public void SetContact(int nContact, int nValue)
        {
            nContactIDs[nContact] = nValue;
        }

        //equipment parameters setters
        public void SetIVSweepDeviceID(int i)
        {
            mIDDeviceSweep = i;
        }

        public void SetGateOrFieldDeviceID(int i)
        {
            mIDDeviceFieldOrGate = i;
        }

        public void SetLakeShoreID(int i)
        {
            mIDLakeShore = i;
        }

        public void SetAMI(String s)
        {
            mAMI = s;
        }

        public void SetEquipmentIDs(int r, int w, int ls)
        {
            mIDDeviceSweep = r;
            mIDDeviceFieldOrGate = w;
            mIDLakeShore = ls;
        }

        public void SetReadoutDeviceID(int nID)
        {
            mIDDeviceReadout = nID;
        }

        public void SetLakeShoreModel(int nModel)
        {
            mLakeShoreModel = nModel;
        }

        public void SetReadoutDeviceType(int nType)
        {
            mReadDeviceType = nType;
        }

        public void SetSweepDeviceType(int nType)
        {
            mSweepDeviceType = nType;
        }

        public void SetSaveData(bool bSave)
        {
            fSaveData = bSave;
        }

        public bool IsReady()
        {
            return (fResistanceReady && fCurrentsReady && fVoltagesReady);
        }

        public void SetParameters(params String[] runParameters)
        {
            UserParams.Clear();
            foreach (String now in runParameters)
                UserParams.Add(now);
        }
        
        // Set additional user-defined parameters for this measurement
        public void SetParameters(params float[] runParameters)
        {
            UserParams.Clear();
            foreach (float now in runParameters)
                UserParams.Add(now.ToString());
        }

        // Updates additional user-defined parameters for this measurement
        public void UpdateParameter(int nParam, String newValue)
        {
            UserParams[nParam] = newValue;
        }

        public int CurrentTab
        {
            get
            {
                return nCurrentTab;
            }
        }

        public void SaveContactSettings()
        {

            Settings sett = new Settings();
            sett.SaveSetting(strContactNumbers, nContactIDs);
        }

        public void LoadContactSettings()
        {
            Settings sett = new Settings();
            if(!sett.TryLoadSetting(strContactNumbers, ref nContactIDs))
            {
                //set default values
                for (int i = 0; i < 4; i++)
                    nContactIDs[i] = i + 1;
            }
        }

        public int[] ContactNumbers
        {
            get
            {
                return nContactIDs;
            }
        }
    }  
}

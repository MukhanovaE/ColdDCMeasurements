using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using Microsoft.Win32;

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

        private const String strError = "Error";

        public Form1()
        {
            InitializeComponent();
        }

        private void button1_Click(object sender, EventArgs e)
        {
            this.Close();
        }

        private void cmdOK_Click(object sender, EventArgs e)
        {
            int nCurrentTab = tabControl1.SelectedIndex;
      
            if (nCurrentTab == tabControl1.TabCount - 1)
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
        }


        private void Form1_FormClosing(object sender, FormClosingEventArgs e)
        {
            SaveSettings();
        }

        private void UpdateCurrentTab()
        {
            int i = tabControl1.SelectedIndex;
            switch (i)
            {
                case 0: //I-V
                    meas_params.UpdateControls(i, btnIV_MkV, btnIV_mV, btnIV_nA, btnIV_mkA, btnIV_mA, txtIV_Resistance, btnIV_kOhm, btnIV_mOhm,
                        txtIV_Range, txtIV_Step, txtIV_RangeI, txtIV_StepI, txtIV_Gain, txtIV_Delay, txtIV_Samples);
                    break;
                case 1: //I-V-T manual
                    meas_params.UpdateControls(i, btnIVTM_mkV, btnIVTM_mV, btnIVTM_nA, btnIVTM_mkA, btnIVTM_mA, txtIVTM_Resistance, btnIVTM_KOhm, btnIVTM_MOhm,
                        txtIVTM_Range, txtIVTM_Step, txtIVTM_RangeI, txtIVTM_StepI, txtIVTM_Gain, txtIVTM_Delay, txtIVTM_Samples);
                    break;
                case 2: //I-V-T manual
                    meas_params.UpdateControls(i, btnIVTA_mkV, btnIVTA_mV, btnIVTA_nA, btnIVTA_mkA, btnIVTA_mA, txtIVTA_Resistance, btnIVTA_KOhm, btnIVTA_MOhm,
                        txtIVTA_Range, txtIVTA_Step, txtIVTA_RangeI, txtIVTA_StepI, txtIVTA_Gain, txtIVTA_Delay, txtIVTA_Samples);
                    break;
                case 3: //I-V-B 
                    meas_params.UpdateControls(i, btnIVB_mkV, btnIVB_mV, btnIVB_nA, btnIVB_mkA, btnIVB_mA, txtIVB_Resistance, btnIVB_KOhm, btnIVB_MOhm,
                        txtIVB_Range, txtIVB_Step, txtIVB_RangeI, txtIVB_StepI, txtIVB_Gain, txtIVB_Delay, txtIVB_Samples);
                    break;
                case 4: //V-B 
                    meas_params.UpdateControls(i, btnVB_mkV, btnVB_mV, btnVB_nA, btnVB_mkA, btnVB_mA, txtVB_Resistance, btnVB_KOhm, btnVB_MOhm,
                        txtVB_Range, txtVB_Step, txtVB_RangeI, txtVB_StepI, txtVB_Gain, txtVB_Delay, txtVB_Samples);
                    break;
                case 5: //V-B 
                    meas_params.UpdateControls(i, btnStats_mkV, btnStats_mV, btnStats_nA, btnStats_mkA, btnStats_mA, txtStats_Resistance, btnStats_KOhm, btnStats_MOhm,
                        txtStats_Range, txtStats_RangeI, txtStats_StepI, txtStats_Step, txtStats_Gain, txtStats_Delay, txtStats_Samples);
                    break;
                case 6: //R-T
                    meas_params.UpdateControls(i, btnRT_mkV, btnRT_mV, btnRT_nA, btnRT_mkA, btnRT_mA, txtRT_Resistance, btnRT_KOhm, btnRT_MOhm,
                        txtRT_Range, txtRT_Step, txtRT_RangeI, txtRT_StepI, txtRT_Gain, txtRT_Delay, txtRT_Samples);
                    break;
                case 7: //I-V with gate
                    meas_params.UpdateControls(i, btnGate_mkV, btnGate_mV, btnGate_nA, btnGate_mkA, btnGate_mA, txtGate_Resistance, btnGate_KOhm, btnGate_MOhm,
                        txtGate_Range, txtGate_Step, txtGate_RangeI, txtGate_StepI, txtGate_Gain, txtGate_Delay, txtGate_Samples);
                    break;
            }
        }

        private void tabControl1_SelectedIndexChanged(object sender, EventArgs e)
        {
            UpdateCurrentTab();
        }

        private void txtSampleName_TextChanged(object sender, EventArgs e)
        {
            meas_params.SetSampleName(txtSampleName.Text);
        }

        private void tabPage9_Click(object sender, EventArgs e)
        {

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

        private void chkSaveData_CheckedChanged(object sender, EventArgs e)
        {
            meas_params.SetSaveData(chkSaveData.Checked);
        }

         
    }
}

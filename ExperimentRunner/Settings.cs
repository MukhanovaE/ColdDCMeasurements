using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Microsoft.Win32;

namespace ExperimentRunner
{
    class Settings
    {
        private RegistryKey hkcu;
        private RegistryKey rk;
        private const string strSettingsKey = @"Software\LeonardoMeasurements";

        public Settings()
        {
           //Initialize registry keys
           hkcu = Registry.CurrentUser;
           rk = hkcu.CreateSubKey(strSettingsKey);
        }

        public bool TryLoadSetting(String setting, ref String strOutput)
        {
            try
            {
                String st = rk.GetValue(setting).ToString();
                strOutput = st;
                return true;
            }
            catch
            {
                //strOutput = "";
                return false;
            }
        }

        public bool TryLoadSetting(String setting, ref int strOutput)
        {
            try
            {
                int st = (int)rk.GetValue(setting);
                strOutput = st;
                return true;
            }
            catch
            {
                //strOutput = 0;
                return false;
            }
        }

        public bool SaveSetting(String setting, String val)
        {
            try
            {
                rk.SetValue(setting, val, RegistryValueKind.String);
                return true;
            }
            catch
            {
                return false;
            }
        }

        public bool SaveSetting(String setting, int val)
        {
            try
            {
                rk.SetValue(setting, val, RegistryValueKind.DWord);
                return true;
            }
            catch
            {
                return false;
            }
        }

        ~Settings()
        {
            //close keys to free resources and flush changed values
            rk.Close();
            hkcu.Close();
        }
    }
}

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

        public bool TryLoadSetting(String setting, ref int[] Output)
        {
            try
            {
                byte[] st = (byte[])rk.GetValue(setting);
                if (st is null)
                    return false;
                Buffer.BlockCopy(st, 0, Output, 0, st.Length);
                return true;
            }
            catch
            {
                //strOutput = 0;
                return false;
            }
        }

        public bool TryLoadSetting(String setting, ref String Output)
        {
            try
            {
                String st = rk.GetValue(setting).ToString();
                Output = st;
                return true;
            }
            catch
            {
                //strOutput = "";
                return false;
            }
        }

        public bool TryLoadSetting(String setting, ref int Output)
        {
            try
            {
                int st = (int)rk.GetValue(setting);
                Output = st;
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

        public bool SaveSetting(String setting, int [] val)
        {
            //try
            //{
            byte[] regData = new byte[val.Length * sizeof(int)];
            Buffer.BlockCopy(val, 0, regData, 0, regData.Length);
            rk.SetValue(setting, regData, RegistryValueKind.Binary);
            return true;
            /*}
            catch
            {
                return false;
            }*/
        }

        ~Settings()
        {
            //close keys to free resources and flush changed values
            rk.Close();
            hkcu.Close();
        }
    }
}

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Windows.Forms;

namespace ExperimentRunner
{
    class InputValidator
    {
        //Check if text box input is correct, and cancel a pressed key if it is not.
        public static void HandleKeyEvent(KeyPressEventArgs e, bool AllowDecimal = true, bool AllowE = false)
        {
            if (!((e.KeyChar >= '0' && e.KeyChar <= '9') || (e.KeyChar == '-') || (e.KeyChar == '.' && AllowDecimal) || (e.KeyChar == 'E' && AllowE) || char.IsControl(e.KeyChar)))
            {
                e.Handled = true;
                System.Media.SystemSounds.Beep.Play();
            }
        }
    }
}

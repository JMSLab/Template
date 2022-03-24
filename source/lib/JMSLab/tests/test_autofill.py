import sys

sys.path.append('./source/lib')

from unittest import main, TestCase
from JMSLab.autofill import GenerateAutofillMacros
from os.path import exists



class Test(TestCase):
    def test_file_exists(self):
        
        P_94 = 16.22
        Epsilon = - 1.19
        MarginalCost = (1 + 1 / Epsilon) * P_94
        autofill_outfile = r"output_macros.tex"
        
        GenerateAutofillMacros(["Epsilon", "MarginalCost"], "{:.2f}", autofill_outfile)
        self.assertTrue(exists(autofill_outfile))
        return

if __name__ == '__main__':
    main()


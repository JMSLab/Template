import sys

sys.path.append('./source/lib')

from unittest import main, TestCase
from JMSLab.autofill import GenerateAutofillMacros
from os.path import exists

P_94 = 16.22
Epsilon = - 1.19
MarginalCost = (1 + 1 / Epsilon) * P_94
SurplusGain = P_94 - MarginalCost

autofill_outfile = r"temp\output_macros.tex"

class Test(TestCase):
    def test_file_exists(self):
        GenerateAutofillMacros(["Epsilon", "MarginalCost"], "{:.2f}", autofill_outfile)
        self.assertTrue(exists(autofill_outfile))
        return

if __name__ == '__main__':
    main()


from unittest import main, TestCase
from os.path import exists

import tempfile, shutil 

from ..autofill import GenerateAutofillMacros

class Test(TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp() 
        self.outfile = self.tempdir + r"output_macros.tex"
        return None

    def tearDown(self):
        shutil.rmtree(self.tempdir)
        return

    def test_file_exists(self):
        Epsilon = -1.19
        
        GenerateAutofillMacros(["Epsilon"], autofill_outfile = self.outfile)
        self.assertTrue(exists(self.outfile))
        return None

    def test_exception(self):
        with self.assertRaises(Exception) as context:
            GenerateAutofillMacros(["Epsilon"], autofill_outfile =  self.outfile)

        self.assertTrue("Autofill: Variable 'Epsilon' not found" in str(context.exception))
        return None

    def test_output(self):
        Epsilon = - 1.19
        MarginalCost = 2.59
        
        GenerateAutofillMacros([["Epsilon"], ["MarginalCost"]], 
                               autofill_formats = ["{:.2f}", "\\textnormal{{{:.2f}}}"], 
                               autofill_outfile = self.outfile)
        tex_file = open(self.outfile, 'r')
        content = tex_file.read()
        self.assertEqual(content, "\\newcommand{\\Epsilon}{-1.19}\n\\newcommand{\\MarginalCost}{\\textnormal{2.59}}\n")
        tex_file.close()
        return None

    def test_list_format(self):
        Epsilon = - 1.19
        MarginalCost = 2.59

        with self.assertRaises(Exception) as context:
            GenerateAutofillMacros("Epsilon", autofill_outfile = self.outfile)

        self.assertTrue("Argument 'autofill_lists' must be list" in str(context.exception))

        with self.assertRaises(Exception) as context:
            GenerateAutofillMacros(["Epsilon"], autofill_formats = ["{:.2f}", "\\textnormal{{{:.2f}}}"], 
                                   autofill_outfile = self.outfile)

        self.assertTrue("Arguments 'autofill_lists' and 'autofill_formats' are incompatible" in str(context.exception))

        with self.assertRaises(Exception) as context:
            GenerateAutofillMacros([["Epsilon"], ["MarginalCost"]], autofill_outfile = self.outfile)

        self.assertTrue("Arguments 'autofill_lists' and 'autofill_formats' are incompatible" in str(context.exception))
        return None
        
if __name__ == '__main__':
    main()


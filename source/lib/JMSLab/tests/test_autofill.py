from unittest import main, TestCase
from ..autofill import GenerateAutofillMacros
from os.path import exists
import tempfile

class Test(TestCase):
    
    def test_file_exists(self):
        
        Epsilon = - 1.19
        MarginalCost = (1 + 1 / Epsilon) * 16.22
        with tempfile.TemporaryDirectory() as tempdir:
     
            autofill_outfile = tempdir + r"output_macros.tex"
        
            GenerateAutofillMacros(["Epsilon", "MarginalCost"], autofill_outfile)
            self.assertTrue(exists(autofill_outfile))
        return
    
    def test_exception(self):
        with tempfile.TemporaryDirectory() as tempdir:
            autofill_outfile = tempdir + r"output_macros.tex"
            with self.assertRaises(Exception) as context:
                GenerateAutofillMacros(["Epsilon"], autofill_outfile)

            self.assertTrue("Autofill: Variable 'Epsilon' not found" in str(context.exception))
        return
    
    def test_output(self):
        Epsilon = - 1.19
        with tempfile.TemporaryDirectory() as tempdir:
            autofill_outfile = tempdir + r"output_macros.tex"
        
            GenerateAutofillMacros(["Epsilon"], autofill_outfile)
            tex_file = open(autofill_outfile, 'r')
            content = tex_file.read()
            self.assertEqual(content, "\\newcommand{\\Epsilon}{-1.19}\n")
        return
    
    def test_list_format(self):
        Epsilon = - 1.19
        MarginalCost = (1 + 1 / Epsilon) * 16.22
        with tempfile.TemporaryDirectory() as tempdir:
     
            autofill_outfile = tempdir + r"output_macros.tex"
            
            with self.assertRaises(Exception) as context:
                GenerateAutofillMacros("Epsilon", autofill_outfile)

            self.assertTrue("Argument 'autofill_lists' must be list" in str(context.exception))
            
            with self.assertRaises(Exception) as context:
                GenerateAutofillMacros(["Epsilon"], autofill_outfile, ["{:.2f}", "\\textnormal{{{:.2f}}}"])

            self.assertTrue("Arguments 'autofill_lists' and 'autofill_formats' are incompatible" in str(context.exception))
            
            with self.assertRaises(Exception) as context:
                GenerateAutofillMacros([["Epsilon"], ["Marginal Cost"]], autofill_outfile)

            self.assertTrue("Arguments 'autofill_lists' and 'autofill_formats' are incompatible" in str(context.exception))
            return
        
if __name__ == '__main__':
    main()


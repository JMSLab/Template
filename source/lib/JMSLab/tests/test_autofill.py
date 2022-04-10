from unittest import main, TestCase
from ..autofill import GenerateAutofillMacros
from os.path import exists
import tempfile, shutil 

class Test(TestCase):
    
    def setUp(self):
        self.tempdir = tempfile.mkdtemp() 
        self.outfile = self.tempdir + r"output_macros.tex"
    
    def tearDown(self):
        shutil.rmtree(self.tempdir)
    
    def test_file_exists(self):
        Epsilon = - 1.19
        MarginalCost = (1 + 1 / Epsilon) * 16.22
        
        GenerateAutofillMacros(["Epsilon", "MarginalCost"], self.outfile)
        self.assertTrue(exists(self.outfile))
        return
    
    def test_exception(self):
        with self.assertRaises(Exception) as context:
            GenerateAutofillMacros(["Epsilon"], self.outfile)

        self.assertTrue("Autofill: Variable 'Epsilon' not found" in str(context.exception))
        return
    
    def test_output(self):
        Epsilon = - 1.19
       
        GenerateAutofillMacros(["Epsilon"], self.outfile)
        tex_file = open(self.outfile, 'r')
        content = tex_file.read()
        self.assertEqual(content, "\\newcommand{\\Epsilon}{-1.19}\n")
        tex_file.close()
        return
    
    def test_list_format(self):
        Epsilon = - 1.19
        MarginalCost = (1 + 1 / Epsilon) * 16.22
            
        with self.assertRaises(Exception) as context:
            GenerateAutofillMacros("Epsilon", self.outfile)

        self.assertTrue("Argument 'autofill_lists' must be list" in str(context.exception))
            
        with self.assertRaises(Exception) as context:
            GenerateAutofillMacros(["Epsilon"], self.outfile, ["{:.2f}", "\\textnormal{{{:.2f}}}"])

        self.assertTrue("Arguments 'autofill_lists' and 'autofill_formats' are incompatible" in str(context.exception))
            
        with self.assertRaises(Exception) as context:
            GenerateAutofillMacros([["Epsilon"], ["Marginal Cost"]], self.outfile)

        self.assertTrue("Arguments 'autofill_lists' and 'autofill_formats' are incompatible" in str(context.exception))
        return
        
if __name__ == '__main__':
    main()


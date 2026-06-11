from unittest import main, TestCase
from os.path import exists

import tempfile, shutil

from ..autofill import AutoFill

class Test(TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.outfile = self.tempdir + r"\output_macros.tex"
        return None

    def tearDown(self):
        shutil.rmtree(self.tempdir)
        return

    def test_file_exists(self):
        AutoFill({"Epsilon": -1.19}, outfile=self.outfile)
        self.assertTrue(exists(self.outfile))
        return None

    def test_dict_output(self):
        AutoFill({"Epsilon": -1.19, "MarginalCost": 2.59}, "{:.2f}", self.outfile)
        with open(self.outfile) as f:
            content = f.read()
        self.assertEqual(content, "\\newcommand{\\Epsilon}{-1.19}\n\\newcommand{\\MarginalCost}{2.59}\n")
        return None

    def test_list_output(self):
        Epsilon = -1.19
        AutoFill(["Epsilon"], "{:.2f}", self.outfile)
        with open(self.outfile) as f:
            content = f.read()
        self.assertEqual(content, "\\newcommand{\\Epsilon}{-1.19}\n")
        return None

    def test_list_variable_not_found(self):
        with self.assertRaises(Exception) as context:
            AutoFill(["Epsilon"], outfile=self.outfile)
        self.assertIn("AutoFill: Variable 'Epsilon' not found", str(context.exception))
        return None

    def test_invalid_macros_type(self):
        with self.assertRaises(Exception) as context:
            AutoFill("Epsilon", outfile=self.outfile)
        self.assertIn("Argument 'macros' must be a dict or list", str(context.exception))
        return None

    def test_text_mode(self):
        AutoFill({"MarginalCost": 2.59}, "{:.2f}", self.outfile, mode="text")
        with open(self.outfile) as f:
            content = f.read()
        self.assertEqual(content, "\\newcommand{\\MarginalCost}{\\textnormal{2.59}}\n")
        return None

    def test_none_format(self):
        AutoFill({"SampleStart": "January 2010"}, None, self.outfile)
        with open(self.outfile) as f:
            content = f.read()
        self.assertEqual(content, "\\newcommand{\\SampleStart}{January 2010}\n")
        return None

    def test_append(self):
        AutoFill({"Epsilon": -1.19}, "{:.2f}", self.outfile)
        AutoFill({"MarginalCost": 2.59}, "{:.2f}", self.outfile, append=True)
        with open(self.outfile) as f:
            content = f.read()
        self.assertEqual(content, "\\newcommand{\\Epsilon}{-1.19}\n\\newcommand{\\MarginalCost}{2.59}\n")
        return None

if __name__ == '__main__':
    main()

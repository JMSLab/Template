from unittest import main, TestCase
import os
import tempfile
import shutil
from pathlib import Path

from ..autofill import AutoFill


class TestOutputContent(TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.outfile = os.path.join(self.tempdir, "output_macros.tex")

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_dict_output(self):
        for outfile in [self.outfile, Path(self.outfile)]:
            AutoFill({"NegativePi": -3.1415, "Pi": 3.1415}, outfile, "{:.2f}")
            with open(outfile) as f:
                content = f.read()
            self.assertEqual(content, "\\newcommand{\\NegativePi}{-3.14}\n\\newcommand{\\Pi}{3.14}\n")

    def test_list_output(self):
        NegativePi = -3.1415
        Pi = 3.1415
        AutoFill(["NegativePi", "Pi"], self.outfile, "{:.2f}")
        with open(self.outfile) as f:
            content = f.read()
        self.assertEqual(content, "\\newcommand{\\NegativePi}{-3.14}\n\\newcommand{\\Pi}{3.1415}\n")

    def test_none_format_numeric(self):
        AutoFill({"NegativePi": -3.1415, "Pi": 3.1415}, self.outfile)
        with open(self.outfile) as f:
            content = f.read()
        self.assertEqual(content, "\\newcommand{\\NegativePi}{-3.1415}\n\\newcommand{\\Pi}{3.1415}\n")
    
    def test_none_format_text(self):
        AutoFill({"SampleStart": "January 2010"}, self.outfile)
        with open(self.outfile) as f:
            content = f.read()
        self.assertEqual(content, "\\newcommand{\\SampleStart}{January 2010}\n")


class TestModeAndFormat(TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.outfile = os.path.join(self.tempdir, "output_macros.tex")

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_text_mode(self):
        AutoFill({"Pi": 3.1415}, self.outfile, "{:.2f}", mode="text")
        with open(self.outfile) as f:
            content = f.read()
        self.assertEqual(content, "\\newcommand{\\Pi}{\\textnormal{3.14}}\n")

    def test_format_list(self):
        AutoFill({"NegativePi": -3.1415, "IntegerPi": 3.1415}, self.outfile, ["{:.2f}", "{:.0f}"])
        with open(self.outfile) as f:
            content = f.read()
        self.assertEqual(content, "\\newcommand{\\NegativePi}{-3.14}\n\\newcommand{\\IntegerPi}{3}\n")


class TestFileBehavior(TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.outfile = os.path.join(self.tempdir, "output_macros.tex")

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_append(self):
        AutoFill({"NegativePi": -3.1415}, self.outfile, "{:.2f}")
        AutoFill({"Pi": 3.1415}, self.outfile, "{:.2f}", append=True)
        with open(self.outfile) as f:
            content = f.read()
        self.assertEqual(content, "\\newcommand{\\NegativePi}{-3.14}\n\\newcommand{\\Pi}{3.14}\n")

    def test_overwrite_without_append(self):
        AutoFill({"NegativePi": -3.1415}, self.outfile, "{:.2f}")
        AutoFill({"Pi": 3.1415}, self.outfile, "{:.2f}")
        with open(self.outfile) as f:
            content = f.read()
        self.assertEqual(content, "\\newcommand{\\Pi}{3.14}\n")


class TestErrors(TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.outfile = os.path.join(self.tempdir, "output_macros.tex")

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_list_variable_not_found(self):
        with self.assertRaises(Exception) as context:
            AutoFill(["NegativePi"], outfile=self.outfile)
        self.assertIn("AutoFill: Variable 'NegativePi' not found", str(context.exception))

    def test_invalid_macros_type(self):
        with self.assertRaises(Exception) as context:
            AutoFill("NegativePi", outfile=self.outfile)
        self.assertIn("Argument 'macros' must be a dict or list", str(context.exception))


if __name__ == '__main__':
    main()

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
            AutoFill({"Epsilon": -1.19, "MarginalCost": 2.59}, outfile, "{:.2f}")
            with open(outfile) as f:
                content = f.read()
            self.assertEqual(content, "\\newcommand{\\Epsilon}{-1.19}\n\\newcommand{\\MarginalCost}{2.59}\n")

    def test_list_output(self):
        Epsilon = -1.19
        MarginalCost = 2.59
        AutoFill(["Epsilon", "MarginalCost"], self.outfile, "{:.2f}")
        with open(self.outfile) as f:
            content = f.read()
        self.assertEqual(content, "\\newcommand{\\Epsilon}{-1.19}\n\\newcommand{\\MarginalCost}{2.59}\n")

    def test_none_format(self):
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
        AutoFill({"MarginalCost": 2.59}, self.outfile, "{:.2f}", mode="text")
        with open(self.outfile) as f:
            content = f.read()
        self.assertEqual(content, "\\newcommand{\\MarginalCost}{\\textnormal{2.59}}\n")

    def test_format_list(self):
        AutoFill({"Epsilon": -1.19, "MarginalCost": 2.59}, self.outfile, ["{:.2f}", "{:.1f}"])
        with open(self.outfile) as f:
            content = f.read()
        self.assertEqual(content, "\\newcommand{\\Epsilon}{-1.19}\n\\newcommand{\\MarginalCost}{2.6}\n")


class TestFileBehavior(TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.outfile = os.path.join(self.tempdir, "output_macros.tex")

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_append(self):
        AutoFill({"Epsilon": -1.19}, self.outfile, "{:.2f}")
        AutoFill({"MarginalCost": 2.59}, self.outfile, "{:.2f}", append=True)
        with open(self.outfile) as f:
            content = f.read()
        self.assertEqual(content, "\\newcommand{\\Epsilon}{-1.19}\n\\newcommand{\\MarginalCost}{2.59}\n")

    def test_overwrite_without_append(self):
        AutoFill({"Epsilon": -1.19}, self.outfile, "{:.2f}")
        AutoFill({"MarginalCost": 2.59}, self.outfile, "{:.2f}")
        with open(self.outfile) as f:
            content = f.read()
        self.assertEqual(content, "\\newcommand{\\MarginalCost}{2.59}\n")


class TestErrors(TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.outfile = os.path.join(self.tempdir, "output_macros.tex")

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_list_variable_not_found(self):
        with self.assertRaises(Exception) as context:
            AutoFill(["Epsilon"], outfile=self.outfile)
        self.assertIn("AutoFill: Variable 'Epsilon' not found", str(context.exception))

    def test_invalid_macros_type(self):
        with self.assertRaises(Exception) as context:
            AutoFill("Epsilon", outfile=self.outfile)
        self.assertIn("Argument 'macros' must be a dict or list", str(context.exception))


if __name__ == '__main__':
    main()

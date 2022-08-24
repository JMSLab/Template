#! /usr/bin/env python

from unittest import mock
from pathlib import Path

import unittest
import shutil
import os

# Import testing helper modules
from . import _test_helpers as helpers
from . import _side_effects as fx

from ..builders.build_latex import build_latex, LatexBuilder
from .._exception_classes import ExecCallError

# Define path to the builder for use in patching
path = 'JMSLab.builders.build_latex'
subprocess_patch = mock.patch('%s.subprocess.check_output' % path)
system_patch = mock.patch('%s.os.system' % path)

# Run tests from test folder
TESTDIR = Path(__file__).resolve().parent
os.chdir(TESTDIR)


class TestBuildLateX(unittest.TestCase):

    def setUp(self):
        (TESTDIR / 'build').mkdir(exist_ok = True)

    @subprocess_patch
    def test_default(self, mock_check_output):
        '''
        Test that build_latex() behaves correctly when provided with
        standard inputs.
        '''
        mock_check_output.side_effect = fx.latex_side_effect
        target = 'build/latex.pdf'
        helpers.standard_test(self, build_latex, 'tex',
                              system_mock = mock_check_output,
                              source      = ['test_script.tex'],
                              target      = target,
                              nsyscalls   = 3)

        self.assertTrue(os.path.isfile(target))

    @subprocess_patch
    def test_list_arguments(self, mock_check_output):
        '''
        Check that build_latex() works when its source and target
        arguments are lists
        '''
        mock_check_output.side_effect = fx.latex_side_effect
        target = ['build/latex.pdf']
        helpers.standard_test(self, build_latex, 'tex',
                              system_mock = mock_check_output,
                              source      = ['test_script.tex'],
                              target      = target,
                              nsyscalls   = 3)
        self.assertTrue(os.path.isfile(target[0]))

    @subprocess_patch
    def test_bibtex_basic(self, mock_check_output):
        '''
        Check that build_latex() works when its source and target
        arguments are lists that include a .bib file and output
        '''
        mock_check_output.side_effect = fx.latex_side_effect
        target = ['build/latex.pdf', 'build/latex.log', 'build/latex.blg']
        source = ['test_script.tex', 'test_ref.bib']

        # Make sure check_bib works as expected
        builder_attributes = {'name': 'LaTeX', 'valid_extensions': ['.tex']}
        test_check_bib = LatexBuilder(target, source, {}, **builder_attributes)
        test_check_bib.check_bib(source)
        self.assertTrue(test_check_bib.checked_bib)

        helpers.standard_test(self, build_latex, 'tex',
                              system_mock = mock_check_output,
                              source      = source,
                              target      = target,
                              nsyscalls   = 4)

        for file in target:
            self.assertTrue(os.path.isfile(file))

    def test_bad_extension(self):
        '''Test that build_latex() recognises an improper file extension'''
        helpers.bad_extension(self, build_latex, good = 'test.tex')

    @system_patch
    def test_env_argument(self, mock_system):
        '''
        Test that numerous types of objects can be passed to
        build_latex() without affecting the function's operation.
        '''
        mock_system.side_effect = fx.latex_side_effect
        target = 'build/latex.pdf'
        source = ['input/latex_test_file.tex']

        for env in [True, [1, 2, 3], ('a', 'b'), None, TypeError]:
            with self.assertRaises(TypeError):
                build_latex(target, source, env = env)

    @system_patch
    def test_nonexistent_source(self, mock_system):
        '''
        Test build_latex()'s behaviour when the source file
        does not exist.
        '''
        mock_system.side_effect = fx.latex_side_effect
        # i) Directory doesn't exist
        with self.assertRaises(ExecCallError):
            build_latex('build/latex.pdf',
                        ['bad_dir/latex_test_file.tex'], env = {})
        # ii) Directory exists, but file doesn't
        with self.assertRaises(ExecCallError):
            build_latex('build/latex.pdf',
                        ['input/nonexistent_file.tex'], env = {})

    @system_patch
    def test_nonexistent_target_directory(self, mock_system):
        '''
        Test build_latex()'s behaviour when the target file's
        directory does not exist.
        '''
        mock_system.side_effect = fx.latex_side_effect
        with self.assertRaises(TypeError):
            build_latex('nonexistent_directory/latex.pdf',
                        ['input/latex_test_file.tex'], env = True)

    def tearDown(self):
        shutil.rmtree(TESTDIR / 'build')


if __name__ == '__main__':
    unittest.main()

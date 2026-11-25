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
shutil_patch = mock.patch('%s.shutil.copy2' % path)

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
        target = ['build/latex.pdf']
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

    @subprocess_patch
    def test_multibib(self, mock_check_output):
        """
        Check that build_latex() works correctly when
        the source '.tex' file contains multiple bibliographies.
        """

        mock_check_output.side_effect = fx.latex_side_effect
        target = ['build/latex.pdf']
        source = ['input/test_multibib.tex', 'input/test_ref.bib']
        env = {"multibib": True}

        # Make sure check_bib works as expected
        builder_attributes = {"name": "LaTeX", "valid_extensions": [".tex"]}
        test_check_bib = LatexBuilder(target, source, env, **builder_attributes)
        test_check_bib.check_bib(source)
        self.assertTrue(test_check_bib.checked_bib)

        # Make sure check_multibib works as expected
        test_check_multibib = LatexBuilder(target, source, env, **builder_attributes)
        test_check_multibib.check_multibib(target, env)
        self.assertTrue(test_check_multibib.checked_multibib)

        helpers.standard_test(self, build_latex, 'tex',
                            system_mock = mock_check_output,
                            source      = source,
                            target      = target,
                            env         = env,
                            nsyscalls   = 5)

        for file in target:
            self.assertTrue(os.path.isfile(file))

    @subprocess_patch
    def test_non_ascii_log(self, mock_check_output):
        '''
        Test that build_latex() keeps the bytes of a log with
        non-ASCII characters when adding timestamps.
        '''

        source   = ['test_script.tex']
        log_path = helpers.expected_log_path(source)
        
        for log_text in ['Log text: “quoted text”'.encode('utf-8'),
                         'café “quoted text”'.encode('cp1252')]:
            mock_check_output.side_effect = lambda *args, **kwargs: \
                fx.latex_side_effect(*args, log_text = log_text, **kwargs)
            build_latex(target = 'build/latex.pdf', source = source, env = {})

            with open(log_path, 'rb') as log_file:
                self.assertTrue(log_file.read().endswith(log_text))
            helpers.check_log(self, log_path, 'succeeded')

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

    def test_handout_nonunique_target(self):
        with self.assertRaises(ValueError):
            build_latex(target = ['path_to_clean.pdf', 'path_to_clean.pdf'], 
                        source = ['input/lyx_test_file.tex'],
                        env = {'HANDOUT_SFIX': '_clean'})

    def test_handout_suffix_mismatch(self):
        with self.assertRaises(ValueError):
            build_latex(target = ['path_to_clean.pdf', 'path_to_handout.pdf'], 
                        source = ['input/lyx_test_file.tex'],
                        env = {'HANDOUT_SFIX': '_'})

    def test_handout_missing_target(self):
        with self.assertRaises(ValueError):
            build_latex(target = ['path_to_clean.pdf'],
                        source = ['input/lyx_test_file.tex'],
                        env = {'HANDOUT_SFIX': '_'})

    @subprocess_patch
    def test_handout_option(self, mock_check_output):
        '''
        Test that build_latex() behaves correctly when provided with
        standard inputs.
        '''
        with shutil_patch as mock_shutil:
            mock_shutil.side_effect = fx.shutil_copy2_effect
            mock_check_output.side_effect = fx.latex_side_effect

            source = ['input/latex_test_file.tex']
            target = ['build/path_to_clean.pdf', 
                      'build/path_to_handout_.pdf',
                      'build/path_to_handout__.pdf']

            helpers.standard_test(self, build_latex, 'tex',
                                  system_mock = mock_check_output,
                                  source      = source,
                                  target      = target,
                                  env         = {'HANDOUT_SFIX': '_'},
                                  nsyscalls   = 6)

            self.assertTrue(os.path.isfile(target[0]))
            self.assertTrue(os.path.isfile(target[1]))
            self.assertTrue(os.path.isfile(target[2]))

    @subprocess_patch
    def test_handout_default(self, mock_check_output):

        with shutil_patch as mock_shutil:
            mock_shutil.side_effect = fx.shutil_copy2_effect
            mock_check_output.side_effect = fx.latex_side_effect

            target = ['build/path_to_clean.pdf', 
                      'build/path_to_handout_.pdf',
                      'build/path_to_handout__.pdf']
            source = ['input/latex_test_file.tex']

            helpers.standard_test(self, build_latex, 'latex',
                                  system_mock = mock_check_output,
                                  target = target,
                                  source = source, 
                                  nsyscalls = 6)

            self.assertTrue(os.path.isfile(target[0]))
            self.assertTrue(os.path.isfile(target[1]))
            self.assertTrue(os.path.isfile(target[2]))

    def test_jobname_backslash_target(self):
        '''
        Test that backslashes in the target path are passed to -jobname
        as forward slashes, since TeX reads backslashes as control sequences.
        '''
        builder_attributes = {'name': 'LaTeX',
                              'valid_extensions': ['.tex'],
                              'exec_opts': '-interaction nonstopmode -jobname'}
        builder = LatexBuilder([r'build\latex.pdf'], ['test_script.tex'], {},
                               **builder_attributes)

        self.assertIn('-jobname build/latex ', builder.system_call)
        self.assertNotIn('build\\latex', builder.system_call)

    def test_handout_jobname_backslash_target(self):
        '''
        Test that backslashes in the main target path are passed to the
        handout's -jobname as forward slashes.
        '''
        builder_attributes = {'name': 'LaTeX',
                              'valid_extensions': ['.tex'],
                              'exec_opts': '-interaction nonstopmode -jobname'}
        builder = LatexBuilder([r'build\path_to_clean.pdf'],
                               ['input/test_script.tex'], {},
                               **builder_attributes)
        builder.main_target = r'build\path_to_clean.pdf'
        builder.create_handout()
        os.remove(builder.handout_in)

        self.assertIn('-jobname build/path_to_clean ', builder.handout_call)
        self.assertNotIn('build\\path_to_clean', builder.handout_call)

    def tearDown(self):
        shutil.rmtree(TESTDIR / 'build')


if __name__ == '__main__':
    unittest.main()

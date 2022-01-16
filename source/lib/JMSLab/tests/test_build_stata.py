#! /usr/bin/env python

from unittest import mock
from pathlib import Path

import unittest
import shutil
import os

# Import testing helper modules
from . import _test_helpers as helpers
from . import _side_effects as fx

from ..builders.executables import get_executable
from ..builders.build_stata import build_stata
from .._exception_classes import PrerequisiteError, ExecCallError

STATA = get_executable('stata')

# Define path to the builder for use in patching
path = 'JMSLab.builders.build_stata'
subprocess_patch = mock.patch('%s.subprocess.check_output' % path)

# Run tests from test folder
TESTDIR = Path(__file__).resolve().parent
os.chdir(TESTDIR)


class TestBuildStata(unittest.TestCase):

    def setUp(self):
        (TESTDIR / 'build').mkdir(exist_ok = True)

    @helpers.platform_patch('darwin', path)
    @mock.patch('%s.misc.is_in_path' % path)
    @subprocess_patch
    def test_unix(self, mock_check_output, mock_path):
        '''Test build_stata()'s standard behaviour on Unix machines'''
        mock_check_output.side_effect = fx.make_stata_side_effect(STATA)
        # Mock is_in_path() to finds just one executable of Stata
        mock_path.side_effect  = fx.make_stata_path_effect(STATA)
        env = {'executable_names': {'stata': None}}
        helpers.standard_test(self, build_stata, 'do',
                              env = env, system_mock = mock_check_output)

    @helpers.platform_patch('win32', path)
    @mock.patch('%s.misc.is_in_path'    % path)
    @mock.patch('%s.misc.is_64_windows' % path)
    @subprocess_patch
    def test_windows(self, mock_check_output, mock_is_64, mock_path):
        '''
        Test that build_stata() behaves correctly on a Windows machine
        when given appropriate inputs.
        '''
        mock_check_output.side_effect = fx.make_stata_side_effect(STATA)
        mock_path.side_effect  = fx.make_stata_path_effect(STATA)
        mock_is_64.return_value = False

        env = {'executable_names': {'stata': None}}
        helpers.standard_test(self, build_stata, 'do',
                              env = env, system_mock = mock_check_output)

    @helpers.platform_patch('cygwin', path)
    @mock.patch('%s.misc.is_in_path' % path)
    @subprocess_patch
    def test_other_platform(self, mock_check_output, mock_path):
        '''
        Test build_stata()'s standard behaviour on a non-Unix,
        non-win32 machine.
        '''
        mock_check_output.side_effect = fx.make_stata_side_effect(STATA)
        mock_path.side_effect  = fx.make_stata_path_effect(STATA)

        # build_stata() will fail to define a command irrespective of
        # whether a stata is specified
        env = {'executable_names': {'stata': STATA.strip('"').strip("'")}}
        with self.assertRaises(PrerequisiteError):
            build_stata(target = 'test_output.txt',
                        source = 'test_script.do',
                        env    = env)

        env = {'executable_names': {'stata': None}}
        with self.assertRaises(PrerequisiteError):
            build_stata(target = 'test_output.txt',
                        source = 'test_script.do',
                        env    = env)

    @helpers.platform_patch('darwin', path)
    @subprocess_patch
    def test_stata_unix(self, mock_check_output):
        mock_check_output.side_effect = fx.make_stata_side_effect(STATA)
        env = {'executable_names': {'stata': STATA.strip('"').strip("'")}}
        helpers.standard_test(self, build_stata, 'do',
                              env = env, system_mock = mock_check_output)

    @helpers.platform_patch('win32', path)
    @subprocess_patch
    def test_stata_windows(self, mock_check_output):
        mock_check_output.side_effect = fx.make_stata_side_effect(STATA)

        env = {'executable_names': {'stata': STATA.strip('"').strip("'")}}
        helpers.standard_test(self, build_stata, 'do',
                              env = env, system_mock = mock_check_output)

    @subprocess_patch
    def test_cl_arg(self, mock_check_output):
        mock_check_output.side_effect = fx.make_stata_side_effect(STATA)

        env = {'executable_names': {'stata': None}}
        helpers.test_cl_args(self, build_stata,
                             mock_check_output, 'do',
                             env = env)
    @subprocess_patch
    def test_bad_stata_executable(self, mock_check_output):
        mock_check_output.side_effect = fx.make_stata_side_effect(recognized = True)
        env = {'executable_names': {'stata': 'bad_executable'}}
        with self.assertRaises(ExecCallError):
            build_stata(target = 'test_output.txt',
                        source = 'test_script.do',
                        env    = env)

    @mock.patch('%s.misc.is_in_path' % path)
    @subprocess_patch
    def test_no_executable_in_path(self, mock_check_output, mock_path):
        '''
        Test build_stata()'s behaviour when there are no valid Stata
        executables in the user's path variable
        '''
        # We mock the system to not find any executable in the path.
        mock_check_output.side_effect = fx.make_stata_side_effect('')
        mock_path.side_effect  = fx.make_stata_path_effect('')

        env = {'executable_names': {'stata': None}}
        with helpers.platform_patch('darwin', path), self.assertRaises(ExecCallError):
            build_stata(target = 'test_output.txt',
                        source = 'test_script.do',
                        env    = env)

        with helpers.platform_patch('win32', path), self.assertRaises(ExecCallError):
            build_stata(target = 'test_output.txt',
                        source = 'test_script.do',
                        env    = env)

    @subprocess_patch
    def test_unavailable_executable(self, mock_check_output):
        '''
        Test build_stata()'s behaviour when a Stata executable that
        isn't recognised is specified.
        '''
        mock_check_output.side_effect = fx.make_stata_side_effect('stata-mp')

        env = {'executable_names': {'stata': 'stata-se'}}
        with self.assertRaises(ExecCallError):
            build_stata(target = 'build/stata.dta',
                        source = 'input/test_script.do',
                        env    = env)

    @subprocess_patch
    def test_bad_extension(self, mock_check_output):
        mock_check_output.side_effect = fx.make_stata_side_effect(STATA)
        env = {'executable_names': {'stata': 'stata-mp'}}
        helpers.bad_extension(self, build_stata,
                              good = 'test.do', env = env)

    def tearDown(self):
        shutil.rmtree(TESTDIR / 'build')
        (TESTDIR / 'test_output.txt').unlink(missing_ok = True)


if __name__ == '__main__':
    unittest.main()

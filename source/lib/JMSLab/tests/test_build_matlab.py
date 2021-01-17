#! /usr/bin/env python

from pathlib import Path

import unittest
import shutil
import os
import re

# Import testing helper modules
from . import _test_helpers as helpers
from . import _side_effects as fx

from ..builders.executables import get_default_executables
from ..builders.build_matlab import build_matlab
from .._exception_classes import ExecCallError, PrerequisiteError

MATLAB = get_default_executables()['matlab']

# Define main test patch
path  = 'JMSLab.builders.build_matlab'
mock = unittest.mock

check_output_patch = mock.patch('%s.subprocess.check_output' % path)
copy_patch = mock.patch('%s.shutil.copy' % path)
main_patch = lambda f: check_output_patch(copy_patch(f))

# Run tests from test folder
TESTDIR = Path(__file__).resolve().parent
os.chdir(TESTDIR)


class TestBuildMatlab(unittest.TestCase):

    def setUp(self):
        (TESTDIR / 'build').mkdir(exist_ok = True)

    @helpers.platform_patch('darwin', path)
    @main_patch
    def test_unix(self, mock_copy, mock_check_output):
        '''
        Test that build_matlab() creates a log and properly submits
        a matlab system command on a Unix machine.
        '''
        # Mock copy so that it just creates the destination file
        mock_copy.side_effect = fx.matlab_copy_effect
        mock_check_output.side_effect = fx.make_matlab_side_effect(True)

        helpers.standard_test(self, build_matlab, 'm')
        self.check_call(mock_check_output, ['-nosplash', '-nodesktop'])

    def check_call(self, mock_check_output, options):
        '''
        Check that build_matlab() called Matlab correctly.
        mock_system should be the mock of os.system in build_matlab().
        '''
        # Extract the system command
        command = mock_check_output.call_args[0][0]
        # Look for the expected executable and options
        self.assertTrue(command.rfind(MATLAB) == 0 or re.search('^matlab', command))
        for option in options:
            self.assertIn(option, command.split(' '))

    @helpers.platform_patch('win32', path)
    @main_patch
    def test_windows(self, mock_copy, mock_check_output):
        '''
        Test that build_matlab() creates a log and properly submits
        a matlab system command on a Windows machine.
        '''
        mock_copy.side_effect = fx.matlab_copy_effect
        mock_check_output.side_effect = fx.make_matlab_side_effect(True)

        helpers.standard_test(self, build_matlab, 'm')
        self.check_call(mock_check_output, ['-nosplash', '-minimize', '-wait'])

    @helpers.platform_patch('riscos', path)
    @main_patch
    def test_other_os(self, mock_copy, mock_check_output):
        '''
        Test that build_matlab() raises an exception when run on a
        non-Unix, non-Windows operating system.
        '''
        mock_copy.side_effect = fx.matlab_copy_effect
        mock_check_output.side_effect = fx.make_matlab_side_effect(True)
        with self.assertRaises(PrerequisiteError):
            build_matlab(target = 'build/test.mat',
                         source = 'input/matlab_test_script.m',
                         env    = {})

    @main_patch
    def test_clarg(self, mock_copy, mock_check_output):
        '''
        Test that build_matlab() properly sets command-line arguments
        in its env argument as system environment variables.
        '''
        mock_copy.side_effect = fx.matlab_copy_effect
        mock_check_output.side_effect = fx.make_matlab_side_effect(True)

        env = {'CL_ARG': 'COMMANDLINE'}
        helpers.standard_test(self, build_matlab, 'm',
                              system_mock = mock_check_output, env = env)
        self.assertEqual(os.environ['CL_ARG'], env['CL_ARG'])

    def test_bad_extension(self):
        '''Test that build_matlab() recognises an improper file extension'''
        helpers.bad_extension(self, build_matlab, good = 'test.m')

    @main_patch
    def test_no_executable(self, mock_copy, mock_check_output):
        mock_copy.side_effect = fx.matlab_copy_effect
        mock_check_output.side_effect = \
            fx.make_matlab_side_effect(recognized = False)

        with self.assertRaises(ExecCallError):
            build_matlab(target = 'build/test.mat',
                         source = 'input/matlab_test_script.m',
                         env    = {})

    def tearDown(self):
        shutil.rmtree(TESTDIR / 'build')
        (TESTDIR / 'test_output.txt').unlink(missing_ok = True)


if __name__ == '__main__':
    unittest.main()

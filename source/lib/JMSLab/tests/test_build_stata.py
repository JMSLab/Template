#! /usr/bin/env python
import unittest
import sys
import os
import shutil
import mock
import subprocess
import re
# Import gslab_scons testing helper modules
import _test_helpers as helpers
import _side_effects as fx

# Ensure that Python can find and load the GSLab libraries
os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path.append('../..')

import gslab_scons as gs
from gslab_scons._exception_classes import ExecCallError, BadExtensionError
from gslab_make  import get_externals
from gslab_make.tests import nostderrout

# Define path to the builder for use in patching
path = 'gslab_scons.builders.build_stata'


class TestBuildStata(unittest.TestCase):

    def setUp(self):
        if not os.path.exists('./build/'):
            os.mkdir('./build/')

    @helpers.platform_patch('darwin', path)
    @mock.patch('%s.misc.is_in_path'         % path)
    @mock.patch('%s.subprocess.check_output' % path)
    def test_unix(self, mock_check, mock_path):
        '''Test build_stata()'s standard behaviour on Unix machines'''
        mock_check.side_effect = fx.make_stata_side_effect('stata-mp')
        # Mock is_in_path() to finds just one executable of Stata 
        mock_path.side_effect  = fx.make_stata_path_effect('stata-mp')
        env = {'stata_executable' : None}
        helpers.standard_test(self, gs.build_stata, 'do', 
                              env = env, system_mock = mock_check)


    @helpers.platform_patch('win32', path)
    @mock.patch('%s.misc.is_in_path'         % path)
    @mock.patch('%s.subprocess.check_output' % path)
    @mock.patch('%s.misc.is_64_windows'      % path)
    def test_windows(self, mock_is_64, mock_check, mock_path):
        '''
        Test that build_stata() behaves correctly on a Windows machine
        when given appropriate inputs. 
        '''
        mock_check.side_effect = fx.make_stata_side_effect('StataMP-64.exe')
        mock_path.side_effect  = fx.make_stata_path_effect('StataMP-64.exe')
        mock_is_64.return_value = False

        env = {'stata_executable' : None}
        helpers.standard_test(self, gs.build_stata, 'do', 
                              env = env, system_mock = mock_check)

    @helpers.platform_patch('cygwin', path)
    @mock.patch('%s.misc.is_in_path'         % path)
    @mock.patch('%s.subprocess.check_output' % path)
    def test_other_platform(self, mock_check, mock_path):
        '''
        Test build_stata()'s standard behaviour on a non-Unix,
        non-win32 machine.
        '''
        mock_check.side_effect = fx.make_stata_side_effect('stata-mp')
        mock_path.side_effect  = fx.make_stata_path_effect('stata-mp')

        # build_stata() will fail to define a command irrespective of
        # whether a stata_executable is specified
        env = {'stata_executable' : 'stata-mp'}
        with self.assertRaises(NameError):
            gs.build_stata(target = './test_output.txt', 
                           source = './test_script.do', 
                           env    = env)

        env = {'stata_executable' : None}
        with self.assertRaises(NameError):
            gs.build_stata(target = './test_output.txt', 
                           source = './test_script.do', 
                           env    = env)
    

    @helpers.platform_patch('darwin', path)
    @mock.patch('%s.subprocess.check_output' % path)
    def test_stata_executable_unix(self, mock_check):
        mock_check.side_effect = fx.make_stata_side_effect('stata-mp')
        env = {'stata_executable': 'stata-mp'}
        helpers.standard_test(self, gs.build_stata, 'do', 
                              env = env, system_mock = mock_check)

    @helpers.platform_patch('win32', path)
    @mock.patch('%s.subprocess.check_output' % path)
    def test_stata_executable_windows(self, mock_check):
        mock_check.side_effect = fx.make_stata_side_effect('stata-mp')

        env = {'stata_executable': 'stata-mp'}
        helpers.standard_test(self, gs.build_stata, 'do', 
                              env = env, system_mock = mock_check)

    @mock.patch('%s.subprocess.check_output' % path)
    def test_cl_arg(self, mock_check):
        mock_check.side_effect = fx.make_stata_side_effect('stata-mp')
        
        env = {'stata_executable' : None}
        helpers.test_cl_args(self, gs.build_stata, mock_check, 'do',
                             env = env)

    def test_bad_stata_executable(self):
        env = {'stata_executable': 'bad_stata_executable'}
        with self.assertRaises(ExecCallError):
            gs.build_stata(target = './test_output.txt', 
                           source = './test_script.do', 
                           env    = env)

    @mock.patch('%s.misc.is_in_path'         % path)
    @mock.patch('%s.subprocess.check_output' % path)
    def test_no_executable_in_path(self, mock_check, mock_path):
        '''
        Test build_stata()'s behaviour when there are no valid Stata
        executables in the user's path variable
        '''
        # We mock the system to not find any executable in the path.
        mock_check.side_effect = fx.make_stata_side_effect('')
        mock_path.side_effect  = fx.make_stata_path_effect('')

        env = {'stata_executable': None}
        with helpers.platform_patch('darwin', path), self.assertRaises(ExecCallError):
            gs.build_stata(target = './test_output.txt', 
                           source = './test_script.do', 
                           env    = env)

        with helpers.platform_patch('win32', path), self.assertRaises(ExecCallError):
            gs.build_stata(target = './test_output.txt', 
                           source = './test_script.do', 
                           env    = env)

    @mock.patch('%s.subprocess.check_output' % path)
    def test_unavailable_executable(self, mock_check):
        '''
        Test build_stata()'s behaviour when a Stata executable that 
        isn't recognised is specified. 
        '''
        mock_check.side_effect = fx.make_stata_side_effect('stata-mp')

        env = {'stata_executable' : 'stata-se'}
        with self.assertRaises(ExecCallError):
            gs.build_stata(target = './build/stata.dta', 
                           source = './input/stata_test_script.do', 
                           env    = env)

    @mock.patch('%s.subprocess.check_output' % path)
    def test_bad_extension(self, mock_check):
        mock_check.side_effect = fx.make_stata_side_effect('stata-mp')
        env = {'stata_executable': 'stata-mp'}
        helpers.bad_extension(self, gs.build_stata, 
                              good = 'test.do', env = env)

    def tearDown(self):
        if os.path.exists('./build/'):
            shutil.rmtree('./build/')
        if os.path.isfile('./test_output.txt'):
            os.remove('./test_output.txt')

if __name__ == '__main__':
    unittest.main()

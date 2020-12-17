#! /usr/bin/env python
import unittest
import sys
import os
import shutil
import mock
import re
# Import gslab_scons testing helper modules
import _test_helpers as helpers
import _side_effects as fx

# Ensure that Python can find and load the GSLab libraries
os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path.append('../..')

import gslab_scons as gs
from gslab_scons._exception_classes import (BadExtensionError,
                                            ExecCallError)
from gslab_make.tests import nostderrout

system_patch = mock.patch('gslab_scons.builders.build_r.subprocess.check_output')


class TestBuildR(unittest.TestCase):

    def setUp(self):
        if not os.path.exists('./build/'):
            os.mkdir('./build/')

    @system_patch
    def test_standard(self, mock_check_output):
        '''Test build_r()'s behaviour when given standard inputs.'''
        mock_check_output.side_effect = fx.make_r_side_effect(True)
        helpers.standard_test(self, gs.build_r, 'R', 
                              system_mock = mock_check_output)
        # With a list of targets
        targets = ['./test_output.txt']
        helpers.standard_test(self, gs.build_r, 'R', 
                              system_mock = mock_check_output,
                              target      = targets)    

    @system_patch
    def test_cl_arg(self, mock_check_output):
        mock_check_output.side_effect = fx.make_r_side_effect(True)
        helpers.test_cl_args(self, gs.build_r, mock_check_output, 'R')

    def test_bad_extension(self): 
        '''Test that build_r() recognises an inappropriate file extension'''
        helpers.bad_extension(self, gs.build_r, good = 'test.r')

    @system_patch
    def test_no_executable(self, mock_check_output):
        '''
        Check build_r()'s behaviour when R is not recognised as
        an executable.
        '''
        mock_check_output.side_effect = \
            fx.make_r_side_effect(recognized = False)
        with self.assertRaises(ExecCallError):
            helpers.standard_test(self, gs.build_r, 'R', 
                                  system_mock = mock_check_output)
   
    @system_patch
    def test_unintended_inputs(self, mock_check_output):
        # We expect build_r() to raise an error if its env
        # argument does not support indexing by strings. 
        mock_check_output.side_effect = fx.make_r_side_effect(True)

        check = lambda **kwargs: helpers.input_check(self, gs.build_r, 
                                                     'r', **kwargs)

        for bad_env in [True, (1, 2), TypeError]:
            check(env = bad_env, error = TypeError)
        
    def tearDown(self):
        if os.path.exists('./build/'):
            shutil.rmtree('./build/')
        if os.path.isfile('./test_output.txt'):
            os.remove('./test_output.txt')

if __name__ == '__main__':
    unittest.main()

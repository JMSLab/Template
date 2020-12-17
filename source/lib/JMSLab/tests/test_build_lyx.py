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

import gslab_scons.builders.build_lyx as gs
from gslab_scons._exception_classes import BadExtensionError, ExecCallError

# Define path to the builder for use in patching
path = 'gslab_scons.builders.build_lyx'


class TestBuildLyX(unittest.TestCase):

    def setUp(self):
        if not os.path.exists('./build/'):
            os.mkdir('./build/')

    @mock.patch('%s.subprocess.check_output' % path)
    def test_default(self, mock_system):
        '''
        Test that build_lyx() behaves correctly when provided with
        standard inputs. 
        '''
        mock_system.side_effect = fx.lyx_side_effect
        target = './build/lyx.pdf'
        helpers.standard_test(self, gs.build_lyx, 'lyx', 
                              system_mock = mock_system, 
                              target = target)
        self.assertTrue(os.path.isfile(target))

    @mock.patch('%s.subprocess.check_output' % path)
    def test_list_arguments(self, mock_system):
        '''
        Check that build_lyx() works when its source and target 
        arguments are lists
        '''
        mock_system.side_effect = fx.lyx_side_effect
        target = ['./build/lyx.pdf']
        helpers.standard_test(self, gs.build_lyx, 'lyx', 
                              system_mock = mock_system, 
                              source = ['./test_script.lyx'],
                              target = target)
        self.assertTrue(os.path.isfile(target[0]))

    def test_bad_extension(self):
        '''Test that build_lyx() recognises an improper file extension'''
        helpers.bad_extension(self, gs.build_lyx, good = 'test.lyx')
   
    @mock.patch('%s.os.system' % path)
    def test_env_argument(self, mock_system):
        '''
        Test that numerous types of objects can be passed to 
        build_lyx() without affecting the function's operation.
        '''
        mock_system.side_effect = fx.lyx_side_effect
        target = './build/lyx.pdf'
        source = ['./input/lyx_test_file.lyx']
        log    = './build/sconscript.log'
        
        for env in [True, [1, 2, 3], ('a', 'b'), None, TypeError]:
            with self.assertRaises(TypeError):
                gs.build_lyx(target, source, env = env)

    @mock.patch('%s.os.system' % path)
    def test_nonexistent_source(self, mock_system):
        '''
        Test build_lyx()'s behaviour when the source file
        does not exist.
        '''
        mock_system.side_effect = fx.lyx_side_effect
        # i) Directory doesn't exist
        with self.assertRaises(ExecCallError):
            gs.build_lyx('./build/lyx.pdf', 
                         ['./bad_dir/lyx_test_file.lyx'], env = {})
        # ii) Directory exists, but file doesn't
        with self.assertRaises(ExecCallError):
            gs.build_lyx('./build/lyx.pdf', 
                         ['./input/nonexistent_file.lyx'], env = {})   

    @mock.patch('%s.os.system' % path)
    def test_nonexistent_target_directory(self, mock_system):
        '''
        Test build_lyx()'s behaviour when the target file's
        directory does not exist.
        '''
        mock_system.side_effect = fx.lyx_side_effect
        with self.assertRaises(TypeError):
            gs.build_lyx('./nonexistent_directory/lyx.pdf', 
                         ['./input/lyx_test_file.lyx'], env = True)

    def tearDown(self):
        if os.path.exists('./build/'):
            shutil.rmtree('./build/')
       

if __name__ == '__main__':
    unittest.main()

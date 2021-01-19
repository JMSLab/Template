#! /usr/bin/env python

from unittest import mock
from pathlib import Path

import unittest
import shutil
import os

# Import testing helper modules
from . import _test_helpers as helpers
from . import _side_effects as fx

from ..builders.build_lyx import build_lyx
from .._exception_classes import ExecCallError

# Define path to the builder for use in patching
path = 'JMSLab.builders.build_lyx'
subprocess_patch = mock.patch('%s.subprocess.check_output' % path)
system_patch = mock.patch('%s.os.system' % path)

# Run tests from test folder
TESTDIR = Path(__file__).resolve().parent
os.chdir(TESTDIR)


class TestBuildLyX(unittest.TestCase):

    def setUp(self):
        (TESTDIR / 'build').mkdir(exist_ok = True)

    @subprocess_patch
    def test_default(self, mock_check_output):
        '''
        Test that build_lyx() behaves correctly when provided with
        standard inputs.
        '''
        mock_check_output.side_effect = fx.lyx_side_effect
        target = 'build/lyx.pdf'
        helpers.standard_test(self, build_lyx, 'lyx',
                              system_mock = mock_check_output,
                              target = target)
        self.assertTrue(os.path.isfile(target))

    @subprocess_patch
    def test_list_arguments(self, mock_check_output):
        '''
        Check that build_lyx() works when its source and target
        arguments are lists
        '''
        mock_check_output.side_effect = fx.lyx_side_effect
        target = ['build/lyx.pdf']
        helpers.standard_test(self, build_lyx, 'lyx',
                              system_mock = mock_check_output,
                              source = ['test_script.lyx'],
                              target = target)
        self.assertTrue(os.path.isfile(target[0]))

    def test_bad_extension(self):
        '''Test that build_lyx() recognises an improper file extension'''
        helpers.bad_extension(self, build_lyx, good = 'test.lyx')

    @system_patch
    def test_env_argument(self, mock_system):
        '''
        Test that numerous types of objects can be passed to
        build_lyx() without affecting the function's operation.
        '''
        mock_system.side_effect = fx.lyx_side_effect
        target = 'build/lyx.pdf'
        source = ['input/lyx_test_file.lyx']

        for env in [True, [1, 2, 3], ('a', 'b'), None, TypeError]:
            with self.assertRaises(TypeError):
                build_lyx(target, source, env = env)

    @system_patch
    def test_nonexistent_source(self, mock_system):
        '''
        Test build_lyx()'s behaviour when the source file
        does not exist.
        '''
        mock_system.side_effect = fx.lyx_side_effect
        # i) Directory doesn't exist
        with self.assertRaises(ExecCallError):
            build_lyx('build/lyx.pdf',
                      ['bad_dir/lyx_test_file.lyx'], env = {})
        # ii) Directory exists, but file doesn't
        with self.assertRaises(ExecCallError):
            build_lyx('build/lyx.pdf',
                      ['input/nonexistent_file.lyx'], env = {})

    @system_patch
    def test_nonexistent_target_directory(self, mock_system):
        '''
        Test build_lyx()'s behaviour when the target file's
        directory does not exist.
        '''
        mock_system.side_effect = fx.lyx_side_effect
        with self.assertRaises(TypeError):
            build_lyx('nonexistent_directory/lyx.pdf',
                      ['input/lyx_test_file.lyx'], env = True)

    def tearDown(self):
        shutil.rmtree(TESTDIR / 'build')


if __name__ == '__main__':
    unittest.main()

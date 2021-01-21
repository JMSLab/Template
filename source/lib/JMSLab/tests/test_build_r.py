#! /usr/bin/env python

from unittest import mock
from pathlib import Path

import unittest
import shutil
import os

# Import testing helper modules
from . import _test_helpers as helpers
from . import _side_effects as fx

from ..builders.build_r import build_r
from .._exception_classes import ExecCallError

path = 'JMSLab.builders.build_r'
subprocess_patch = mock.patch('%s.subprocess.check_output' % path)

# Run tests from test folder
TESTDIR = Path(__file__).resolve().parent
os.chdir(TESTDIR)


class TestBuildR(unittest.TestCase):

    def setUp(self):
        (TESTDIR / 'build').mkdir(exist_ok = True)

    @subprocess_patch
    def test_standard(self, mock_check_output):
        '''Test build_r()'s behaviour when given standard inputs.'''
        mock_check_output.side_effect = fx.make_r_side_effect(True)
        helpers.standard_test(self, build_r, 'R',
                              system_mock = mock_check_output)
        # With a list of targets
        targets = ['test_output.txt']
        helpers.standard_test(self, build_r, 'R',
                              system_mock = mock_check_output,
                              target      = targets)

    @subprocess_patch
    def test_cl_arg(self, mock_check_output):
        mock_check_output.side_effect = fx.make_r_side_effect(True)
        helpers.test_cl_args(self, build_r, mock_check_output, 'R')

    def test_bad_extension(self):
        '''Test that build_r() recognises an inappropriate file extension'''
        helpers.bad_extension(self, build_r, good = 'test.r')

    @subprocess_patch
    def test_no_executable(self, mock_check_output):
        '''
        Check build_r()'s behaviour when R is not recognised as
        an executable.
        '''
        mock_check_output.side_effect = \
            fx.make_r_side_effect(recognized = False)
        with self.assertRaises(ExecCallError):
            helpers.standard_test(self, build_r, 'R',
                                  system_mock = mock_check_output)

    @subprocess_patch
    def test_unintended_inputs(self, mock_check_output):
        # We expect build_r() to raise an error if its env
        # argument does not support indexing by strings.
        mock_check_output.side_effect = fx.make_r_side_effect(True)

        check = lambda **kwargs: helpers.input_check(self, build_r,
                                                     'r', **kwargs)

        for bad_env in [True, (1, 2), TypeError]:
            check(env = bad_env, error = TypeError)

    def tearDown(self):
        shutil.rmtree(TESTDIR / 'build')
        (TESTDIR / 'test_output.txt').unlink(missing_ok = True)


if __name__ == '__main__':
    unittest.main()

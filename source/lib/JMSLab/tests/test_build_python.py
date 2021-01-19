#! /usr/bin/env python

from unittest import mock
from pathlib import Path

import unittest
import shutil
import os

# Import testing helper modules
from . import _test_helpers as helpers
from . import _side_effects as fx

from ..builders.build_python import build_python
from .._exception_classes import BadExtensionError, ExecCallError

# Define path to the builder for use in patching
path = 'JMSLab.builders.build_python'
subprocess_patch = mock.patch('%s.subprocess.check_output' % path)

# Run tests from test folder
TESTDIR = Path(__file__).resolve().parent
os.chdir(TESTDIR)


class TestBuildPython(unittest.TestCase):

    def setUp(self):
        (TESTDIR / 'build').mkdir(exist_ok = True)

    @subprocess_patch
    def test_standard(self, mock_check_output):
        '''Test build_python()'s behaviour when given standard inputs.'''
        mock_check_output.side_effect = fx.python_side_effect
        helpers.standard_test(self, build_python, 'py',
                              system_mock = mock_check_output)

    def test_bad_extension(self):
        '''Test that build_python() recognises an improper file extension'''
        helpers.bad_extension(self, build_python, good = 'test.py')

    @subprocess_patch
    def test_cl_arg(self, mock_check_output):
        mock_check_output.side_effect = fx.python_side_effect
        helpers.test_cl_args(self, build_python, mock_check_output, 'py')

    @subprocess_patch
    def test_unintended_inputs(self, mock_check_output):
        '''
        Test that build_python() handles unintended inputs
        as expected.
        '''
        mock_check_output.side_effect = fx.python_side_effect
        check = lambda **kwargs: helpers.input_check(self, build_python,
                                                     'py', **kwargs)

        # env's class must support indexing by strings
        check(env = None,  error = TypeError)
        check(env = 'env', error = TypeError)

        test_source = ['test_script.py', 'nonexistent_data.txt']
        check(source = test_source, error = None)
        test_source.reverse()
        check(source = test_source, error = BadExtensionError)

    def test_nonexistent_input(self):
        '''
        Test build_python()'s behaviour when the source script doesn't exist.
        '''
        if os.path.exists('test.py'):
            os.remove('test.py')

        with self.assertRaises(ExecCallError):
            helpers.standard_test(self, build_python, source = 'test.py')

    def tearDown(self):
        shutil.rmtree(TESTDIR / 'build')
        (TESTDIR / 'test_output.txt').unlink(missing_ok = True)


if __name__ == '__main__':
    unittest.main()

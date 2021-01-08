#! /usr/bin/env python

from pathlib import Path

import unittest
import os
import re
import mock
import datetime

# Import testing helper modules
from .. import misc
from .._exception_classes import PrerequisiteError
from ..builders.executables import get_executables

STATA = get_executables()['stata']

# Define path to the builder for use in patching
path = 'JMSLab.misc'

# Run tests from test folder
TESTDIR = Path(__file__).resolve().parent
os.chdir(TESTDIR)


# This class is used for testing current_time()
class MockDateTime(datetime.datetime):
    @classmethod
    def now(cls):
        return cls(2017, 1, 20,
                   15,   2, 18,
                   133911)


class TestMisc(unittest.TestCase):
    def test_is_unix(self):
        '''
        Test that is_unix() returns True on Mac and Linux
        machines and False otherwise.
        '''
        platform_ref = '%s.sys.platform' % path
        with mock.patch(platform_ref, 'win32'):
            self.assertFalse(misc.is_unix())

        with mock.patch(platform_ref, 'darwin'):
            self.assertTrue(misc.is_unix())

        with mock.patch(platform_ref, 'linux'):
            self.assertTrue(misc.is_unix())

        with mock.patch(platform_ref, 'atheos'):
            self.assertFalse(misc.is_unix())

    def test_is_64_windows(self):
        '''
        Test that is_64_windows() returns True when PROGRAMFILES(X86)
        is a key in the system environment as accessed through
        os.environ.
        '''
        environ = '%s.os.environ' % path
        mocked_environ = {'PROGRAMFILES(X86)': 'C:/Program Files (x86)'}
        with mock.patch(environ, mocked_environ):
            self.assertTrue(misc.is_64_windows())
        with mock.patch(environ, dict()):
            self.assertFalse(misc.is_64_windows())

    @mock.patch('%s.os.environ' % path, {'PATH': '/bin:usrs/local'})
    @mock.patch('%s.os.pathsep' % path, ':')
    @mock.patch('%s.os.access' % path)
    def test_is_in_path(self, mock_access):
        '''
        Test that is_in_path() returns i) the full path of
        a recognised executable that the function takes as
        an argument and ii) False if the function's argument
        is not recognised as an executable.
        '''
        mock_access.side_effect = self.access_side_effect

        self.assertEqual(misc.is_in_path('stata'), '/bin/stata')
        self.assertFalse(misc.is_in_path('not_an_executable_file'))
        self.assertFalse(misc.is_in_path('stata-mp'))

    @staticmethod
    def access_side_effect(*args, **kwargs):
        '''
        This function mocks os.access by defining which
        files our mocked up machine can execute or
        otherwise access.
        '''
        # Define the files to which we have access
        # Total access
        execute_files = ['/bin/stata',
                         'executable_file']
        # Total access except execution
        other_files   = ['test_script.do']

        # Access the arguments of the os.access() call.
        path = args[0]
        mode = args[1]

        # If mode == os.X_OK, return True only for files with execute access
        if mode == os.X_OK and path in execute_files:
            result = True
        # For other modes return True if the file exists in our mocked set-up
        elif mode != os.X_OK and path in (execute_files + other_files):
            result = True
        # If the file doesn't "exist":
        else:
            result = False

        return result

    def test_make_list_if_string(self):
        self.assertEqual(misc.make_list_if_string(['test', 'test']), ['test', 'test'])
        self.assertEqual(misc.make_list_if_string('test'), ['test'])
        self.assertEqual(misc.make_list_if_string(['test']), ['test'])

        # We expect the function to raise Type Errors when it receives
        # inputs that are not strings or lists
        with self.assertRaises(TypeError):
            self.assertEqual(misc.make_list_if_string(1), 1)
        with self.assertRaises(TypeError):
            self.assertEqual(misc.make_list_if_string(None), None)

    @mock.patch('%s.datetime.datetime' % path, MockDateTime)
    def test_current_time(self):
        '''
        Test that current_time() prints the correct current time
        in the expected format. Here, the "correct current time"
        is a fixed value set within the MockDateTime class.
        '''
        the_time = misc.current_time()
        self.assertEqual('2017-01-20 15:02:18', the_time)

    def test_lyx_scan(self):
        # Open a test LyX file containing dependency statements
        infile = open(Path('input', 'lyx_test_dependencies.lyx'), 'r').read()
        # Mock an SCons node object to return this file's contents
        # when its get_contents() method is called.
        node   = mock.MagicMock(get_contents = lambda: infile)
        # Mock an SCons environment object with an EXTENSIONS data attribute
        env    = mock.MagicMock(EXTENSIONS = ['.lyx', '.txt'])
        output = misc.lyx_scan(node, env, None)
        # Ensure lyx_scan scanned the test file correctly
        self.assertEqual(output, ['lyx_test_file.lyx', 'tables_appendix.txt'])

    @mock.patch('%s.os.path.expanduser' % path)
    @mock.patch('%s.os.path.isdir' % path)
    def test_check_and_expand_path(self, mock_is_dir, mock_expanduser):
        mock_expanduser.side_effect = lambda x: re.sub('~', 'Users/lb', x)
        mock_is_dir.side_effect     = lambda x: x == 'Users/lb/cache'

        misc.check_and_expand_path('~/cache')
        misc.check_and_expand_path('Users/lb/cache')
        with self.assertRaises(PrerequisiteError):
            misc.check_and_expand_path('~/~/cache')
        with self.assertRaises(PrerequisiteError):
            misc.check_and_expand_path('lb/cache')
        with self.assertRaises(PrerequisiteError):
            misc.check_and_expand_path(3)


if __name__ == '__main__':
    unittest.main()

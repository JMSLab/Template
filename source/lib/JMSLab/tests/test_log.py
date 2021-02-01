#! /usr/bin/env python

from unittest import mock
from pathlib import Path

import unittest
import sys
import os
import re

# Import testing helper modules
from .. import log
from . import _test_helpers as helpers

# Define path to the builder for use in patching
path = 'JMSLab.log'

# Run tests from test folder
TESTDIR = Path(__file__).resolve().parent
os.chdir(TESTDIR)


class TestLog(unittest.TestCase):

    def setUp(self):
        (TESTDIR / 'sconstruct.log').unlink(missing_ok = True)

    def test_start_log_stdout_on_unix(self):
        '''
        Test that start_log() leads stdout to be captured in
        a log file on Unix machines.
        '''
        if log.misc.is_unix():
            # Save the initial standard output
            initial_stdout = sys.stdout
            test = "Test message"
            # Call start_log(), which redirects standard output to a log
            log.start_log(mode = 'develop')
            print(test)
            sys.stdout.close()

            # Restore the initial standard output
            sys.stdout = initial_stdout

            # Ensure that start_log() actually redirected standard output
            # to a log at the expected path.
            with open('sconstruct.log', 'r') as f:
                log_contents = f.read()

                message_match = r'^\*\*\* New build: \{[0-9\s\-:]+\} \*\*\*\n%s$' % test
                self.assertTrue(re.search(message_match, log_contents.strip()))

    @mock.patch('%s.os.popen' % path)
    @mock.patch('%s.open' % path)
    def test_start_log_popen_on_unix(self, mock_open, mock_popen):
        '''
        Test that start_log() uses popen() to initialise its log
        on Unix machines.
        '''
        if log.misc.is_unix():
            log.start_log(mode = 'develop')
            mock_popen.assert_called_with('tee -a sconstruct.log', 'w')
            log.start_log(mode = 'develop', log = 'test_log.txt')
            mock_popen.assert_called_with('tee -a test_log.txt', 'w')

    # Set the platform to Windows
    @helpers.platform_patch('win32', '%s.misc' % path)
    def test_start_log_stdout_on_windows(self):
        '''
        Test that start_log() leads stdout to be captured in
        a log file on Windows machines.
        '''
        initial_stdout = sys.stdout
        test = "Test message"

        log.start_log(mode = 'develop')
        print(test)
        sys.stdout.close()
        sys.stdout = initial_stdout

        with open('sconstruct.log', 'r') as f:
            log_contents = f.read()

        message_match = r'^\*\*\* New build: \{[0-9\s\-:]+\} \*\*\*\n%s$' % test
        self.assertTrue(re.search(message_match, log_contents.strip()))

    @helpers.platform_patch('win32', '%s.misc' % path)
    @mock.patch('%s.os.popen' % path)
    @mock.patch('%s.open' % path)
    def test_start_log_open_on_windows(self, mock_open, mock_popen):
        '''
        Test that start_log() uses open() to initialise its log
        on Windows machines.
        '''
        log.start_log(mode = 'develop')
        mock_open.assert_called_with('sconstruct.log', 'a')
        log.start_log(mode = 'develop', log = 'test_log.txt')
        mock_open.assert_called_with('test_log.txt', 'a')

        mock_popen.assert_not_called()

    @helpers.platform_patch('cygwin', '%s.misc' % path)
    def test_start_log_other_os(self):
        '''
        Test start_log()'s behaviour when run on a platform other
        than Windows, Darwin, or Linux.
        (We don't expect it to change sys.stdout, but we expect it
        to set sys.stderr to sys.stdout.)
        '''
        # initial_stderr = sys.stderr
        initial_stdout = sys.stdout
        log.start_log(mode = 'develop')
        self.assertEqual(initial_stdout, sys.stderr)
        self.assertEqual(initial_stdout, sys.stdout)

        test_file  = mock.MagicMock()
        sys.stdout = test_file
        log.start_log(mode = 'develop')
        self.assertEqual(sys.stderr, test_file)

    @helpers.platform_patch('darwin', '%s.misc' % path)
    def test_invalid_mode(self):
        '''Check behaviour when mode argument is invalid'''
        with self.assertRaises(Exception):
            log.start_log(mode = [1, 2, 3])

        with self.assertRaises(Exception):
            log.start_log(mode = None)

    @helpers.platform_patch('darwin', '%s.misc' % path)
    def test_start_log_nonstring_input(self):
        '''
        Test start_log()'s behaviour when its log argument is
        not a string.

        Note: Previous tests had 1 and True, both of which
        Python tries to evaluate as file descriptors. This
        ended up messing up Python and the test. See

            https://docs.python.org/3/library/os.html#file-descriptor-operations
        '''
        # initial_stdout = sys.stdout
        with self.assertRaises(TypeError):
            log.start_log(mode = 'develop', log = 1.0)

        with self.assertRaises(TypeError):
            log.start_log(mode = 'develop', log = {})

        with self.assertRaises(TypeError):
            log.start_log(mode = 'develop', log = [1, 2, 3])

    def check_log_creation(self, log_names, initial_stdout):
        sys.stdout.close()
        if isinstance(log_names, str):
            log_names = [log_names]
        for logfile in log_names:
            self.assertTrue(os.path.isfile(logfile))
            os.remove(logfile)
        sys.stdout = initial_stdout

    @mock.patch('%s.misc.current_time' % path)
    def test_end_log(self, mock_time):
        # Mock the current time
        now = '2000-01-01 0:0:0'
        mock_time.return_value = now
        log.end_log()
        with open(Path('sconstruct.log'), 'r') as f:
            line = f.readline()
            self.assertTrue(re.search('Build completed', line))
            self.assertTrue(re.search(r'\{%s\}' % now, line))

    def tearDown(self):
        (TESTDIR / 'test_log.txt').unlink(missing_ok = True)
        (TESTDIR / 'sconstruct.log').unlink(missing_ok = True)


if __name__ == '__main__':
    unittest.main()

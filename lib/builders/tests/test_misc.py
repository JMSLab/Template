import unittest
import sys
import os
import re
import shutil
import mock
import datetime

# Ensure that Python can find and load the GSLab libraries
os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path.append('../..')

import gslab_scons.misc as misc
import gslab_scons._exception_classes as ex_classes
from gslab_make.tests import nostderrout

path = 'gslab_scons.misc'


# This class is used for testing current_time()
class MockDateTime(datetime.datetime):
    @classmethod
    def now(cls):
        return cls(2017, 1, 20, 
                   15,   2, 18, 
                   133911)


class TestMisc(unittest.TestCase):
    @mock.patch('gslab_scons.misc.state_of_repo')
    @mock.patch('gslab_scons.misc.issue_size_warnings')
    def test_scons_debrief(self, mock_size_warn, mock_repo_state):
        target = 'state_of_repo.log'
        env    = {'MAXIT': '10', 
                  'look_in': 'release',
                  'file_MB_limit': '1',
                  'total_MB_limit': '2'}
        misc.scons_debrief(target, env)
        mock_size_warn.assert_called_with(['release'], 1, 2)
        mock_repo_state.assert_called_with(10)

        with self.assertRaises(KeyError):
            misc.scons_debrief(target, {})

        env = {'MAXIT': 'maxit', 
               'look_in': 'release',
               'file_MB_limit': '1',
               'total_MB_limit': '2'}            
        with self.assertRaises(ValueError):
            misc.scons_debrief(target, env)

    #== Tests for stata_command_unix() and stata_command_win() ======
    # The tests below patch sys.platform to mock various 
    # operating systems. 
    @mock.patch('gslab_scons.misc.sys.platform', 'darwin')
    def test_stata_command_unix_mac(self):
        '''
        Test that stata_command_unix() returns the expected
        command when run on Mac computers.
        '''
        output = misc.stata_command_unix('stata')
        self.assertEqual(output.strip(), 'stata -e %s %s')

    @mock.patch('gslab_scons.misc.sys.platform', 'linux')
    def test_stata_command_unix_linux(self):
        '''
        Test that stata_command_unix() returns the expected
        command when run on Linux computers.
        '''        
        output = misc.stata_command_unix('stata-se')
        self.assertEqual(output.strip(), 'stata-se -b %s %s')

    @mock.patch('gslab_scons.misc.sys.platform', 'win32')
    def test_stata_command_unix_windows(self):
        '''
        Test that stata_command_unix() raises an error when
        when on run Windows computers.
        '''
        with self.assertRaises(KeyError):
            output = misc.stata_command_unix('stata-mp')

    @mock.patch('gslab_scons.misc.sys.platform', 'cygwin')
    def test_stata_command_unix_other(self):
        '''
        Test that stata_command_unix() raises an error when 
        run on non-Windows, non-Mac, non-Linux machines.
        '''
        with self.assertRaises(KeyError):
            output = misc.stata_command_unix('stata-mp')

    @mock.patch('gslab_scons.misc.sys.platform', 'win32')        
    def test_stata_command_win_windows(self):
        output = misc.stata_command_win('stata-mp')
        self.assertEqual(output.strip(), 'stata-mp /e do %s %s')           

    @mock.patch('gslab_scons.misc.sys.platform', 'darwin')        
    def test_stata_command_win_unix(self):
        '''
        Test that stata_command_win() gives a Windows stata
        command even on a non-Windows machine. 
        '''
        output = misc.stata_command_win('stata-mp')
        self.assertEqual(output.strip(), 'stata-mp /e do %s %s')

    #================================================================
    
    def test_is_unix(self):
        '''
        Test that is_unix() returns True on Mac and Linux
        machines and False otherwise. 
        '''
        platform_ref = 'gslab_scons.misc.sys.platform'
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
        environ = 'gslab_scons.misc.os.environ'
        mocked_environ = {'PROGRAMFILES(X86)': 'C:/Program Files (x86)'}
        with mock.patch(environ, mocked_environ):
            self.assertTrue(misc.is_64_windows())
        with mock.patch(environ, dict()):
            self.assertFalse(misc.is_64_windows())

    @mock.patch('gslab_scons.misc.os.environ', {'PATH': '/bin:usrs/local'})
    @mock.patch('gslab_scons.misc.os.pathsep', ':')
    @mock.patch('gslab_scons.misc.os.access')
    def test_is_in_path(self, mock_access):
        '''
        Test that is_in_path() returns i) the full path of 
        a recognised executable that the function takes as
        an argument and ii) None if the function's argument
        is not recognised as an executable. 
        '''
        mock_access.side_effect = self.access_side_effect

        self.assertEqual(misc.is_in_path('stata'), 
                         '/bin/stata')
        self.assertEqual(misc.is_in_path('executable_file'), 
                         'executable_file')
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

    def test_command_line_args(self):
        env = {'test' : ''}
        self.assertEqual(misc.command_line_args(env), '')

        env = {'CL_ARG' : 'Test'}
        self.assertEqual(misc.command_line_args(env), 'Test')

        env = {'CL_ARG' : 1}
        self.assertEqual(misc.command_line_args(env), '1')

        env = {'CL_ARG' : ['Test_1', 'Test_2']}
        self.assertEqual(misc.command_line_args(env), 'Test_1 Test_2')

        env = {'CL_ARG' : [True, None, 'Test']}
        self.assertEqual(misc.command_line_args(env), 'True None Test')             

    def test_make_list_if_string(self):
        self.assertEqual(misc.make_list_if_string(['test', 'test']), 
                                                  ['test', 'test'])
        self.assertEqual(misc.make_list_if_string('test'), ['test'])
        self.assertEqual(misc.make_list_if_string(['test']), ['test'])
        
        # We expect the function to raise Type Errors when it receives
        # inputs that are not strings or lists
        with self.assertRaises(TypeError):
            self.assertEqual(misc.make_list_if_string(1), 1)
        with self.assertRaises(TypeError):
            self.assertEqual(misc.make_list_if_string(None), None)

    def test_check_code_extension(self):
        '''Unit tests for check_code_extension()

        This method tests that check_code_extensions() associates software with 
        file extensions as intended. The function should return None in cases 
        where the extension is correctly specified and raise an error otherwise.
        '''
    	self.assertEqual(misc.check_code_extension('test.do',  '.do'),  None)
    	self.assertEqual(misc.check_code_extension('test.r',   '.r'),   None)
    	self.assertEqual(misc.check_code_extension('test.lyx', '.lyx'), None)
        self.assertEqual(misc.check_code_extension('test.py',  '.py'),  None)
        self.assertEqual(misc.check_code_extension('test.m',   '.m'),   None)
        self.assertEqual(misc.check_code_extension('test.M',   '.M'),   None)
    	
        with self.assertRaises(ex_classes.BadExtensionError), nostderrout():
            misc.check_code_extension('test.badextension', '.py')

    @mock.patch('gslab_scons.misc.datetime.datetime', MockDateTime)
    def test_current_time(self):
        '''
        Test that current_time() prints the correct current time
        in the expected format. Here, the "correct current time"
        is a fixed value set within the MockDateTime class.
        '''                            
        the_time = misc.current_time()
        self.assertEqual('2017-01-20 15:02:18', the_time)

    def test_state_of_repo(self):
        maxit = 10
        # Test general functionality
        misc.state_of_repo(maxit)
        logfile = open('state_of_repo.log', 'rU').read()
        self.assertIn('GIT STATUS', logfile)
        self.assertIn('FILE STATUS', logfile)

        # Test maxit functionality
        os.mkdir('state_of_repo')
        for i in range(1, 20):
            with open('state_of_repo/test_%s.txt' % i, 'wb') as f:
                f.write('Test')
        misc.state_of_repo(maxit)
        logfile = open('state_of_repo.log', 'rU').read()
        self.assertIn('MAX ITERATIONS', logfile)

        # Cleanup
        shutil.rmtree('state_of_repo')
        os.remove('state_of_repo.log')

    def test_lyx_scan(self):
        # Open a test LyX file containing dependency statements
        infile = open('./input/lyx_test_dependencies.lyx').read()
        # Mock an SCons node object to return this file's contents
        # when its get_contents() method is called.
        node   = mock.MagicMock(get_contents = lambda: infile)
        # Mock an SCons environment object with an EXTENSIONS data attribute
        env    = mock.MagicMock(EXTENSIONS = ['.lyx', '.txt'])
        output = misc.lyx_scan(node, env, None)
        # Ensure lyx_scan scanned the test file correctly
        self.assertEqual(output, ['lyx_test_file.lyx', 'tables_appendix.txt'])

    @mock.patch('%s.raw_input' % path)
    def test_load_yaml_value(self, mock_raw_input):
        # Setup
        def raw_input_side_effect(*args, **kwargs):
            message = args[0]
            if re.search("corrupted", message):
                return 'y'
            if re.search("Enter", message):
                return 'value'

        def raw_input_side_effect2(*args, **kwargs):
            message = args[0]
            if re.search("corrupted", message):
                return 'n'
            if re.search("Enter", message):
                return 'none'

        mock_raw_input.side_effect = raw_input_side_effect

        yaml = 'yaml.yaml'
        def make_yaml(string):
            if os.path.isfile(yaml):
                os.remove(yaml)  
            with open(yaml, 'wb') as f:
                f.write('%s\n' % string)

        # Test Good
        key = 'key'
        value = 'value'
        # Yaml file exists, is not corrupt, and has key.
        make_yaml('%s: %s' % (key, value))
        self.assertEqual(misc.load_yaml_value(yaml, key), value)

        # Yaml file exists, is not corrupt, and doesn't have key. 
        # User enters value for key.
        make_yaml('bad_key: bad_value')
        self.assertEqual(misc.load_yaml_value(yaml, key), value)
        
        # But now yaml has a correct key and doesn't require user input.
        mock_raw_input.side_effect = lambda x: "bad_value"
        self.assertEqual(misc.load_yaml_value(yaml, key), value)
        mock_raw_input.side_effect = raw_input_side_effect

        # Yaml file exists and is corrupt. User deletes and re-creates. 
        make_yaml('%s %s' % (key, value))
        self.assertEqual(misc.load_yaml_value(yaml, key), value)

        # Yaml file does not exist. User enters value to create. 
        os.remove(yaml)
        self.assertEqual(misc.load_yaml_value(yaml, key), value)

        # Yaml file does not exist. User enters none value to create. 
        os.remove(yaml)
        key = 'stata_executable'
        mock_raw_input.side_effect = raw_input_side_effect2
        self.assertEqual(misc.load_yaml_value(yaml, key), None)

        # Yaml file now exists with none value.
        self.assertTrue(os.path.isfile(yaml))
        self.assertEqual(misc.load_yaml_value(yaml, key), None)

        # Test bad
        with self.assertRaises(ex_classes.PrerequisiteError):
            # Corrupt file and user doesn't choose to delete and re-create 
            make_yaml('key value')
            misc.load_yaml_value(yaml, 'key')

        if os.path.isfile(yaml):
            os.remove(yaml)  


    @mock.patch('%s.os.path.expanduser' % path)
    @mock.patch('%s.os.path.isdir' % path)
    def test_check_and_expand_path(self, mock_is_dir, mock_expanduser):
        mock_expanduser.side_effect = lambda x: re.sub('~', 'Users/lb', x)
        mock_is_dir.side_effect     = lambda x: x == 'Users/lb/cache'

        misc.check_and_expand_path('~/cache')
        misc.check_and_expand_path('Users/lb/cache')
        with self.assertRaises(ex_classes.PrerequisiteError):
            misc.check_and_expand_path('~/~/cache')
        with self.assertRaises(ex_classes.PrerequisiteError):
            misc.check_and_expand_path('lb/cache')
        with self.assertRaises(ex_classes.PrerequisiteError):
            misc.check_and_expand_path(3)

            
if __name__ == '__main__':
    unittest.main()

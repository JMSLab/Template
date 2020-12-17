import unittest
import sys
import os
import re
import shutil
import mock
import datetime
import subprocess

# Ensure that Python can find and load the GSLab libraries
os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path.append('../..')

import gslab_scons.configuration_tests as config_tests
import gslab_scons._exception_classes as ex_classes
from gslab_make.tests import nostderrout

path = 'gslab_scons.configuration_tests'

class TestConfigurationTests(unittest.TestCase):

    @mock.patch('%s.check_python_packages' % path)
    def test_check_python(self, mock_check_python_packages):
        # Incorrect python
        with mock.patch('%s.sys.version_info' % path, [3]):
            with self.assertRaises(ex_classes.PrerequisiteError):
                config_tests.check_python('3.0.2')
            mock_check_python_packages.assert_not_called()

        with mock.patch('%s.sys.version_info' % path, [2]):
            # Test default arguments and correct python
            packages = ["yaml", "gslab_scons", "gslab_make", "gslab_fill"]
            config_tests.check_python('3.0.2')
            mock_check_python_packages.assert_called_with('3.0.2', packages)

            # Test alternative arguments and correct Python
            packages = ["yaml"]
            config_tests.check_python(3.0, packages)
            mock_check_python_packages.assert_called_with(3.0, packages)        

            # Test alternative arguments format and correct python
            packages = "yaml"
            config_tests.check_python('3.0.2', packages)
            mock_check_python_packages.assert_called_with('3.0.2', packages) 


    @mock.patch('%s.pkg_resources.get_distribution' % path)
    @mock.patch('%s.importlib.import_module'        % path)
    @mock.patch('%s.convert_packages_argument'      % path)
    def test_check_python_packages(self, mock_convert_packages, 
                                   mock_import, mock_version):
        # Setup
        class MockVersionSideEffect(object):
            def __init__(self):
                self.version = '3.0.2'

        def version_side_effect(*args, **kwargs):
            return MockVersionSideEffect()

        mock_version.side_effect          = version_side_effect
        mock_convert_packages.side_effect = lambda x: ['yaml', 'os']
        mock_import.side_effect           = lambda x: None

        # Default correct test
        config_tests.check_python_packages('3.0.2', ['yaml', 'os'])
        mock_convert_packages.assert_called_with(['yaml', 'os'])
        mock_import.assert_called()
        mock_version.assert_called_with('gslab_tools')

        # Incorrect gslab_python version
        packages = ['yaml', 'os']
        with self.assertRaises(ex_classes.PrerequisiteError):
            config_tests.check_python_packages('3.0.3', packages)
        with self.assertRaises(ex_classes.PrerequisiteError):
            config_tests.check_python_packages('3.0.13', packages)
        with self.assertRaises(ex_classes.PrerequisiteError):
            config_tests.check_python_packages('10.00.01', packages)
        with self.assertRaises(ex_classes.PrerequisiteError):
            config_tests.check_python_packages('3.2.2', packages)

        # Module doesn't exist
        def import_side_effect(*args, **kwargs):
            if args[0] == 'os':
                raise ImportError(args[0])

        with self.assertRaises(ex_classes.PrerequisiteError):
            mock_import.side_effect = import_side_effect
            config_tests.check_python_packages('3.0.2', packages)


    def test_convert_packages_argument(self):
        arg = ['test']
        self.assertEqual(config_tests.convert_packages_argument(arg),    arg)
        self.assertEqual(config_tests.convert_packages_argument(arg[0]), arg)
        arg = ['test', 'test1']
        self.assertEqual(config_tests.convert_packages_argument(arg), arg)

        with self.assertRaises(ex_classes.PrerequisiteError):
            config_tests.convert_packages_argument(123)
        with self.assertRaises(ex_classes.PrerequisiteError):
            config_tests.convert_packages_argument({'test'})
        with self.assertRaises(ex_classes.PrerequisiteError):
            config_tests.convert_packages_argument(['test', 2])
        with self.assertRaises(ex_classes.PrerequisiteError):
            config_tests.convert_packages_argument([2, 2])
        with self.assertRaises(ex_classes.PrerequisiteError):
            config_tests.convert_packages_argument(lambda x: 'test')


    @mock.patch('%s.is_in_path'       % path)
    @mock.patch('%s.check_r_packages' % path)
    def test_check_r(self, mock_check_r_packages, mock_is_in_path):
        # No R executable
        mock_is_in_path.side_effect = lambda x: None
        with self.assertRaises(ex_classes.PrerequisiteError):
            config_tests.check_r()
        mock_check_r_packages.assert_not_called()

        # Test default arguments 
        mock_is_in_path.side_effect = lambda x: x == 'R'
        config_tests.check_r()
        mock_check_r_packages.assert_called_with(["yaml"])

        # Test alternative arguments
        packages = ["yaml", "ggplot"]
        config_tests.check_r(packages)
        mock_check_r_packages.assert_called_with(packages)        

        # Test alternative arguments format
        packages = "yaml"
        config_tests.check_r(packages)
        mock_check_r_packages.assert_called_with(packages)


    @mock.patch('%s.subprocess.check_output'   % path)
    @mock.patch('%s.convert_packages_argument' % path)
    def test_check_r_packages(self, mock_convert_packages, mock_check_output):
        # Setup
        def output_side_effect(*args, **kwargs):
            cmd_line_call = args[0]
            if cmd_line_call in ['R -q -e "suppressMessages(library(%s))"' % a \
                                        for a in ['yaml', 'ggplot']]:
                return 0
            else:
                subprocess.check_call("exit 1", shell = True)

        mock_convert_packages.side_effect = lambda x: ['yaml', 'ggplot']
        mock_check_output.side_effect     = output_side_effect

        # Default correct test
        packages = ['yaml', 'ggplot']
        config_tests.check_r_packages(packages)
        mock_convert_packages.assert_called_with(packages)
        mock_check_output.assert_called()

        # Module doesn't exist
        packages = ['yaml', 'os']
        mock_convert_packages.side_effect = lambda x: packages
        with self.assertRaises(ex_classes.PrerequisiteError):
            config_tests.check_r_packages(packages)

        packages = ['sys', 'os']
        mock_convert_packages.side_effect = lambda x: packages
        with self.assertRaises(ex_classes.PrerequisiteError):
            config_tests.check_r_packages(packages)


    @mock.patch('%s.is_in_path' % path)
    def test_check_lyx(self, mock_is_in_path):
        # No lyx executable
        mock_is_in_path.side_effect = lambda x: None
        with self.assertRaises(ex_classes.PrerequisiteError):
            config_tests.check_lyx()

        # Test default 
        mock_is_in_path.side_effect = lambda x: x == 'lyx'
        config_tests.check_lyx()


    @mock.patch('%s.subprocess.check_output' % path)
    def test_check_lfs(self, mock_check):
        mock_check.side_effect = self.make_side_effect(['install', 'init'])
        config_tests.check_lfs()

        mock_check.side_effect = self.make_side_effect(['init'])
        config_tests.check_lfs()

        mock_check.side_effect = self.make_side_effect(['install'])
        config_tests.check_lfs()

        with self.assertRaises(ex_classes.PrerequisiteError):
            mock_check.side_effect = self.make_side_effect(['checkout'])
            config_tests.check_lfs()

    @staticmethod
    def make_side_effect(available_options):
        '''
        This function returns a side effect that does nothing if 
        the command specified by its first positional argument
        is i) not a git-lfs command or ii) a git-lfs command 
        followed by one of the commands specified in the 
        available_options argument. 
        '''
        def side_effect(*args, **kwargs):
            command = args[0]
            if re.search('^git-lfs', command.strip(), flags = re.I):
                option = re.sub('git-lfs', '', command).strip()
                if option not in available_options:
                    raise subprocess.CalledProcessError(1, command)  
                else:
                    pass  
            else:
                pass
        return side_effect


    @mock.patch('%s.check_stata_packages' % path)
    @mock.patch('%s.get_stata_executable' % path)
    @mock.patch('%s.get_stata_command'    % path)
    def test_check_stata(self, mock_stata_command, mock_stata_exec, mock_stata_packages):
        # Setup
        def stata_package_side_effect(*args, **kwargs):
            command  = args[0]
            packages = args[1]
            if command != 'statamp':
                raise ex_classes.PrerequisiteError()
            for package in packages:
                if package != 'yaml':
                    raise ex_classes.PrerequisiteError()

        f = lambda x: x['stata_executable'] if x['stata_executable'] is not None \
                                            else 'statamp'
        mock_stata_exec.side_effect     = f
        mock_stata_command.side_effect  = lambda x: x
        mock_stata_packages.side_effect = stata_package_side_effect

        # Correct tests
        # Has yaml value
        self.assertEqual(config_tests.check_stata(), 'statamp')

        # No yaml value
        self.assertEqual(config_tests.check_stata(), 'statamp')

        # Failures
        # No yaml value and no default value in path
        mock_stata_exec.side_effect = lambda x: None
        with self.assertRaises(ex_classes.PrerequisiteError):
            config_tests.check_stata()

        # Bad package
        mock_stata_exec.side_effect = f
        with self.assertRaises(ex_classes.PrerequisiteError):
            config_tests.check_stata(packages = ['bad_package'])


    

    @mock.patch('%s.is_unix' % path)
    @mock.patch('%s.convert_packages_argument' % path)
    @mock.patch('%s.subprocess.check_output' % path)
    def test_check_stata_packages(self, mock_check_output, 
                                  mock_package_argument, mock_is_unix):

        def check_output_side_effect(*args, **kwargs):
            command = args[0].split("which ")[0]
            if not re.search("statamp", command):
                raise subprocess.CalledProcessError(1, args[0])  

            with open('stata.log', 'wb') as f:
                if not re.search('yaml', args[0]):
                    package = args[0].split("which ")[1]
                    f.write("command %s not found" % package)

        mock_check_output.side_effect     = check_output_side_effect
        mock_package_argument.side_effect = lambda x: ['yaml']
        mock_is_unix.return_value = True  

        with mock.patch('%s.sys.platform' % path, 'win32'):
            # Good tests

            # Unix (is.unix is checked before sys.platform)
            config_tests.check_stata_packages("statamp", "yaml")

            # Windows
            mock_is_unix.return_value = False
            config_tests.check_stata_packages("statamp", "yaml")

            # No packages
            mock_check_output.reset_mock()
            mock_package_argument.side_effect = lambda x: []
            config_tests.check_stata_packages("statamp", [])
            mock_check_output.assert_not_called()

            # Bad Tests
            with self.assertRaises(ex_classes.PrerequisiteError):
                # Bad package
                mock_package_argument.side_effect = lambda x: ['bad_package']
                config_tests.check_stata_packages("statamp", "bad_package")
            
            with self.assertRaises(ex_classes.PrerequisiteError):
                # Bad executable
                mock_package_argument.side_effect = lambda x: ['yaml']
                config_tests.check_stata_packages("bad_executable", "yaml")

        # More bad tests
        with self.assertRaises(ex_classes.PrerequisiteError): 
            with mock.patch('%s.sys.platform' % path, 'Unknown'):
                # Unknown platform
                config_tests.check_stata_packages("statamp", "yaml")
        

if __name__ == '__main__':
    unittest.main()

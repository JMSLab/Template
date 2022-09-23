import importlib
import tempfile
# import sys
import os
import re

from unittest import mock
from .. import misc
from ..builders.executables import get_executable
from .._exception_classes import BadExtensionError


def platform_patch(platform, path):
    '''
    This script produces a mock.patch decorator that mocks sys.platform
    as `platform` in both the module given by `path` and, if possible,
    this module's imported misc module.
    '''
    main_patch  = mock.patch('%s.sys.platform' % path, platform)

    # Try to also patch misc.sys.platform
    try:
        misc_path = '%s.misc.sys.platform' % path
        # Check whether misc_path is a valid module
        importlib.util.find_spec(misc_path)
        misc_patch  = mock.patch(misc_path, platform)
        total_patch = lambda f: misc_patch(main_patch(f))
    except ImportError:
        total_patch = main_patch

    return total_patch


def command_match(command, language, which = None):
    match = None

    '''Parse Python, R, and Stata system calls as re.match objects'''
    if language in ['python', 'py']:
        # e.g. "python script.py cl_arg > script.log"
        default = re.escape(get_executable('python'))
        match = re.match(r'\s*'
                         rf'(?P<executable>python|{default})'
                         r'\s*'
                         r'(?P<source>[-\.\/\\\w]+)'
                         r'\s*'
                         r'(?P<args>(\s?[\.\/\\\w]+)*)?'
                         r'\s*'
                         r'(?P<log>>\s*[\.\/\\\w]+)?',
                         command)

    elif language in ['r', 'R']:
        # e.g. "Rscript --no-save --no-restore --verbose script.R input.txt > script.log 2>&1"
        default = re.escape(get_executable('r'))
        match = re.match(r'\s*'
                         rf'(?P<executable>Rscript|{default})'
                         r'\s+'
                         r'(?P<option1>--no-save)'
                         r'\s*'
                         r'(?P<option2>--no-restore)'
                         r'\s*'
                         r'(?P<option3>--verbose)'
                         r'\s*'
                         r'(?P<source>[\.\/\\\w]+\.[rR])'
                         r'\s*'
                         r'(?P<args>(\s?[\.\/\\\w]+)*)?'
                         r'\s*'
                         r'(?P<log>>\s*[\.\/\\\w]+(\.\w+)?)?'
                         r'\s*'
                         r'(?P<append>2\>\&1)',
                         command)

    elif language in ['stata', 'do']:
        # e.g. "stata-mp -e do script.do cl_arg"
        default = re.escape(get_executable('stata'))
        match = re.match(r'\s*'
                         rf'(?P<executable>\S+|{default})'
                         r'\s+'
                         r'(?P<options>(\s?[-\/][-A-Za-z]+)+)?'
                         r'\s*'
                         r'(?P<do>do)?'
                         r'\s*'
                         r'(?P<source>[\.\/\\\w]+\.do)'
                         r'\s*'
                         r'(?P<args>.*)',
                         command)
    elif language == 'lyx':
        # e.g. "lyx -E pdf2 target_file file.lyx > sconscript.log"
        default = re.escape(get_executable('lyx'))
        match = re.match(r'\s*'
                         rf'(?P<executable>\w+|{default})'
                         r'\s+'
                         r'(?P<option>-\w+\s+\w+)?'
                         r'\s*'
                         r'(?P<target>[\.\/\\\w]+\.\w+)?'
                         r'\s*'
                         r'(?P<source>[\.\/\\\w]+\.\w+)?'
                         r'\s*'
                         r'(?P<log_redirect>\> [\.\/\\\w]+\.\w+)?',
                         command)

    elif language in ['latex', 'pdflatex']:
        # e.g. "pdflatex -interaction nonstopmode -jobname target_file file.tex > sconscript.log"
        default = re.escape(get_executable('latex'))
        match = re.match(r'\s*'
                         rf'(?P<executable>\w+|{default})'
                         r'\s+'
                         r'(?P<option1>-\w+\s+\S+)?'
                         r'\s*'
                         r'(?P<option2>-\w+\s+\S+)?'
                         r'\s*'
                         r'(?P<source>[\.\/\\\w]+\.\w+)?'
                         r'\s*'
                         r'(?P<log_redirect>\>\s*[\.\/\\\w]+\.\w+)?',
                         command)

    elif language in ['bibtex']:
        # e.g. "bibtex target_file > sconscript.log"
        default = re.escape(get_executable('bibtex'))
        match = re.match(r'\s*'
                         rf'(?P<executable>\w+|{default})'
                         r'\s+'
                         r'(?P<target>[\.\/\\\w]+)?'
                         r'\s*'
                         r'(?P<log_redirect>\>\s*[\.\/\\\w]+\.\w+)?',
                         command)

    if which:
        return match.group(which)
    else:
        return match


def check_log(test_object, log_path, timestamp = True):
    '''Check for the existence of a (timestamped) log'''
    with open(log_path, 'r') as log_file:
        log_data = log_file.read()

    if timestamp:
        test_object.assertIn('*** Builder log created:', log_data)
    else:
        test_object.assertNotIn('Log created:', log_data)

    os.remove(log_path)


def bad_extension(test_object, builder,
                  bad  = None,
                  good = None,
                  env  = {}):
    '''Ensure builders fail when their first sources have bad extensions'''

    tf = tempfile.NamedTemporaryFile(suffix = '.bad', mode = 'w', delete = False)
    if bad is None:
        bad = tf.name

    if good:
        # We expect a failure even when a source with a "good" extension
        # is included but is not the first source.
        source = [bad, good]
    else:
        source = [bad]

    with test_object.assertRaises(BadExtensionError):
        builder(target = 'test_output.txt',
                source = source,
                env    = env)

    tf.close()


def standard_test(test_object, builder,
                  extension   = None,
                  system_mock = None,
                  source      = None,
                  target      = 'test_output.txt',
                  env         = {},
                  nsyscalls   = 1):
    '''Test that builders run without errors and create logs properly.'''
    if not source:
        source = 'input/test_script.%s' % extension

    builder(source = source, target = target, env = env)

    if isinstance(target, str):
        log_directory = misc.get_directory(target)
    else:
        log_directory = misc.get_directory(target[0])

    log_path = os.path.join(log_directory, 'sconscript.log')
    check_log(test_object, log_path)

    if system_mock:
        test_object.assertEqual(system_mock.call_count, nsyscalls)
        system_mock.reset_mock() 


def input_check(test_object, builder, extension,
                source = 'missing',
                target = 'test_output.txt',
                env    = {},
                error  = None):
    '''Test builders' behaviour when passed unconventional arguments.'''
    # If alternatives are not provided, define
    # standard builder arguments
    if source == 'missing':
        source = 'test_script.%s' % extension

    if not error:
        builder(source = source, target = target, env = env)
        check_log(test_object, 'sconscript.log')
    else:
        with test_object.assertRaises(error):
            builder(source = source, target = target, env = env)


def test_cl_args(test_object, builder, system_mock, extension, env = {}):
    '''
    Ensure that builders correctly include command line arguments in
    their system calls.
    '''
    source = 'test_script.%s' % extension
    target = 'test_output.txt'

    # i) Single command line argument
    if env:
        env['CL_ARG'] = 'test'
    else:
        env = {'CL_ARG': 'test'}

    builder(source = source, target = target, env = env)

    # The system command is the first positional argument
    command = system_mock.call_args[0][0]
    args    = command_match(command, extension, which = 'args')

    test_object.assertIn('test', args.split(' '))
    test_object.assertEqual(len(args.split(' ')), 1)
    check_log(test_object, 'sconscript.log')

    # Multiple command line arguments
    env['CL_ARG'] = [1, 2, None]

    builder(source = source,
            target = target,
            env    = env)

    command = system_mock.call_args[0][0]
    args    = command_match(command, extension, which = 'args')

    for arg in env['CL_ARG']:
        test_object.assertIn(str(arg), args.split(' '))

    test_object.assertEqual(len(args.split(' ')), 3)
    check_log(test_object, 'sconscript.log')

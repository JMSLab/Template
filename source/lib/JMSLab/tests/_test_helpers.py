import os
import re
import sys
import mock
import inspect
import imp

sys.path.append('../..')
import gslab_scons.misc as misc
from gslab_scons._exception_classes import BadExtensionError


def platform_patch(platform, path):
    '''
    This script produces a mock.patch decorator that mocks
    sys.platform as `platform` in both the module given by 
    `path` and, if possible, this module's
    imported misc module. 
    '''
    main_patch  = mock.patch('%s.sys.platform' % path, platform)
    
    # Try to also patch misc.sys.platform
    try:
        misc_path = '%s.misc.sys.platform' % path
        # Check whether misc_path is a valid module
        imp.find_module(misc_path)
        misc_patch  = mock.patch(misc_path, platform)
        total_patch = lambda f: misc_patch(main_patch(f))
    except ImportError:
        total_patch = main_patch

    return total_patch

def command_match(command, executable, which = None):
    '''Parse Python, R, and Stata system calls as re.match objects'''
    if executable in ['python', 'py']:
        # e.g. "python script.py cl_arg > script.log"
        match = re.match('\s*'
                         '(?P<executable>python)'
                         '\s*'
                         '(?P<source>[-\.\/\w]+)'
                         '\s*'
                         '(?P<args>(\s?[\.\/\w]+)*)?'
                         '\s*'
                         '(?P<log>>\s*[\.\/\w]+)?',
                         command)

    elif executable in ['r', 'R']:
        # e.g. "Rscript --no-save --no-restore --verbose script.R input.txt > script.log 2>&1"
        match = re.match('\s*'
                         '(?P<executable>Rscript)'
                         '\s+'
                         '(?P<option1>--no-save)'
                         '\s*'
                         '(?P<option2>--no-restore)'
                         '\s*'
                         '(?P<option3>--verbose)'
                         '\s*'
                         '(?P<source>[\.\/\w]+\.[rR])'
                         '\s*'
                         '(?P<args>(\s?[\.\/\w]+)*)?'
                         '\s*'
                         '(?P<log>> [\.\/\w]+(\.\w+)?)?'
                         '\s*'
                         '(?P<append>2\>\&1)',
                         command)

    elif executable in ['stata', 'do']: 
        # e.g. "stata-mp -e do script.do cl_arg"
        match = re.match('\s*'
                         '(?P<executable>\S+)'
                         '\s+'
                         '(?P<options>(\s?[-\/][-A-Za-z]+)+)?'
                         '\s*'
                         '(?P<do>do)?'
                         '\s*'
                         '(?P<source>[\.\/\w]+\.do)'
                         '\s*'
                         '(?P<args>.*)',
                         command)

    elif executable == 'lyx':
        # e.g. "lyx -e pdf2 file.lyx > ./sconscript.log"
        match = re.match('\s*'
                         '(?P<executable>\w+)'
                         '\s+'
                         '(?P<option>-\w+ \w+)?'
                         '\s*'
                         '(?P<source>[\.\/\w]+\.\w+)?'
                         '\s*'
                         '(?P<log_redirect>\> [\.\/\w]+\.\w+)?',
                         command)

    elif executable == 'pdflatex':
        # e.g. "pdflatex -interaction nonstopmode -jobname target_file file.tex > ./sconscript.log"
        match = re.match('\s*'
                         '(?P<executable>\w+)'
                         '\s+'
                         '(?P<option1>-\w+ \S+)?'
                         '\s*'
                         '(?P<option2>-\w+ \S+)?'
                         '\s*'
                         '(?P<source>[\.\/\w]+\.\w+)?'
                         '\s*'
                         '(?P<log_redirect>\> [\.\/\w]+\.\w+)?',
                         command)

    if which:
        return match.group(which)
    else:
        return match


def check_log(test_object, log_path, timestamp = True):
    '''Check for the existence of a (timestamped) log'''
    with open(log_path, 'rU') as log_file:
        log_data = log_file.read()

    if timestamp:
        test_object.assertIn('*** Builder log created:', log_data)
    else:
        test_object.assertNotIn('Log created:', log_data)

    os.remove(log_path)


def bad_extension(test_object, builder, 
                  bad  = 'bad',
                  good = None,
                  env  = {}):
    '''Ensure builders fail when their first sources have bad extensions'''
    if good:
        # We expect a failure even when a source with a "good" extension
        # is included but is not the first source. 
        source = [bad, good]
    else:
        source = [bad]

    with test_object.assertRaises(BadExtensionError):
        builder(target = './test_output.txt', 
                source = source, 
                env    = env)


def standard_test(test_object, builder, 
                  extension   = None,  
                  system_mock = None,
                  source      = None,
                  target = './test_output.txt',
                  env    = {}):
    '''Test that builders run without errors and create logs properly.'''
    if not source:
        source = './test_script.%s' % extension

    builder(source = source, target = target, env = env)
    
    if isinstance(target, str):
        log_directory = misc.get_directory(target)
    else:
        log_directory = misc.get_directory(target[0])

    log_path = os.path.join(log_directory, 'sconscript.log')
    check_log(test_object, log_path)

    if system_mock:
        system_mock.assert_called_once()
        system_mock.reset_mock()

def input_check(test_object, builder, extension,
                source = 'missing',
                target = './test_output.txt',
                env    = {},
                error  = None):
    '''Test builders' behaviour when passed unconventional arguments.'''
    # If alternatives are not provided, define 
    # standard builder arguments
    if source == 'missing':
        source = 'test_script.%s' % extension

    if not error:
        builder(source = source, target = target, env = env)
        check_log(test_object, './sconscript.log')
    else:
        with test_object.assertRaises(error):
            builder(source = source, target = target, env = env)


def test_cl_args(test_object, builder, system_mock, extension, env = {}):
    '''
    Ensure that builders correctly include command line arguments in
    their system calls.
    '''
    source = './test_script.%s' % extension
    target = './test_output.txt'

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
    check_log(test_object, './sconscript.log')

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
    check_log(test_object, './sconscript.log')


def mock_release_data(args):
    '''
    Create a mock of the content attribute of a requests.session 
    object's get() method for a GitHub api session. The `args` argument
    should be a dictionary storing a GitHub repo's name and organisation,
    the version of a release, and a value for get().content's
    target_commitish field. 
    '''
    org              = args['org']
    repo             = args['repo']
    version          = args['vers']
    target_commitish = args['target_commitish']

    mock_release_data = \
        ','.join([
              '[{"url":'
                  '"https://api.github.com/'
                  'repos/%s/%s/releases/test_ID"' % (org, repo),
               '"assets_url":'
                  'https://api.github.com/'
                  'repos/%s/%s/releases/test_ID/assets"' % (org, repo),
               '"upload_url":'
                  '"https://uploads.github.com/'
                  'repos/%s/%s/releases/test_ID/assets{?name,label}"' % (org, repo),
               '"html_url":'
                  '"https://github.com/'
                  '%s/%s/releases/tag/%s"' % (org, repo, version),
               '"id":test_ID',
               '"tag_name":"%s"' % version,
               '"target_commitish":"%s"' % target_commitish,
               '"name":"%s"' % version,
               '"draft":false',
               '"prerelease":false}]']) 
    return mock_release_data

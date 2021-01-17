import os
import re
import subprocess

from ..builders.executables import get_executables
from . import _test_helpers as helpers

EXE = get_executables()


def make_r_side_effect(recognized = True):
    '''
    Make a mock of mocks subprocess.check_output() for R CMD BATCH commands

    The executable_recognized argument determines whether "R"
    is a recognized executable on the mock platform.
    '''
    def side_effect(*args, **kwargs):
        '''
        This side effect mocks the behaviour of a subprocess.check_output()
        call on a machine with R set up for command-line use.
        '''
        # Get and parse the command passed to os.system()
        command = args[0]
        if re.search('R', command, flags = re.I) and not recognized:
            raise subprocess.CalledProcessError(1, command)

        match   = helpers.command_match(command, 'R')

        executable = match.group('executable')
        log        = match.group('log')
        append     = match.group('append')

        if log is None:
            # If no log path is specified, create one by using the
            # R script's path after replacing .R (if present) with .log.
            source = match.group('source')
            log    = '%s.log' % re.sub(r'\.R', '', source)

        if executable == 'Rscript' and log and append == '2>&1':
            with open(log.replace('>', '').strip(), 'wb') as log_file:
                log_file.write(b'Test log\n')
            with open('test_output.txt', 'wb') as target:
                target.write(b'Test target')

    return side_effect


def python_side_effect(*args, **kwargs):
    '''    Mock subprocess.check_output for testing build_python()'''
    command = args[0]
    match   = helpers.command_match(command, 'python')

    if match.group('log'):
        log_path = re.sub(r'(\s|>)', '', match.group('log'))
        with open(log_path, 'wb') as log_file:
            log_file.write(b'Test log')
        with open('test_output.txt', 'wb') as target:
            target.write(b'Test target')


def make_matlab_side_effect(recognized = True):
    '''
    Make a mock of subprocess.check_output() for Matlab commands

    The recognized argument determines whether "matlab"
    is a recognized executable on the mock platform.
    '''
    def side_effect(*args, **kwargs):
        try:
            command = kwargs['command']
        except KeyError:
            command = args[0]

        found = command.rfind(EXE['matlab']) == 0 or re.search('^matlab', command, flags = re.I)
        if found and not recognized:
            raise subprocess.CalledProcessError(1, command)

        log_match = re.search(r'> (?P<log>[-\.\w\/]+)', command)

        if log_match:
            log_path = log_match.group('log')
            with open(log_path, 'wb') as log_file:
                log_file.write(b'Test log')
            with open('test_output.txt', 'wb') as target:
                target.write(b'Test target')

        return None

    return side_effect


def matlab_copy_effect(*args, **kwargs):
    '''Mock copy so that it creates a file with the destination's path'''
    with open(args[1], 'wb') as test_file:
        test_file.write(b'test')


def make_stata_side_effect(recognized = True):
    '''
    Make a side effect mocking the behaviour of
    subprocess.check_output() when `recognized` is
    the only recognised system command.
    '''
    def stata_side_effect(*args, **kwargs):
        command = args[0]
        match   = helpers.command_match(command, 'stata')

        if match.group('executable') == recognized:
            # Find the Stata script's name
            script_name = match.group('source')
            stata_log   = os.path.basename(script_name).replace('.do', '.log')

            # Write a log
            with open(stata_log, 'wb') as logfile:
                logfile.write(b'Test Stata log.\n')
            with open('test_output.txt', 'wb') as target:
                target.write(b'Test target')

        else:
            # Raise an error if the executable is not recognised.
            raise subprocess.CalledProcessError(1, command)

    return stata_side_effect


def make_stata_path_effect(executable):
    '''
    Return a side effect for misc.is_in_path() that returns
    True iff the function's argument equals `executable`.
    '''
    def side_effect(*args, **kwargs):
        return (args[0] == executable)
    return side_effect


def lyx_side_effect(*args, **kwargs):
    '''
    This side effect mocks the behaviour of a subprocess.check_output call.
    The mocked machine has lyx set up as a command-line executable
    and can export .lyx files to .pdf files only using
    the "-e pdf2" option.
    '''
    # Get and parse the command passed to os.system()
    command = args[0]
    match = helpers.command_match(command, 'lyx')

    executable   = match.group('executable')
    option       = match.group('option')
    target_file  = match.group('target')
    source       = match.group('source')
    log_redirect = match.group('log_redirect')

    option_type    = re.findall(r'^(-\w+)',  option)[0]
    option_setting = re.findall(r'\s(\w+)$', option)[0]

    is_lyx = bool(re.search('^lyx$', executable, flags = re.I))

    # As long as output is redirected, create a log
    if log_redirect:
        log_path = re.sub(r'>\s*', '', log_redirect)
        with open(log_path, 'wb') as log_file:
            log_file.write(b'Test log\n')

    # If LyX is the executable, the options are correctly specified,
    # and the source exists, produce a .pdf file with the same base
    # name as the source file.

    # Mock a list of the files that LyX sees as existing
    # source_exists should be True only if the source script
    # specified in the system command belongs to existing_files.
    existing_files = ['test_script.lyx', 'input/lyx_test_file.lyx']
    source_exists  = os.path.abspath(source) in \
        map(os.path.abspath, existing_files)

    if is_lyx and option_type == '-E' and option_setting == 'pdf2' \
            and source_exists:

        with open(target_file, 'wb') as out_file:
            out_file.write(b'Mock .pdf output')


def latex_side_effect(*args, **kwargs):
    '''
    This side effect mocks the behaviour of a subprocess.check_output call.
    The mocked machine has pdflatex set up as a command-line executable
    and can export .tex files to .pdf files only using the "-jobname" option.
    '''
    # Get and parse the command passed to os.system()
    command = args[0]
    match = helpers.command_match(command, 'pdflatex')

    executable   = match.group('executable')
    option1      = match.group('option1')
    option2      = match.group('option2')
    source       = match.group('source')
    log_redirect = match.group('log_redirect')

    option1_type = re.findall(r'^(-\w+)', option1)[0]
    option2_type = re.findall(r'^(-\w+)', option2)[0]
    target_file  = re.findall(r'\s(\S+)', option2)[0]

    is_pdflatex  = bool(re.search('^pdflatex$', executable, flags = re.I))

    # As long as output is redirected, create a log
    if log_redirect:
        log_path = re.sub(r'\>\s*', '', log_redirect)
        with open(log_path, 'wb') as log_file:
            log_file.write(b'Test log\n')

    # If pdflatex is the executable, the options are correctly specified,
    # and the source exists, produce a .pdf file with the name specified in
    # the -jobname option.

    # Mock a list of the files that pdflatex sees as existing
    # source_exists should be True only if the source script
    # specified in the system command belongs to existing_files.
    existing_files = ['test_script.tex', 'input/latex_test_file.tex']
    source_exists  = os.path.abspath(source) in \
        map(os.path.abspath, existing_files)

    if is_pdflatex and source_exists and option1_type == '-interaction' and option2_type == '-jobname':
        with open('%s.pdf' % target_file, 'wb') as out_file:
            out_file.write(b'Mock .pdf output')
        with open('%s.log' % target_file, 'wb') as out_file:
            out_file.write(b'Mock .log output')

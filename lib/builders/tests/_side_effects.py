import os
import re
import mock
import requests
import shutil
import subprocess
import _test_helpers as helpers

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
            log    = '%s.log' % re.sub('\.R', '', source)
    
        if executable == 'Rscript' and log and append == '2>&1':
            with open(log.replace('>', '').strip(), 'wb') as log_file:
                log_file.write('Test log\n')
            with open('./test_output.txt', 'wb') as target:
                target.write('Test target')

    return side_effect


def python_side_effect(*args, **kwargs):
    '''    Mock subprocess.check_output for testing build_python()'''
    command = args[0]
    match   = helpers.command_match(command, 'python')

    if match.group('log'):
        log_path = re.sub('(\s|>)', '', match.group('log'))
        with open(log_path, 'wb') as log_file:
            log_file.write('Test log')
        with open('./test_output.txt', 'wb') as target:
            target.write('Test target')


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
    
        if re.search('^matlab', command, flags = re.I) and not recognized:
            raise subprocess.CalledProcessError(1, command)

        log_match = re.search('> (?P<log>[-\.\w\/]+)', command)
    
        if log_match:
            log_path = log_match.group('log')
            with open(log_path, 'wb') as log_file:
                log_file.write('Test log')
            with open('./test_output.txt', 'wb') as target:
                target.write('Test target')
    
        return None

    return side_effect


def matlab_copy_effect(*args, **kwargs):
    '''Mock copy so that it creates a file with the destination's path'''
    open(args[1], 'wb').write('test')


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
                logfile.write('Test Stata log.\n')
            with open('./test_output.txt', 'wb') as target:
                target.write('Test target')

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
    source       = match.group('source')
    log_redirect = match.group('log_redirect')

    option_type    = re.findall('^(-\w+)',  option)[0]
    option_setting = re.findall('\s(\w+)$', option)[0]

    is_lyx = bool(re.search('^lyx$', executable, flags = re.I))

    # As long as output is redirected, create a log
    if log_redirect:
        log_path = re.sub('>\s*', '', log_redirect)
        with open(log_path, 'wb') as log_file:
            log_file.write('Test log\n')

    # If LyX is the executable, the options are correctly specified,
    # and the source exists, produce a .pdf file with the same base 
    # name as the source file.

    # Mock a list of the files that LyX sees as existing
    # source_exists should be True only if the source script 
    # specified in the system command belongs to existing_files. 
    existing_files = ['test_script.lyx', './input/lyx_test_file.lyx']
    source_exists  = os.path.abspath(source) in \
                         map(os.path.abspath, existing_files)

    if is_lyx and option_type == '-e' and option_setting == 'pdf2' \
              and source_exists:
        out_path = re.sub('lyx$', 'pdf', source, flags = re.I)
        with open(out_path, 'wb') as out_file:
            out_file.write('Mock .pdf output')

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

    option1_type = re.findall('^(-\w+)', option1)[0]
    interaction  = re.findall('\s(\S+)', option1)[0]
    option2_type = re.findall('^(-\w+)', option2)[0]
    target_file  = re.findall('\s(\S+)', option2)[0]

    is_pdflatex  = bool(re.search('^pdflatex$', executable, flags = re.I))

    # As long as output is redirected, create a log
    if log_redirect:
        log_path = re.sub('>\s*', '', log_redirect)
        with open(log_path, 'wb') as log_file:
            log_file.write('Test log\n')

    # If pdflatex is the executable, the options are correctly specified,
    # and the source exists, produce a .pdf file with the name specified in
    # the -jobname option.

    # Mock a list of the files that pdflatex sees as existing
    # source_exists should be True only if the source script
    # specified in the system command belongs to existing_files.
    existing_files = ['test_script.tex', './input/latex_test_file.tex']
    source_exists  = os.path.abspath(source) in \
                     map(os.path.abspath, existing_files)

    if is_pdflatex and source_exists and option1_type == '-interaction' and option2_type == '-jobname':
        with open('%s.pdf' % target_file, 'wb') as out_file:
            out_file.write('Mock .pdf output')
        with open('%s.log' % target_file, 'wb') as out_file:
            out_file.write('Mock .log output')

def make_call_side_effect(text):
    '''
    Intended for mocking the subprocess.call() in testing
    _release_tools.up_to_date(). Return a side effect that
    prints text to mocked function's stdout argument.
    '''
    def side_effect(*args, **kwargs):
        log = kwargs['stdout']
        log.write(text)
        
    return side_effect


def upload_asset_side_effect(*args, **kwargs):
    '''
    This side effect, intended for mocking 
    _release_tools.upload_asset() in testing release(), 
    copies an asset so it can be checked by tests. 
    '''
    assets_path    = kwargs['file_name']
    shutil.copyfile(assets_path, 'assets_listing.txt')    


def post_side_effect(*args, **kwargs):
  '''
  Intended for mocking requests.session.post in testing release().
  This side effect returns a MagicMock that raises an error 
  when its raise_for_status() method is called unless
  a specific release_path is specified.
  '''
  # The release path is specified by the first positional argument.
  mock_output = mock.MagicMock(raise_for_status = mock.MagicMock())
  release_path = args[0]
  real_path = "https://test_token:@api.github.com/repos/org/repo/releases"

  def raise_http_error():
      raise requests.exceptions.HTTPError('404 Client Error')

  if release_path != real_path:
      mock_output.raise_for_status.side_effect = raise_http_error

  return mock_output  


def dot_git_open_side_effect(repo   = 'repo',
                             org    = 'org',
                             branch = 'branch',
                             url    = True):
    '''
    This function produces a side effect mocking the behaviour of
    open() when used to read the lines of the 'config' or 'HEAD' file
    of a GitHub repository's '.git' directory.
    '''
    def open_side_effect(*args, **kwargs):
        path = args[0]
        if path not in ['.git/config', '.git/HEAD']:
            raise Exception('Cannot open %s' % path)

        # If specified by the url argument, include the url of the origin
        # in the mock .git file, as is standard. 
        github_url = '\turl = https://github.com/%s/%s\n' % (org, repo)
        github_url = ['', github_url][int(url)]

        if path == '.git/config':
            # These are the mocked contents of a .git/config file
            lines = ['[core]\n', 
                         '\trepositoryformatversion = 0\n', 
                         '\tfilemode = true\n', 
                         '\tbare = false\n', 
                         '\tlogallrefupdates = true\n', 
                         '\tignorecase = true\n', 
                         '\tprecomposeunicode = true\n', 
                     '[remote "origin"]\n', 
                         github_url, 
                         '\tfetch = +refs/heads/*:refs/remotes/origin/*\n', 
                     '[branch "master"]\n', 
                         '\tremote = origin\n', 
                     '\tmerge = refs/heads/master\n']

        elif path == '.git/HEAD':
            # These are the mocked contents of a .git/HEAD file
            lines = ['ref: refs/heads/%s\n' % branch]

        # Ultimately return a mock whose readlines() method
        # just returns a list of lines from our mocked-up file.
        file_object = mock.MagicMock(readlines = lambda: lines)

        return file_object

    return open_side_effect

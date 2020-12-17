import sys
import subprocess
import pkg_resources

import misc
from _exception_classes import PrerequisiteError


def check_prereq(prereq, manual_execs = {}, gslab_vers = None):
    '''
    Check if the prerequisites for prereq are satisfied.
    If prereq is a program, check that its executable is in the path.
    If prereq is (gslab_)python, check that it is the appropriate version.
    If prereq is git_lfs, check that it has been installed.
    '''
    prereq_clean = str(prereq).lower().strip()
    path_checkers = ['r', 'stata', 'matlab', 'lyx', 'latex']
    if prereq_clean in path_checkers:
        executable = misc.get_executable(prereq_clean, manual_execs)
        if not misc.is_in_path(executable):
            message = 'Cannot find executable for %s in PATH.' % prereq_clean
            raise PrerequisiteError(message)
    elif prereq_clean == 'python':
        if sys.version_info[0] != 2:
            raise PrerequisiteError('Please use Python 2')
    elif prereq_clean == 'gslab_python':
        required_version  = process_gslab_version(gslab_vers)
        installed_version = pkg_resources.get_distribution('gslab_tools').version
        installed_version = process_gslab_version(installed_version)
        if check_gslab_version(required_version, installed_version):
            message = 'Your version of gslab_python (%s) is outdated. ' \
                      'This repository requires gslab_python (%s) or higher to run' \
                      % ('.'.join(str(v) for v in installed_version), '.'.join(str(v) for v in required_version))
            raise PrerequisiteError(message)
    elif prereq_clean == 'git_lfs':
        check_git_lfs()
    else:
        message = 'Cannot find prerequisite check for %s' % prereq
        raise PrerequisiteError(message)
    return None


def process_gslab_version(gslab_version):
    '''
    Split semantically versioned gslab_version number at `.`.
    '''
    try:
        vers = gslab_version.split('.')
    except:
        message = 'You must pass gslab_version as a string value.'
        raise PrerequisiteError(message)
    if len(vers) != 3:
        message = 'The gslab_version argument must have exactly two periods `.` ' \
                  'to correspond to semantic versioning.'
        raise PrerequisiteError(message)
    try:
        vers = [int(val) for val in vers]
    except ValueError:
        message = 'All components of gslab_version between periods ' \
                  'must be expressable as integers.'
        raise PrerequisiteError(message)
    return vers


def check_gslab_version(required, installed):
    '''
    Check (recursively) that installed gslab_python version meets or exceeds the required.
    '''
    # Base case
    if required == installed:
        return False
    else:
        required_val = required[0]
        installed_val = installed[0]
        # More base cases
        if required_val > installed_val:
            out_dated = True
        else:
            out_dated = False
        # Recursive case
        if required_val == installed_val:
            out_dated = check_gslab_version(required[1:], installed[1:])
    return out_dated


def check_git_lfs():
    '''
    Check that a valid git-lfs is installed by trying to start it.
    '''
    try:
        _ = subprocess.check_output('git lfs install', shell = True)
    except subprocess.CalledProcessError:
        try:
            _ = subprocess.check_output('git lfs init', shell = True)
        except subprocess.CalledProcessError:
            message = "Either Git LFS is not installed " \
                      "or your Git LFS settings need to be updated. " \
                      "Please install Git LFS or run " \
                      "'git lfs install --force' if prompted above."
            raise PrerequisiteError(message)
    return None

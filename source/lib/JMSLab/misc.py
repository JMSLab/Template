import os
import sys
import datetime

from pathlib import Path
from .builders.executables import get_executable_path


def is_scons_dry_run(cl_args_list = []):
    '''
    Determine if SCons is executing as a dry run based on the command line arguments.
    '''
    dry_run_terms = {'--dry-run', '--recon', '-n', '--just-print'}
    is_dry_run = bool(dry_run_terms.intersection(set(cl_args_list)))
    return is_dry_run


def is_unix():
    '''
    This function return True if the user's platform is Unix and false
    otherwise.
    '''
    unix = ['darwin', 'linux', 'linux2']
    return sys.platform in unix


def is_64_windows():
    '''
    This function return True if the user's platform is Windows (64 bit)
    and False otherwise.
    '''
    return 'PROGRAMFILES(X86)' in os.environ


def is_in_path(program):
    '''
    Wrapper for get_executable_path; used in Stata tests
    '''
    exe = get_executable_path(program)
    return exe if exe else False


def make_list_if_string(source):
    '''Convert a string input into a singleton list containing that string.'''
    if not isinstance(source, list):
        if isinstance(source, str):
            source = [source]
        else:
            message = "SCons source/target input must be either list or string. " + \
                      "Here, it is %s, a %s." % (
                          str(source), str(type(source)))
            raise TypeError(message)
    return source


def current_time():
    '''Return the current time in a Y-M-D H:M:S format.'''
    now = datetime.datetime.now()
    return datetime.datetime.strftime(now, '%Y-%m-%d %H:%M:%S')


def get_directory(path):
    '''
    Determine the directory of a file. This function returns
    './' rather than '' when `path` does not include a directory.
    '''
    directory = os.path.dirname(path)
    if directory == '':
        directory = './'
    return directory


def finder(rel_parent_dir, pattern, excluded_dirs=[], files_only=False):
    '''
    Recursively find all files and directories matching pattern in
    rel_parent_dir, excluding matches in certain directories.
    '''
    out_paths = []
    excluded_dirs = list(map(Path, excluded_dirs))
    for out in Path(rel_parent_dir).glob(f"**/{pattern}"):
        exclude = any(excluded in out.parents for excluded in excluded_dirs)
        is_file = out.is_file() or not files_only
        if is_file and not exclude:
            out_paths += [str(out)]

    return out_paths

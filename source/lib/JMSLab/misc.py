import os
import sys
import subprocess
import datetime
import shutil
import fnmatch

from textwrap import dedent
from pathlib import Path

from . import _exception_classes
from .builders.executables import get_executables


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
    This general helper function checks whether `program` exists in the
    user's path environment variable.
    '''
    if shutil.which(program):
        return shutil.which(program)
    elif os.access(str(Path(program).expanduser().resolve()), os.X_OK):
        return str(Path(program).expanduser().resolve())
    else:
        for path in os.environ['PATH'].split(os.pathsep):
            path = path.strip("'")
            exe  = str(Path(path) / program)
            if os.access(exe, os.X_OK):
                return exe

            exe += ".exe"
            if os.access(exe, os.X_OK):
                return exe

    return False


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


def get_executable(language_name, manual_executables = {}):
    '''
    Get executable stored at language_name of dictionary manual_executables.
    If key doesn't exist, use a default.
    '''
    lower_name = language_name.lower().strip()
    manual_executables = {str(k).lower().strip(): str(v).lower().strip()
                          for k, v in manual_executables.items()}
    manual_executables = {k: v for k, v in manual_executables.items()
                          if k and v and v not in ['none', 'no', 'false', 'n', 'f']}
    default_executables = get_executables(languages = [lower_name])

    try:
        executable = manual_executables[lower_name]
    except KeyError:
        has_default_executable = lower_name in default_executables.keys()
        if not has_default_executable:
            error_message = dedent(f"""
                Cannot find default executable for language: {language_name}.
                Try specifying a default by defining the environment variable

                    JMSLAB_EXE_{lower_name.upper().replace(' ', '_')}
            """)

            raise _exception_classes.PrerequisiteError(error_message)

        executable = default_executables[lower_name]

    return executable


def finder(rel_parent_dir, pattern, excluded_dirs=[]):
    '''
    A nice wrapper for the commands `find` (MacOS) and `dir` (Windows)
    that allow excluded directories.
    '''

    if is_unix():
        command = 'find %s' % (rel_parent_dir)
        exclude_opt = ''
        if len(excluded_dirs) > 0:
            for x in excluded_dirs:  # add in args to exclude folders from search
                # see https://stackoverflow.com/questions/4210042/exclude-directory-from-find-command/16595367
                exclude_opt = '%s -path "*%s*" -prune -o ' % (
                    exclude_opt, os.path.normpath(x))
        command = '%s %s -name "%s" -type f' % (command, exclude_opt, pattern)

    else:
        command = 'dir "%s" /b/s' % os.path.join(rel_parent_dir, pattern)
        for x in excluded_dirs:
            command = '%s | find ^"%s^" /v /i ' % (
                command, os.path.normpath(x))

    try:
        out_paths = subprocess.check_output(
            command, shell=True).decode().replace('\r\n', '\n')
        out_paths = out_paths.split('\n')
        # Strip paths and keep non-empty
        out_paths = filter(bool, map(str.strip, out_paths))
        out_paths = fnmatch.filter(out_paths, pattern)
    except subprocess.CalledProcessError:
        out_paths = []

    return out_paths

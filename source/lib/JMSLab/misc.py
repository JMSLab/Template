import os
import re
import sys
import subprocess
import datetime
import yaml
import shutil
import getpass
import fnmatch

from textwrap import dedent
from pathlib import Path

from . import _exception_classes
from .builders.executables import get_executables


def make_heading(s):
    '''
    Wrap s in a bunch of equals signs for nice heading printing
    '''
    equals_signs = '=' * 35
    out = '%s\n\n *** %s ***\n\n%s\n' % (equals_signs, s, equals_signs)
    return out


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
    elif os.access(Path(program).expanduser().resolve(), os.X_OK):
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


def lyx_scan(node, env, path):
    contents = node.get_contents()
    SOURCE = []
    for ext in env.EXTENSIONS:
        src_find = re.compile(r'filename\s(\S+%s)' % ext, re.M)

        SOURCE = SOURCE + [source.replace('"', '')
                           for source in src_find.findall(contents)]

    return SOURCE


def load_yaml_value(path, key):
    '''
    Load the yaml value indexed by the key argument in the file
    specified by the path argument.
    '''
    if key == "stata_executable":
        prompt = "Enter %s or None to search for defaults: "
    elif key == "github_token":
        prompt = "(Optional) Enter %s to be stored in config_user.yaml.\n"
        prompt = prompt + "Github token can also be entered without storing to file later:"
    else:
        prompt = "Enter %s: "

    # Check if file exists and is not corrupted. If so, load yaml contents.
    yaml_contents = None
    if os.path.isfile(path):
        try:
            yaml_contents = yaml.load(open(path, 'r'))
            if not isinstance(yaml_contents, dict):
                raise yaml.scanner.ScannerError()

        except yaml.scanner.ScannerError:
            message = "%s is a corrupted yaml file. Delete file and recreate? (y/n) "
            response = str(input(message % path))
            if response.lower() == 'y':
                os.remove(path)
                yaml_contents = None
            else:
                message = "%s is a corrupted yaml file. Please fix." % path
                raise _exception_classes.PrerequisiteError(message)

    # If key exists, return value. Otherwise, add key-value to file.
    try:
        if yaml_contents[key] == "None":
            return None
        else:
            return yaml_contents[key]
    except:
        with open(path, 'ab') as f:
            if key == "github_token":
                val = getpass.getpass(prompt=(prompt % key))
            else:
                val = str(input(prompt % key))
            if re.sub('"', '', re.sub('\'', '', val.lower())) == "none":
                val = None
            f.write('%s: %s\n' % (key, val))
        return val


def check_and_expand_path(path):
    error_message = " The directory provided, '%s', cannot be found. " % path + \
                    "Please manually create before running " + \
                    "or fix the path in config_user.yaml.\n"
    try:
        path = os.path.expanduser(path)
        if not os.path.isdir(path):
            raise _exception_classes.PrerequisiteError(error_message)
        return path
    except:
        raise _exception_classes.PrerequisiteError(error_message)


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

                    JMSLAB_EXE_{lower_name.upper()}
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
            command, shell=True).replace('\r\n', '\n')
        out_paths = out_paths.split('\n')
        # Strip paths and keep non-empty
        out_paths = filter(bool, map(str.strip, out_paths))
        out_paths = fnmatch.filter(out_paths, pattern)
    except subprocess.CalledProcessError:
        out_paths = []

    return out_paths


def add_two_dict_keys(d = {}, common_key = '', key1 = 'global', key2 = 'user'):
    '''
    Combine items of d[key1][common_key] and d[key2][common_key] for dictionary d.
    Overwrites repeated values at key1 by key2.
    '''
    try:
        items1 = d[key1][common_key].items()
    except (KeyError, TypeError):
        items1 = []
    try:
        items2 = d[key2][common_key].items()
    except (KeyError, TypeError):
        items2 = []
    items = dict(items1 + items2)
    if not items:
        message = 'Inappropriate input values: `d` must be a dictionary, and ' \
                  'at least one of `d[%s][%s]` and `d[%s][%s]` ' \
                  'must be a dictionary as well.' % (key1, common_key, key2, common_key)
        raise _exception_classes.PrerequisiteError(message)
    return items


def flatten_dict(d, parent_key = '', sep = ':',
                 safe_keys = True, skip_keys = ()):
    '''
    Recursively flatten nested dictionaries. Default sep between keys is ':'.
    Using safe_keys avoids overwriting values assigned to the same key
    in the flattened dict. Does so by adding _(`times repeated`) to the key.
    Keeps track of repeated keys using the skip_keys argument.
    '''
    items = []
    for key, val in sorted(d.items()):
        # Create name of new key
        if parent_key:
            prefix = parent_key + sep
        else:
            prefix = ''
        new_key = prefix + key
        # If safe_keys is True, give new key a unique name and record it.
        if not safe_keys:
            pass
        else:
            if new_key in skip_keys:
                new_key_base = new_key.split('_')[0]
                # Regex for new_key optionally folowed by underscore
                # and some digits. Then string must end.
                key_regex = re.compile(r'%s(?:_\d+)?$' % new_key_base)
                num_same_keys = len([True for skip_key in skip_keys
                                     if bool(key_regex.match(skip_key))])
                if num_same_keys > 0:
                    new_key = '%s_%s' % (new_key_base, num_same_keys)
                else:
                    pass
            else:
                pass
            skip_keys += (new_key,)
        try:  # Recursive case
            items.extend(flatten_dict(val, parent_key = new_key,
                                      skip_keys = skip_keys).items())
        except AttributeError:  # Base case
            items.append((new_key, val))

    return dict(items)

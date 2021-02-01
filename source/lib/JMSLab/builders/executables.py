from textwrap import indent, dedent
from pathlib import Path
from shutil import which

import yaml
import os

from .._exception_classes import PrerequisiteError

EXE_FILE = Path(__file__).resolve().parents[0] / 'executables.yml'


def get_executable(language_name, manual_executables = {}):
    '''
    Get executable stored at language_name of dictionary manual_executables.
    If key doesn't exist, use a default.
    '''
    lower_name = language_name.lower().strip()
    manual_executables = {str(k).lower().strip(): str(v).strip()
                          for k, v in manual_executables.items()}
    manual_executables = {k: v for k, v in manual_executables.items()
                          if k and v and v.lower() not in ['none', 'no', 'false', 'n', 'f']}
    default_executables = get_default_executables(languages = [lower_name])

    if lower_name in manual_executables.keys():
        executable = manual_executables[lower_name]
    elif lower_name in default_executables.keys():
        executable = default_executables[lower_name]
    else:
        error_message = dedent(f"""
            Cannot find executable for language: {language_name}. Pass
            an executable manually or specify a default by defining the
            environment variable

                JMSLAB_EXE_{lower_name.upper().replace(' ', '_')}
        """)

        raise PrerequisiteError(error_message)

    if not get_executable_path(executable):
        print_executable_warnings([[lower_name, executable]])

    return quote_str(executable)


def get_default_executables(efile = EXE_FILE, languages = [], warn = False):
    warn_languages = []
    with open(efile, 'r') as e:
        executables = yaml.safe_load(e)
        for lang in list(executables.keys()) + languages:
            ENV = f'JMSLAB_EXE_{lang.replace(" ", "_")}'.upper()
            if ENV in os.environ:
                executables[lang] = os.environ[ENV]

    for lang, program in executables.items():
        if not get_executable_path(program):
            warn_languages += [[lang, program]]

    if warn:
        print_executable_warnings(warn_languages)

    return executables


def get_executable_path(program):
    '''
    Check if `program` is executable and return full path.

    1. Check user's PATH (first checked by shutil.which):

        - e.g. an executable in the user's path, like "matlab"

    2. Check full/relative path or current directory:

        - e.g. "/path/to/matlab" or "./relative/path/to/matlab"; if
          "matlab" is passed and is not in the user's PATH, then
          "./matlab" is checked.

    3. In the user's path environment variable (fallback):

        - If the executable is not found by shutil.which or by its
          full/relative path, then we check each directory in the
          user's path to see whether the executable is there (this is a
          manually coded fallback to shutil.which).

    Note if the program exists but is not executable then this search
    will also fail.
    '''

    exe_global = which(program)
    exe_local  = str(Path(program).expanduser().resolve())

    if exe_global:
        return exe_global
    elif os.access(exe_local, os.X_OK):
        return exe_local
    else:
        for path in os.environ['PATH'].split(os.pathsep):
            path = path.strip("'")
            exe  = str(Path(path, program))
            if os.access(exe, os.X_OK):
                return exe

            # Windows fallback
            exe += ".exe"
            if os.access(exe, os.X_OK):
                return exe

    return ''


def print_executable_warnings(warn_languages):
    if len(warn_languages):
        s    = "s" if len(warn_languages) > 1 else ""
        maxl = 0
        for lang, program in warn_languages:
            maxl = max(maxl, len(lang))

        fmt = f"%-{maxl + 1}s %s"
        warn_fmt = []
        for (lang, program) in warn_languages:
            warn_fmt += [fmt % (lang + ':', program)]

        warn = dedent(f"""
            WARNING: Executable{s} not found or not executable.

            %s
        """) % indent(os.linesep.join(warn_fmt), '    ')
        print(warn)


def quote_str(x, quotechar = '"', contains = None):
    not_quoted = not (x.startswith(quotechar) or x.endswith(quotechar))
    x_contains = True if contains is None else x.find(contains) >= 0
    return quotechar + x + quotechar if not_quoted and x_contains else x

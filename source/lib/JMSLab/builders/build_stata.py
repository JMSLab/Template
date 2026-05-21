import subprocess  # noqa: F401 — required for test mocking
import shutil
import sys
import os
import re

from .jmslab_builder import JMSLabBuilder
from .._exception_classes import BadExtensionError, PrerequisiteError
from .. import misc


def build_stata(target, source, env):
    '''
    Build targets with a Stata command

    This function executes a Stata script to build objects specified
    by target using the objects specified by source.

    Parameters
    ----------
    target: string or list
        The target(s) of the SCons command.
    source: string or list
        The source(s) of the SCons command. The first source specified
        should be the Stata .do script that the builder is intended to execute.
    env: SCons construction environment, see SCons user guide 7.2
    '''
    builder_attributes = {
        'name': 'Stata',
        'valid_extensions': ['.do']
    }
    builder = StataBuilder(target, source, env, **builder_attributes)
    builder.execute_system_call()
    return None


class StataBuilder(JMSLabBuilder):
    '''
    '''
    def __init__(self, target, source, env, name = '', valid_extensions = []):
        '''
        '''
        exec_opts = self.add_executable_options()
        super(StataBuilder, self).__init__(target, source, env, name = name,
                                           exec_opts = exec_opts,
                                           valid_extensions = valid_extensions)

    def check_code_extension(self):
        super(StataBuilder, self).check_code_extension()
        stem = os.path.splitext(os.path.basename(self.source_file))[0]
        if '.' in stem:
            raise BadExtensionError('Periods disallowed in .do file stems to avoid log file collision.')

    def add_log_file(self):
        super(StataBuilder, self).add_log_file()
        self.final_log_file = os.path.normpath(self.log_file)
        log_file = os.path.splitext(os.path.basename(self.source_file))[0]
        log_file = '%s.log' % log_file
        self.log_file = os.path.normpath(log_file)
        return None

    def _move_stata_log(self):
        '''
        Move Stata's native log into the shared per-script log location.
        '''
        if self.log_file != self.final_log_file and os.path.isfile(self.log_file):
            shutil.move(self.log_file, self.final_log_file)
        self.log_file = self.final_log_file
        return None

    def add_executable_options(self):
        platform_options = {
            'darwin': ' -e',
            'linux':  ' -b',
            'linux2': ' -b',
            'win32':  ' /e do '
        }
        try:
            options = platform_options[sys.platform]
        except KeyError:
            message = 'Cannot find Stata command line syntax for platform %s.' % sys.platform
            raise PrerequisiteError(message)
        return options

    def add_call_args(self):
        '''
        '''
        args = '%s %s' % (os.path.normpath(self.source_file), self.cl_arg)
        self.call_args = args
        return None

    def raise_system_call_exception(self, command = '', traceback = ''):
        self._move_stata_log()
        super(StataBuilder, self).raise_system_call_exception(command = command,
                                                              traceback = traceback)
        return None

    def execute_system_call(self):
        self.check_code_extension()
        self.start_time = misc.current_time()
        self.do_call()
        self._move_stata_log()
        with open(self.log_file) as f:
            log = f.read()
        stata_runtime_error_code = re.compile(r'\br\([1-9]\d*\);')
        if re.search(stata_runtime_error_code, log):
            self.raise_system_call_exception()
        self.check_targets()
        self.timestamp_log(misc.current_time())
        return None

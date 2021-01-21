import subprocess
import sys
import os

from .. import misc
from .jmslab_builder import JMSLabBuilder
from .._exception_classes import PrerequisiteError


def build_matlab(target, source, env):
    '''
    Build targets with a MATLAB command

    This function executes a MATLAB function to build objects
    specified by target using the objects specified by source.
    It requires MATLAB to be callable from the command line
    via `matlab`.

    Accessing command line arguments from within matlab is
    possible via the `command_line_arg = getenv('CL_ARG')`.
    '''
    builder_attributes = {
        'name': 'MATLAB',
        'valid_extensions': ['.m'],
    }
    builder = MatlabBuilder(target, source, env, **builder_attributes)
    builder.execute_system_call()
    return None


class MatlabBuilder(JMSLabBuilder):
    '''
    '''
    def __init__(self, target, source, env, name = '', valid_extensions = []):
        '''
        '''
        exec_opts = self.add_executable_options()
        super(MatlabBuilder, self).__init__(target, source, env, name = name,
                                            exec_opts = exec_opts,
                                            valid_extensions = valid_extensions)

    def add_executable_options(self):
        '''
        '''
        if misc.is_unix():
            platform_option = '-nodesktop '
        elif sys.platform == 'win32':
            platform_option = '-minimize -wait '
        else:
            message = 'Cannot find MATLAB command line syntax for platform.'
            raise PrerequisiteError(message)
        options = ' -nosplash %s -r' % platform_option
        return options

    def add_call_args(self):
        '''
        '''
        self.exec_file = os.path.normpath(self.source_file)
        args = '%s > %s' % (os.path.normpath(self.exec_file), os.path.normpath(self.log_file))
        self.call_args = args
        return None

    def execute_system_call(self):
        '''
        '''
        os.environ['CL_ARG'] = self.cl_arg
        super(MatlabBuilder, self).execute_system_call()
        return None

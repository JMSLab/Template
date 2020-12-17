import os
import shutil
import sys

import gslab_scons.misc as misc
from gslab_builder import GSLabBuilder

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

class StataBuilder(GSLabBuilder):
    '''
    '''
    def __init__(self, target, source, env, name = '', valid_extensions = []):
        '''
        '''
        exec_opts = self.add_executable_options()
        super(StataBuilder, self).__init__(target, source, env, name = name,
                                           exec_opts = exec_opts,
                                           valid_extensions = valid_extensions)


    def add_log_file(self):
        super(StataBuilder, self).add_log_file()
        self.final_sconscript_log = os.path.normpath(self.log_file)
        log_file = os.path.splitext(os.path.basename(self.source_file))[0]
        log_file = '%s.log' % log_file
        self.log_file = os.path.normpath(log_file)
        return None


    def add_executable_options(self):
        platform_options = {
            'darwin': ' -e' ,
            'linux':  ' -b' ,
            'linux2': ' -b' ,
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


    def execute_system_call(self):
        '''
        '''
        super(StataBuilder, self).execute_system_call()
        shutil.move(self.log_file, self.final_sconscript_log)
        return None


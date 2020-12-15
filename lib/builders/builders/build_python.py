import os

from gslab_builder import GSLabBuilder

def build_python(target, source, env):
    '''
    Build SCons targets using a Python script

    This function executes a Python script to build objects specified
    by target using the objects specified by source.

    Parameters
    ----------
    target: string or list 
        The target(s) of the SCons command.
    source: string or list
        The source(s) of the SCons command. The first source specified
        should be the Python script that the builder is intended to execute. 
    env: SCons construction environment, see SCons user guide 7.2
    '''
    builder_attributes = {
        'name': 'Python',
        'valid_extensions': ['.py'],
    }
    builder = PythonBuilder(target, source, env, **builder_attributes)
    builder.execute_system_call()
    return None

class PythonBuilder(GSLabBuilder):
    '''
    '''
    def add_call_args(self):
        '''
        '''
        args = '%s %s > %s' % (os.path.normpath(self.source_file), self.cl_arg, os.path.normpath(self.log_file))
        self.call_args = args
        return None

import os
from gslab_builder import GSLabBuilder


def build_r(target, source, env):
    '''
    Build SCons targets using an R script

    This function executes an R script to build objects specified
    by target using the objects specified by source.

    Parameters
    ----------
    target: string or list 
        The target(s) of the SCons command.
    source: string or list
        The source(s) of the SCons command. The first source specified
        should be the R script that the builder is intended to execute. 
    env: SCons construction environment, see SCons user guide 7.2
    '''
    builder_attributes = {
        'name': 'R',
        'valid_extensions': ['.r'],
        'exec_opts': '--no-save --no-restore --verbose'
    }
    builder = RBuilder(target, source, env, **builder_attributes)
    builder.execute_system_call()
    return None

class RBuilder(GSLabBuilder):
    '''
    '''
    def add_call_args(self):
        '''
        '''
        args = '%s %s > %s 2>&1' % (os.path.normpath(self.source_file), self.cl_arg, os.path.normpath(self.log_file))
        self.call_args = args
        return None

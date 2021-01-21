import subprocess
import os

from .jmslab_builder import JMSLabBuilder


def build_lyx(target, source, env):
    '''Compile a pdf from a LyX file

    This function is a SCons builder that compiles a .lyx file
    as a pdf and places it at the path specified by target.

    Parameters
    ----------
    target: string or list
        The target of the SCons command. This should be the path
        of the pdf that the builder is instructed to compile.
    source: string or list
        The source of the SCons command. This should
        be the .lyx file that the function will compile as a PDF.
    env: SCons construction environment, see SCons user guide 7.2
    '''
    builder_attributes = {
        'name': 'LyX',
        'valid_extensions': ['.lyx'],
        'exec_opts': '-E pdf2'
    }
    builder = LyxBuilder(target, source, env, **builder_attributes)
    builder.execute_system_call()
    return None


class LyxBuilder(JMSLabBuilder):
    '''
    '''
    def add_call_args(self):
        '''
        '''
        args = '%s %s %s > %s' % (self.cl_arg,
                                  os.path.normpath(self.target[0]),
                                  os.path.normpath(self.source_file),
                                  os.path.normpath(self.log_file))
        self.call_args = args
        return None

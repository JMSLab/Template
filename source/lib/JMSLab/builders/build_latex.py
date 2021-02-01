import subprocess
import os

from .jmslab_builder import JMSLabBuilder


def build_latex(target, source, env):
    '''
    Compile a pdf from a LaTeX file

    This function is a SCons builder that compiles a .tex file
    as a pdf and places it at the path specified by target.

    Parameters
    ----------
    target: string or list
        The target of the SCons command. This should be the path
        of the pdf that the builder is instructed to compile.
    source: string or list
        The source of the SCons command. This should
        be the .tex file that the function will compile as a PDF.
    env: SCons construction environment, see SCons user guide 7.2
    '''
    builder_attributes = {
        'name': 'LaTeX',
        'valid_extensions': ['.tex'],
        'exec_opts': '-interaction nonstopmode -jobname'
    }
    builder = LatexBuilder(target, source, env, **builder_attributes)
    builder.execute_system_call()
    return None


class LatexBuilder(JMSLabBuilder):
    '''
    '''
    def add_call_args(self):
        '''
        '''
        target_name = os.path.splitext(self.target[0])[0]
        args = '%s %s %s > %s' % (os.path.normpath(target_name),
                                  os.path.normpath(self.source_file),
                                  self.cl_arg,
                                  os.path.normpath(self.log_file))
        self.call_args = args
        return None

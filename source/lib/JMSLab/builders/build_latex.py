import subprocess
import os
from .. import misc

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
    builder.add_bib_name(source)
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
     
    def add_bib_name(self, source):
        if bool(source):
            sources = misc.make_list_if_string(source)
            source_file = str(sources[0]).split(".")[0]
        else:
            source_file = ''
        self.bib_file = source_file
        return None
    
    def do_call(self):
        '''
        Acutally execute the system call attribute.
        Raise an informative exception on error.
        '''
        self.bibtex_executable  = 'bibtex'
        self.bibtex_system_call = '%s %s' % (self.bibtex_executable, self.bib_file)
        
        traceback = ''
        raise_system_call_exception = False
        try:
            subprocess.check_output(self.system_call, shell = True, stderr = subprocess.STDOUT)
            subprocess.check_output(self.bibtex_system_call, shell = True, stderr = subprocess.STDOUT)
            subprocess.check_output(self.system_call, shell = True, stderr = subprocess.STDOUT)
            subprocess.check_output(self.system_call, shell = True, stderr = subprocess.STDOUT)
        except subprocess.CalledProcessError as ex:
            traceback = ex.output
            raise_system_call_exception = True

        self.cleanup()
        if raise_system_call_exception:
            self.raise_system_call_exception(traceback = traceback)
        return None
        
    
    
     

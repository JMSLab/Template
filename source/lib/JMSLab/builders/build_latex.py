import subprocess
import os

from .. import misc
from .executables import get_executable

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
    builder.execute_system_call(target, source)
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
     
    def add_out_name(self, target):
        if bool(target):
            target        = misc.make_list_if_string(target)
            target_file = os.path.splitext(str(target[0]))[0]
        else:
            target_file   = ''
        self.out_name = target_file
        return None
        
    def check_bib(self, source):
    
        bibext = '.bib'
        bib_file = ''
        
        if bool(source):
            sources = misc.make_list_if_string(source)
            for source_file in sources:
                source_file = str(source_file)
                if source_file.lower().endswith(bibext):
                    bib_file = source_file
        else:
            bib_file = ''  
        self.check_bib = bool(bib_file)
        return None

    def cleanup(self):
        delete_ext = ['.aux', '.lof', '.lot', '.fls', '.out',
                      '.toc', '.bbl','.nav','.vrb','.snm']

        for ext in delete_ext:
            try:
                os.remove(self.out_name+ext)
            except FileNotFoundError:
                continue
            
    def do_call(self, target, source):
        '''
        Acutally execute the system call attribute.
        Raise an informative exception on error.
        '''
        
        self.check_bib(source)
        self.add_out_name(target)

        if self.check_bib:

            self.bibtex_executable  = get_executable('bibtex', manual_executables = {})
            
            self.bibtex_system_call = '%s %s' % (self.bibtex_executable, self.out_name)
                    
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
        else:
            traceback = ''
            raise_system_call_exception = False
            try:
                subprocess.check_output(self.system_call, shell = True, stderr = subprocess.STDOUT)
                subprocess.check_output(self.system_call, shell = True, stderr = subprocess.STDOUT)
                subprocess.check_output(self.system_call, shell = True, stderr = subprocess.STDOUT)
            except subprocess.CalledProcessError as ex:
                traceback = ex.output
                raise_system_call_exception = True
            self.cleanup()
            if raise_system_call_exception:
                self.raise_system_call_exception(traceback = traceback)
     
        return None
        
    def execute_system_call(self, target, source):
        '''
        Execute the system call attribute.
        Log the execution.
        Check that expected targets exist after execution.
        '''
        self.check_code_extension()
        self.start_time = misc.current_time()
        self.do_call(target, source)
        self.check_targets()
        self.timestamp_log(misc.current_time())
        return None
    
     

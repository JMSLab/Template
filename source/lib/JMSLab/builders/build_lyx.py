import subprocess
import os
import shutil
import fileinput

from .. import misc
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
    builder.create_handout()
    builder.execute_system_call()
    return None


class LyxBuilder(JMSLabBuilder):
    '''
    '''
    def add_call_args(self):
        '''
        '''
        args = '%s %s %s > %s' % (os.path.normpath(self.target[0]),
                                  os.path.normpath(self.source_file),
                                  self.cl_arg,
                                  os.path.normpath(self.log_file))
        self.call_args = args
        return None

    def create_handout(self):
        '''
        Converts notes to greyedout for export to handout
        '''

        source_name = os.path.splitext(str(self.source_file))[0]
        target_name = os.path.splitext(str(self.target[0]))[0]
        
        handout_doc_suffix = '_handout'
        handout_doc_input  = source_name + handout_doc_suffix + '.lyx'
        handout_doc_output = target_name + handout_doc_suffix + '.pdf'

        shutil.copy2(self.source_file, handout_doc_input)
        beamer = False
        for line in fileinput.input(handout_doc_input, inplace = True):
            if r'\textclass beamer' in line:
                beamer = True
            elif r'\begin_inset Note Note' in line and beamer:
                line = line.replace('Note Note', 'Note Greyedout')
            print(line)
        
        args = '%s %s %s > %s' % (handout_doc_output,
                               handout_doc_input,
                                self.cl_arg,
                               os.path.normpath(self.log_file))
        
        self.handout_args = args

        self.handout_call = '%s %s %s' % (self.executable, self.exec_opts, self.handout_args)
        subprocess.check_output(self.handout_call, shell = True, stderr = subprocess.STDOUT)


def do_call(self):
    '''
    Acutally execute the system call attribute.
    Raise an informative exception on error.
    '''
    
    traceback = ''
    raise_system_call_exception = False
    try:
        subprocess.check_output(self.system_call, shell = True, stderr = subprocess.STDOUT)
    except subprocess.CalledProcessError as ex:
        traceback = ex.output
        raise_system_call_exception = True

    self.cleanup()
    if raise_system_call_exception:
        self.raise_system_call_exception(traceback = traceback)
    return None

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
    builder.execute_system_call(target, env)
    return None


class LyxBuilder(JMSLabBuilder):
    
    def add_call_args(self):
        args = '%s %s %s > %s' % (os.path.normpath(self.target[0]),
                                  os.path.normpath(self.source_file),
                                  self.cl_arg,
                                  os.path.normpath(self.log_file))
        self.call_args = args
        return None


    def create_handout(self, target, env):
        '''
        Converts notes to greyedout for export to handout
        '''
        file = str((misc.make_list_if_string(target))[0])
        file_root = os.path.splitext(file)[0]
        file_ext = os.path.splitext(file)[1]
        handout_suffix = "_handout"
        
        self.handout_doc_output =  file_root + handout_suffix + file_ext
        self.handout_doc_input  = file_root + handout_suffix + '.lyx'

        shutil.copy2(self.source_file, self.handout_doc_input)
        beamer = False
        for line in fileinput.input(self.handout_doc_input, inplace = True):
            if r'\textclass beamer' in line:
                beamer = True
            elif r'\begin_inset Note Note' in line and beamer:
                line = line.replace('Note Note', 'Note Greyedout')
            print(line)
        
        args = '%s %s %s > %s' % (self.handout_doc_output,
                                self.handout_doc_input,
                                self.cl_arg,
                                os.path.normpath(self.log_file))
        
        self.handout_args = args
        self.handout_call = '%s %s %s' % (self.executable, self.exec_opts, self.handout_args)

        return None


    def cleanup_handout(self):
        os.remove(self.handout_doc_input)
        shutil.move(self.handout_doc_output, 'temp/' + os.path.split(self.handout_doc_output)[1])
        return None


    def do_call(self, target, env):
        '''
        Acutally execute the system call attribute.
        Raise an informative exception on error.
        '''
        if bool(env['HANDOUT_BOOL']):
            self.create_handout(target, env)
            traceback = ''
            raise_system_call_exception = False
            try:
                subprocess.check_output(self.handout_call, shell = True, stderr = subprocess.STDOUT)
            except subprocess.CalledProcessError as ex:
                traceback = ex.output
                raise_system_call_exception = True

            self.cleanup_handout()
            if raise_system_call_exception:
                self.raise_system_call_exception(traceback = traceback)
        else:
            pass

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
    
    
    def execute_system_call(self, target, env):
        '''
        Execute the system call attribute.
        Log the execution.
        Check that expected targets exist after execution.
        '''
        self.check_code_extension()
        self.start_time = misc.current_time()
        self.do_call(target, env)
        self.check_targets()
        self.timestamp_log(misc.current_time())
        return None
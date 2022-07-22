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
        file_root, file_ext = os.path.splitext(str(self.pdf_target))
        
        self.handout_doc_output =  file_root + env['HANDOUT_SFIX'] + file_ext
        self.handout_doc_input  = file_root + env['HANDOUT_SFIX'] + '.lyx'

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
        
        handout_target_dest = [x for x in self.handout_target if self.handout_doc_output != str(x)]
        for x in handout_target_dest:
            shutil.copy2(self.handout_doc_output, str(x))
        if set(self.handout_target) == set(handout_target_dest):
            os.remove(self.handout_doc_output)
        os.remove(self.handout_doc_input)
        return None


    def do_call(self, target, env):
        '''
        Acutally execute the system call attribute.
        Raise an informative exception on error.
        '''
        #'''
        if bool(env['HANDOUT_SFIX']):
            
            pdf_target = misc.make_list_if_string(target)[0]
            pdf_target_tail = os.path.split(str(pdf_target))[1]
            pdf_target_tail_root, pdf_target_tail_ext = os.path.splitext(pdf_target_tail)
            handout_target_check = pdf_target_tail_root + env['HANDOUT_SFIX'] + pdf_target_tail_ext
            
            handout_target = [x for x in misc.make_list_if_string(target) 
                              if os.path.split(str(x))[1] == handout_target_check]
            
            if bool(handout_target):
                self.pdf_target, self.handout_target = pdf_target, handout_target
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
                raise Exception('The handout_target is empty')
            
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
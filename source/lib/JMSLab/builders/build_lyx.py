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


    def create_handout(self):
        '''
        If beamer document class, convert Lyx notes to greyedout.
        '''
        
        self.handout_out = str(self.main_target)
        self.handout_in  = os.path.splitext(self.source_file)[0] + '.handout.lyx' 

        shutil.copy2(self.source_file, self.handout_in)
        beamer = False
        for line in fileinput.input(self.handout_in, inplace = True):
            if r'\textclass beamer' in line:
                beamer = True
            elif r'\begin_inset Note Note' in line and beamer:
                line = line.replace('Note Note', 'Note Greyedout')
            print(line, end='')
        
        args = '%s %s %s > %s' % (self.handout_out,
                                self.handout_in,
                                self.cl_arg,
                                os.path.normpath(self.log_file))
        
        self.handout_args = args
        self.handout_call = '%s %s %s' % (self.executable, 
                                          self.exec_opts, 
                                          self.handout_args)

        return None


    def cleanup_handout(self):
        '''
        Copy handout pdf to desired locations.
        Remove intermediate files.
        '''
        for x in self.handout_target_list:
            shutil.copy2(self.handout_out, str(x))
        os.remove(self.handout_in)
        return None


    def do_call(self, target, env):
        '''
        Generate handout pdf if handout path exists in target and handout path
        has the correct suffix and/or extension. Raise value error if intended 
        behavior implied by target list contradicts behavior implied by 
        HANDOUT_SFIX.
        
        Always generate main pdf.        
        '''
        
        target_list = misc.make_list_if_string(target)
        handout_sfix = '' if 'HANDOUT_SFIX' not in env else env['HANDOUT_SFIX']
        
        if target_list[0] in target_list[1:]:
            raise ValueError(
                'Error: Duplicate targets')
            
            
        if len(target_list) == 1:
             if bool(handout_sfix):
                 raise ValueError(
                     'Error: HANDOUT_SFIX non-empty but only one target specified.')
        
        elif len(target_list) > 1:

            handout_flag = handout_sfix + '.pdf'
            handout_target_list = [x for x in target_list[1:]
                                   if str(x).lower().endswith(handout_flag.lower())]
                
            if not bool(handout_target_list):
                raise ValueError('Error: No valid targets contain handout suffix.')
            
            self.main_target = target_list[0]
            self.handout_target_list = handout_target_list
            self.create_handout()

            traceback = ''
            raise_system_call_exception = False
            try:
                subprocess.check_output(self.handout_call, 
                                        shell = True, 
                                        stderr = subprocess.STDOUT)
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
            subprocess.check_output(self.system_call, 
                                    shell = True, 
                                    stderr = subprocess.STDOUT)
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


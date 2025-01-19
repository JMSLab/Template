import subprocess
import os
import re
import shutil
import fileinput

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
    builder.add_out_name(target)
    builder.execute_system_call(target, source, env)
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

    def check_handout(self, target, env):

        self.checked_handout = False
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

            self.checked_handout = True

        else:
            pass      

        return None

    def create_handout(self):
        '''
        If beamer document class, show notes.
        '''   

        self.handout_out = os.path.splitext(str(self.main_target))[0]
        self.handout_in  = os.path.splitext(self.source_file)[0] + '.handout.tex' 

        shutil.copy2(self.source_file, self.handout_in)
        beamer = False
        for line in fileinput.input(self.handout_in, inplace = True):
            if bool(re.search(r'\\documentclass.*{beamer}', line)):
                beamer = True
            elif bool(re.search(r'\\setbeameroption.*{hide notes}', line)) and beamer:
                line = line.replace('hide notes', 'show notes')
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
            shutil.copy2(str(self.handout_out) + '.pdf', str(x))
        os.remove(self.handout_in)
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
        self.checked_bib = bool(bib_file)
        return None

    def check_number_of_bibliographies(self):
        """
        After a run with 'pdflatex', this function checks for multiple bibliographies.
        Checks for files matching "[target_name] + '.\d+' + '.aux'" in the path of target file.
        Adds all matching files to a list, using the full relative path and omitting the '.aux' extension.
        """
        aux_ext = ".aux"
        target_name = os.path.basename(self.out_name)
        target_path = os.path.normpath(os.path.dirname(self.out_name))
        pattern = target_name + ".(\d+)" + aux_ext
        aux_list = []
        for f in os.listdir(target_path):
            if bool(re.search(pattern, f)):
                aux_to_add = os.path.join(target_path, os.path.splitext(f)[0])
                aux_list.append(aux_to_add)
        aux_list.sort()
        self.aux_files = aux_list
        self.checked_number_of_bibliographies = bool(aux_list)
        return None

    def cleanup(self):
        out_dir = os.path.normpath(os.path.dirname(self.out_name))
        out_basename = os.path.basename(self.out_name)
        delete_ext = ['.aux', '.lof', '.lot', '.fls', '.out',
                      '.toc', '.bbl', '.blg', '.nav','.vrb','.snm']
        for f in os.listdir(out_dir):
            for ext in delete_ext:
                pattern = out_basename + '(\.\d+)?' + ext
                if re.search(pattern, f):
                    try:
                        os.remove(os.path.join(out_dir,f))
                    except FileNotFoundError:
                        continue

    def do_call(self, target, source, env):
        '''
        Actually execute the system call attribute.
        Raise an informative exception on error.
        '''

        self.check_bib(source) 
        self.check_handout(target, env)

        if self.checked_handout:

            self.cleanup()
            traceback = ''
            raise_system_call_exception = False
            try:
                subprocess.check_output(self.handout_call, shell = True, stderr = subprocess.STDOUT)
                self.check_number_of_bibliographies()
                if self.checked_bib:
                    self.bibtex_executable  = get_executable('bibtex')
                    if self.checked_number_of_bibliographies:
                        for f in self.aux_files:
                            self.bibtex_system_call = '%s %s' % (self.bibtex_executable, f)
                    else:
                        self.bibtex_system_call = '%s %s' % (self.bibtex_executable, self.out_name) 
                    subprocess.check_output(self.bibtex_system_call, shell = True, stderr = subprocess.STDOUT)
                subprocess.check_output(self.handout_call, shell = True, stderr = subprocess.STDOUT)
                subprocess.check_output(self.handout_call, shell = True, stderr = subprocess.STDOUT)
            except subprocess.CalledProcessError as ex:
                traceback = ex.output
                raise_system_call_exception = True

            self.cleanup_handout()
            self.cleanup()
            if raise_system_call_exception:
                self.raise_system_call_exception(traceback = traceback)

        self.cleanup()
        traceback = ''
        raise_system_call_exception = False
        try:
            subprocess.check_output(self.system_call, shell = True, stderr = subprocess.STDOUT)
            self.check_number_of_bibliographies()
            if self.checked_bib:
                self.bibtex_executable  = get_executable('bibtex')
                if self.checked_number_of_bibliographies:
                    for f in self.aux_files:
                        self.bibtex_system_call = '%s %s' % (self.bibtex_executable, f)
                        subprocess.check_output(self.bibtex_system_call, shell = True, stderr = subprocess.STDOUT)
                else:
                    self.bibtex_system_call = '%s %s' % (self.bibtex_executable, self.out_name)  
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

    def execute_system_call(self, target, source, env):
        '''
        Execute the system call attribute.
        Log the execution.
        Check that expected targets exist after execution.
        '''
        self.check_code_extension()
        self.start_time = misc.current_time()
        self.do_call(target, source, env)
        self.check_targets()
        self.timestamp_log(misc.current_time())
        return None

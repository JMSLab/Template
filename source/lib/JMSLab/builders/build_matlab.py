import subprocess
import hashlib
import shutil
import sys
import os
import re

from .. import misc
from .jmslab_builder import JMSLabBuilder
from .._exception_classes import PrerequisiteError


def build_matlab(target, source, env):
    '''
    Build targets with a MATLAB command

    This function executes a MATLAB function to build objects
    specified by target using the objects specified by source.
    It requires MATLAB to be callable from the command line
    via `matlab`.

    Accessing command line arguments from within matlab is
    possible via the `command_line_arg = getenv('CL_ARG')`.
    '''
    builder_attributes = {
        'name': 'MATLAB',
        'valid_extensions': ['.m'],
    }
    builder = MatlabBuilder(target, source, env, **builder_attributes)
    builder.execute_system_call()
    return None


class MatlabBuilder(JMSLabBuilder):
    '''
    '''
    def __init__(self, target, source, env, name = '', valid_extensions = []):
        '''
        '''
        exec_opts = self.add_executable_options()
        super(MatlabBuilder, self).__init__(target, source, env, name = name,
                                            exec_opts = exec_opts,
                                            valid_extensions = valid_extensions)

    def add_executable_options(self):
        '''
        '''
        if misc.is_unix():
            platform_option = '-nodesktop '
        elif sys.platform == 'win32':
            platform_option = '-minimize -wait '
        else:
            message = 'Cannot find MATLAB command line syntax for platform.'
            raise PrerequisiteError(message)
        options = ' -nosplash %s -r' % platform_option
        return options


    def add_call_args(self):
        '''
        Matlab automagically changes the working directory to the directory
        of the script it is executing. Hence we copy the source script to the
        current working directory.
        '''
        source_hash = hashlib.sha1(self.source_file.encode()).hexdigest()
        source_exec = 'source_%s' % source_hash
        exec_file   = source_exec + '.m'
        shutil.copy(self.source_file, exec_file)
        self.exec_file = os.path.normpath(exec_file)

        file_rstrip_pattern(self.exec_file, r'exit(\(\d*\))?\s*[,;]?')

        norm_log  = os.path.normpath(self.log_file)
        norm_base = os.path.dirname(os.path.normpath(self.source_file))
        self.call_args = re.sub(r'\s+', ' ', '''"
            diary('{0}');
            addpath('{1}');
            try,
                {3},
                rc = 0,
            catch me,
                fprintf('%s: %s\\n', me.identifier, me.message),
                rc = 1,
            end,
            diary off;

            fileID = fopen('{2}', 'w');
            if rc,
                fprintf(fileID, '{2} failed; see log file'),
            else,
                fprintf(fileID, '{2} run successfully'),
            end,
            fclose(fileID);
            
            id = feature('getpid');
            if ispc,
                 cmd = sprintf('taskkill /pid %d /f',id),
            elseif (ismac || isunix),
                cmd = sprintf('kill -9 %d',id),
            else,
                error('unknown operating system'),
            end,
            system(cmd);
            
            exit(0);
        "'''.format(norm_log, norm_base, self.exec_file, source_exec), flags = re.MULTILINE)

        return None

    def cleanup(self):
        super(MatlabBuilder, self).cleanup()
        for delete_file in [self.exec_file]:
            try:
                os.remove(delete_file)
            except FileNotFoundError:
                continue

    def execute_system_call(self):
        '''
        '''
        os.environ['CL_ARG'] = self.cl_arg
        super(MatlabBuilder, self).execute_system_call()
        self.cleanup()
        return None
        
    def do_call(self):
        '''
        Special handling for Matlab since we kill it forcefully
        '''
        try:
            subprocess.check_output(self.system_call, shell = True, stderr = subprocess.STDOUT)
        except subprocess.CalledProcessError as ex:
            matlab_msg = self.exec_file + ' run successfully'
            with open(self.exec_file, 'r') as matlab_exit:
                matlab_killed = (matlab_exit.read() == matlab_msg)
            self.cleanup()        
            if not matlab_killed:
                self.raise_system_call_exception(traceback = ex.output)
        return None

def file_rstrip_pattern(file_path, pattern):
    '''
    Strip pattern from end of file. Warning: This is NOT memory-efficient
    but is OK to use on small source code text files.
    '''
    skip = True
    exec_lines = []
    with open(file_path, "r") as fh:
        lines = reversed(list(fh.readlines()))
        for line in lines:
            if line.strip() != '':
                skip = False

            if skip:
                continue

            if re.match(pattern, line.strip()):
                continue

            exec_lines += [line]

    with open(file_path, "w") as fh:
        fh.writelines(reversed(exec_lines))
        

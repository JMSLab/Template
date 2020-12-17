import abc
import os
import subprocess
import sys

import gslab_scons.misc as misc
from gslab_scons._exception_classes import ExecCallError, TargetNonexistenceError, BadExtensionError

class GSLabBuilder(object):
    '''
    Abstract Base Class for custom GSLab SCons builders.
    '''
    __metaclass__ = abc.ABCMeta

    def __init__(self, target, source, env, name = 'GSLab Builder', 
                 valid_extensions = [], exec_opts = ''):
        '''
        Fill builder with information about build step.
        
        Parameters
        ----------
        target: string or list 
            The target(s) of the SCons command.
        source: string or list
            The source(s) of the SCons command. The first source specified
            should be the script that the builder is intended to execute.
        env: SCons construction environment, see SCons user guide 7.2
        name: string
            Name of builder-type. Use to refer to builder in error messages and env.
        valid_extensions: iterable
            Valid (case-insensitive) extensions for first element of source list.
        default_exec: string
            Executable used to execute first element of source list.
            Override by passing value through env.
        exec_opts: string
            Options used to execute first element of source list.
        '''
        # Store keyword args
        self.name             = name
        self.valid_extensions = valid_extensions
        self.exec_opts        = exec_opts
        # Build system call and store components
        self.add_source_file(source)
        self.target           = [str(t) for t in misc.make_list_if_string(target)]
        self.target_dir       = misc.get_directory(self.target[0])
        if 'executable_names' not in env:
            env['executable_names'] = {}
        self.executable       = misc.get_executable(name, env['executable_names'])
        self.env              = env
        self.add_command_line_arg()
        self.add_log_file()
        self.add_call_args()
        self.system_call = '%s %s %s' % (self.executable, self.exec_opts, self.call_args)


    def add_source_file(self, source):
        '''
        Add source file to execute as the first element of source.
        If source is an empty list, then the source file is ''.
        '''
        if bool(source):
            sources = misc.make_list_if_string(source)
            source_file = str(sources[0])
        else:
            source_file = ''
        self.source_file = os.path.normpath("%s" % source_file)
        return None


    def add_command_line_arg(self):
        '''
        Store arguments to pass to the executing script on the command line.

        Return the content of env['CL_ARG'] as a string with spaces separating entries. 
        If env['CL_ARG'] doesn't exist, return an empty string.
        '''
        try:
            cl_arg = self.env['CL_ARG']
        except KeyError:
            cl_arg = ''
        try:
            cl_arg = misc.make_list_if_string(cl_arg)
            cl_arg = ' '.join([str(s) for s in cl_arg])
        except TypeError:
            cl_arg = str(cl_arg)
        self.cl_arg = "%s" % cl_arg
        return None


    def add_log_file(self):
        '''
        Store file to which script execution is logged.
        '''
        try:
            log_ext = '_%s' % self.env['log_ext']
        except KeyError:
            log_ext = ''
        self.log_file = os.path.join(self.target_dir, ('sconscript%s.log' % log_ext))
        return None


    @abc.abstractmethod
    def add_call_args(self):
        '''
        Abstract method to record executable-specific ordering of SCons build step arguments.
        '''
        pass


    def execute_system_call(self):
        '''
        Execute the system call attribute.
        Log the execution.
        Check that expected targets exist after execution.
        '''
        self.check_code_extension()
        start_time = misc.current_time()
        self.do_call()
        self.check_targets()
        end_time =  misc.current_time()    
        self.timestamp_log(start_time, end_time)
        return None


    def check_code_extension(self):
        '''
        Raise an exception if the extension in executing script
        does not mach extension in valid_extensions attribute.
        '''
        extensions = misc.make_list_if_string(self.valid_extensions)
        if extensions == []:
            return None
        matches = [True for extension in extensions 
                   if self.source_file.lower().endswith("%s" % extension)]
        if not matches:
            message = 'First argument, %s, must be a file of type %s.' % (self.source_file, extensions)
            raise BadExtensionError(message)
        return None


    def do_call(self):
        '''
        Acutally execute the system call attribute.
        Raise an informative exception on error.
        '''
        try:
            subprocess.check_output(self.system_call, shell = True, stderr = subprocess.STDOUT)
        except subprocess.CalledProcessError as ex:
            self.raise_system_call_exception(traceback = ex.output)
        return None


    def raise_system_call_exception(self, command = '', traceback = ''):
        '''
        Create and raise an informative error message from failed system call.
        '''
        if not command:
            command = self.system_call
        traceback = str(traceback)
        traceback = '%s%s' % ('\n' * bool(traceback), traceback)
        message = '%s did not run successfully. ' \
                  'Please check that the executable, source, and target files are correctly specified. ' \
                  'Check %s and sconstruct.log for errors. ' \
                  '\nCommand tried: %s%s' % (self.name, self.log_file, command, traceback)
        raise ExecCallError(message)
        return None


    def check_targets(self):
        '''
        Check that all elements of the target attribute after executing system call.
        '''
        missing_targets = [t for t in self.target if not os.path.isfile(t)]
        if missing_targets:
            missing_targets = '\n    '.join(missing_targets)
            message = 'The following target files do not exist after build:\n    %s' % missing_targets
            raise TargetNonexistenceError(message)
        return None


    def timestamp_log(self, start_time, end_time):
        '''
        Adds beginning and ending times to a log file made for system call.
        '''
        with open(self.log_file, mode = 'rU') as f:
            content = f.read()
            f.seek(0, 0)
            builder_log_msg = '*** Builder log created: {%s}\n' \
                              '*** Builder log completed: {%s}\n%s' \
                              % (start_time, end_time, content)
        with open(self.log_file, mode = 'wb') as f:
            f.write(builder_log_msg)
        return None

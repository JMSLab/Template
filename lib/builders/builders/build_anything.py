import os
import copy
import warnings

from gslab_builder import GSLabBuilder
import gslab_scons.misc as misc


def build_anything(target, source, action, env, warning = True, **kw):
    ''' 
    Anything builder-generator. The generator will create a custom builder 
    that runs `action` and add it as a SCons node, similar to the native env.Command.
    Using gslab_scons.build_anything will utilize our logging mechanism
    and error catching similar to our other builders.
    `    
    Parameters
    target: string or list 
        The target(s) of the SCons command. The log ends up in the 
        directory of the first specified target.
    source: string or list
        The source(s) of the SCons command. 
    action: string
        The code to be run by the generated builder.
    env: SCons construction environment, see SCons user guide 7.2.
        You *** MUST *** manually pass `env = env` when calling this in SConscript,
        since this is not a Scons.env method like env.Command.
        Special parameters that can be added when using the builder
        log_ext: string
            Instead of logging to `sconscript.log` in the target dir, 
            the builder will log to `sconscript_<log_ext>.log`.
        origin_log_file: string
            Sometimes, your command may produce a log file in an undesirable location.
            Specifying the that location in this argument leads the builder to append
            the content of origin_log_file to log_file and delete origin_log_file.            
            The builder will crash if this file doesn't exist at the end of the command.
        warning: Boolean
            Turns off warnings if warning = False. 
    '''
    import SCons.Builder
    builder_attributes = {
        'name': 'Anything Builder'
    }
    target = [t for t in misc.make_list_if_string(target) if t]
    source = [s for s in misc.make_list_if_string(source) if s]
    local_env = env.Clone()
    for k, v in kw.items():
        local_env[k] = v
    builder = AnythingBuilder(target, source, action, local_env, warning, **builder_attributes)
    bkw = {
        'action': builder.build_anything,
        'target_factory' : local_env.fs.Entry,
        'source_factory':  local_env.fs.Entry,
    }
    bld = SCons.Builder.Builder(**bkw)
    return bld(local_env, target, source)


class AnythingBuilder(GSLabBuilder):
    '''
    '''
    def __init__(self, target, source, action, env, warning = True, name = ''):
        '''
        '''
        target = [self.to_str(t) for t in target]
        source = [self.to_str(s) for s in source]
        self.action = action
        super(AnythingBuilder, self).__init__(target, source, env, name = name)
        try:
            origin_log_file = env['origin_log_file']
        except KeyError:
            origin_log_file = None
        self.origin_log_file = origin_log_file
        if '>' in action and warning == True:
            warning_message = '\nThere is a redirection operator > in ' \
                              'your prescribed action key.\n' \
                              'The Anything Builder\'s logging mechanism '\
                              'may not work as intended.'
            warnings.warn(warning_message)


    @staticmethod
    def to_str(s):
        '''
        Convert s to string and drop leading `#` if it exists.
        '''
        s = str(s)
        if s and s[0] == '#':
            s = s[1:]
        return s


    def add_call_args(self):
        '''
        '''
        args = '%s > %s 2>&1' % (self.action, os.path.normpath(self.log_file))
        self.call_args = args
        return None


    def build_anything(self, **kwargs):
        '''
        Just a GSLabBuilder execute_system_call method,
        but given a nice name for printing.
        '''
        super(AnythingBuilder, self).execute_system_call()
        if self.origin_log_file is not None:
            with open(log_file, 'ab') as sconscript_log:
                with open(origin_log_file, 'rU') as origin_log:
                    sconscript_log.write(origin_log.read())
            os.remove(origin_log_file)
        return None

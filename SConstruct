# Preliminaries
import os
import sys
import json
import atexit
import source.lib.JMSLab as jms

sys.path.append('config')
sys.dont_write_bytecode = True # Don't write .pyc files

AddOption('--mode', dest='build_mode', type='string', default='full')
mode = GetOption('build_mode')

def resolve_config(source_path, mode):
    src = File(source_path).abspath
    dst = File('#temp/' + source_path.removeprefix('#source/')).abspath
    config = json.load(open(src))
    overrides = config.pop('dev', {})
    if mode == 'dev':
        config.update(overrides)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    json.dump(config, open(dst, 'w'))
    return config

os.environ['PYTHONPATH'] = '.'
env = Environment(ENV = {'PATH' : os.environ['PATH']},
                  IMPLICIT_COMMAND_DEPENDENCIES = 0,
                  BUILDERS = {'R'         : Builder(action = jms.build_r),
                              'Tablefill' : Builder(action = jms.build_tables),
                              'Stata'     : Builder(action = jms.build_stata),
                              'Matlab'    : Builder(action = jms.build_matlab),
                              'Python'    : Builder(action = jms.build_python),
                              'Lyx'       : Builder(action = jms.build_lyx),
                              'Latex'     : Builder(action = jms.build_latex)})

env.Decider('MD5-timestamp') # Only computes hash if time-stamp changed
Export('env', 'mode', 'resolve_config')

jms.start_log('develop', '')

SConscript('source/derived/SConscript')
SConscript('source/analysis/SConscript')
SConscript('source/tables/SConscript')
SConscript('source/figures/SConscript')
SConscript('source/paper/SConscript')
SConscript('source/talk/SConscript')

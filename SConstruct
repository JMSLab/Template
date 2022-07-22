# Preliminaries
import os
import sys
import atexit
import source.lib.JMSLab as jms

sys.path.append('config')
sys.dont_write_bytecode = True # Don't write .pyc files

vars = Variables()
vars.Add('HANDOUT_SFIX', 'Set to string to create handout', '')
env = Environment(variables = vars,
                  ENV = {'PATH' : os.environ['PATH']},
                  IMPLICIT_COMMAND_DEPENDENCIES = 0,
                  BUILDERS = {'R'         : Builder(action = jms.build_r),
                              'Tablefill' : Builder(action = jms.build_tables),
                              'Stata'     : Builder(action = jms.build_stata),
                              'Matlab'    : Builder(action = jms.build_matlab),
                              'Python'    : Builder(action = jms.build_python),
                              'Lyx'       : Builder(action = jms.build_lyx)})

env.Decider('MD5-timestamp') # Only computes hash if time-stamp changed
Export('env')

jms.start_log('develop', '')

SConscript('source/derived/SConscript')
SConscript('source/analysis/SConscript')
SConscript('source/tables/SConscript')
SConscript('source/paper/SConscript')
SConscript('source/talk/SConscript')

# Preliminaries
import os
import sys
import atexit
import gslab_scons as gs

sys.path.append('config')
sys.dont_write_bytecode = True # Don't write .pyc files
 
env = Environment(ENV = {'PATH' : os.environ['PATH']}, 
                  IMPLICIT_COMMAND_DEPENDENCIES = 0,
                  BUILDERS = {'R'         : Builder(action = gs.build_r),
                              'Stata'     : Builder(action = gs.build_stata),
                              'Python'    : Builder(action = gs.build_python),
                              'Lyx'       : Builder(action = gs.build_lyx)})
env.Decider('MD5-timestamp') # Only computes hash if time-stamp changed
Export('env')

gs.start_log('develop', '')

SConscript('source/derived/SConscript')
SConscript('source/paper/SConscript')

import os
import sys
import glob
from datetime import datetime
import subprocess
import shutil
import gslab_scons.misc as misc


def start_log(mode, cl_args_list = sys.argv, log = 'sconstruct.log'):
    '''Begins logging a build process'''
    
    if not (mode in ['develop', 'cache']):
        raise Exception("Error: %s is not a defined mode" % mode)
    elif misc.is_scons_dry_run(cl_args_list = cl_args_list):
        return None

    start_message = "*** New build: {%s} ***\n" % misc.current_time()
    with open(log, "w") as f:
        f.write(start_message)

    if misc.is_unix():
        sys.stdout = os.popen('tee -a %s' % log, 'wb')
    elif sys.platform == 'win32':
        sys.stdout = open(log, 'ab')

    sys.stderr = sys.stdout 

    return None


def end_log(cl_args_list = sys.argv, log = 'sconstruct.log', excluded_dirs = [], 
            release_dir = './release/'):
    '''Complete the log of a build process.'''
    if misc.is_scons_dry_run(cl_args_list = cl_args_list):
        return None

    end_message = "*** Build completed: {%s} ***\n \n \n" % misc.current_time()
    with open(log, "a") as f:
        f.write(end_message)

    # scan sconstruct.log for start time
    with open(log, "rU") as f:
        s = f.readline()
        s = s[s.find('{') + 1: s.find('}')]
        start_time = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")

    # gather all sconscript logs 
    parent_dir = os.getcwd()
    builder_logs = collect_builder_logs(parent_dir, excluded_dirs = excluded_dirs)
    
    # keep only builder logs from this run OR is broken (value == beginning_of_time)
    beginning_of_time    = datetime.min # to catch broken logs (see collect_builder_logs)
    this_run_dict = {key:value for key, value in builder_logs.items() if (value > start_time) or value == beginning_of_time}
    this_run_list = sorted(this_run_dict, key=this_run_dict.get, reverse=True)

    with open(log, "a") as sconstruct:
        for f in this_run_list:
            with open(f, 'rU') as sconscript:
                if this_run_dict[f] == beginning_of_time:
                    warning_string = "*** Warning!!! The log below does not have timestamps," + \
                                     " the Sconscript may not have finished.\n"
                    sconstruct.write(warning_string)
                sconstruct.write(f + '\n')
                sconstruct.write(sconscript.read())

    # move top level logs to /release/ directory.
    if not os.path.exists(release_dir):
        os.makedirs(release_dir)
    for file in glob.glob("*.log"):
        shutil.move('./' + file, release_dir + file)
    return None


def collect_builder_logs(parent_dir, excluded_dirs = []):
    ''' Recursively return dictionary of files named sconscript*.log 
        in parent_dir and nested directories.
        Also return timestamp from those sconscript.log 
        (snippet from SO 3964681)

        excluded_dirs (str or list of str):
            list of directories to be excluded from the search
        '''
    builder_log_collect = {}

    # Store paths to logs in a list, found from platform-specific command line tool 
    rel_parent_dir = os.path.relpath(parent_dir)
    log_name = '*sconscript*.log'
    excluded_dirs = misc.make_list_if_string(excluded_dirs)

    log_paths = misc.finder(rel_parent_dir, log_name, excluded_dirs)

    # Read the file at each path to a log and store output complete-time in a dict at filename
    for log_path in log_paths:
        with open(log_path, 'rU') as f:
            try:
                s = f.readlines()[1] # line 0 = log start time, line 1 = log end time
            except IndexError:
                s = ''
            s = s[s.find('{') + 1: s.find('}')] # find {} time identifier 
            try:
                builder_log_end_time = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
            except ValueError: # if the code breaks, there's no time identifier
                beginning_of_time    = datetime.min
                builder_log_end_time = beginning_of_time
        builder_log_collect[log_path]  = builder_log_end_time

    return builder_log_collect
    

import os
import sys
import scandir
import pymmh3 as mmh3

import misc

def log_paths_dict(d, record_key = 'input', nest_depth = 1, sep = ':', 
                  cl_args_list = sys.argv):
    '''
    Records contents of dictionary d at record_key on nest_depth.
    Assumes unnested elements of d follow human-name: file-path.
    Values of d at record_key can be string or (nested) dict.
    '''
    if misc.is_scons_dry_run(cl_args_list = cl_args_list):
        return None 
    record_dict = misc.flatten_dict(d)
    record_dict = [(key, val) for key, val in sorted(record_dict.items())
                   if key.count(sep) >= nest_depth and val not in [None, 'None', '']]
    for name, path in record_dict:
        if record_key == name.split(sep)[nest_depth]:
            record_dir(path, name)
    return None

def record_dir(inpath, name,
               include_checksum = False,
               file_limit = 5000,
               outpath = 'state_of_input.log'):
    '''
    Record relative path, size, and (optionally) checksum of all files within inpath.
    Relative paths are from inpath.
    Append info in |-delimited format to outpath below a heading made from inpath.
    '''
    inpath, name, this_file_only, do_walk = check_inpath(inpath, name)
    if do_walk:
        files_info = walk(inpath, include_checksum, file_limit, this_file_only)
    else:
        files_info = None
    check_outpath(outpath)
    write_log(name, files_info, outpath)
    return None

def check_inpath(inpath, name):
    '''
    Check that inpath exists as file or directory.
    If file, make inpath the file's directory and only record info for that file.
    '''
    this_file_only = None
    do_walk = True
    if os.path.isfile(inpath):
        this_file_only = inpath
        inpath = os.path.dirname(inpath)
    elif os.path.isdir(inpath):
        pass
    else:
        name = name + ', could not find at runtime.'
        do_walk = False
    return inpath, name, this_file_only, do_walk

def check_outpath(outpath):
    '''
    Ensure that the directory for outpath exists.
    '''
    dirname = os.path.dirname(outpath)
    if dirname and not os.path.isdir(dirname):
        os.makedirs(dirname)
    return None

def walk(inpath, include_checksum, file_limit, this_file_only):
    '''
    Walk through inpath and grab paths to all subdirs and info on all files. 
    Walk in same order as os.walk.
    Keep walking until there are no more subdirs or there's info on file_limit files.
    '''
    dirs = [inpath]
    files_info, file_limit = prep_files_info(include_checksum, file_limit)
    while dirs and do_more_files(files_info, file_limit):
        dirs, files_info = scan_dir_wrapper(
            dirs, files_info, inpath, include_checksum, file_limit, this_file_only)
    return files_info

def prep_files_info(include_checksum, file_limit):
    '''
    Create a header for the file characteristics to grab.
    Adjusts file_limit for existence of header. 
    '''
    files_info = [['file path', 'file size in bytes']]
    if include_checksum:
        files_info[0].append('MurmurHash3')
    file_limit += 1
    return files_info, file_limit

def do_more_files(files_info, file_limit):
    '''
    True if files_info has fewer then file_limit elements.
    '''
    return bool(len(files_info) < file_limit)

def scan_dir_wrapper(dirs, files_info, inpath, include_checksum, file_limit, 
                     this_file_only):
    '''
    Drop down access and output management for scan_dir. 
    Keep running the while loop in walk as directories are removed and added. 
    '''
    dir_to_scan = dirs.pop(0)
    subdirs, files_info = scan_dir(
        dir_to_scan, files_info, inpath, include_checksum, file_limit, this_file_only)
    dirs += subdirs
    return dirs, files_info

def scan_dir(dir_to_scan, files_info, inpath, include_checksum, file_limit, 
             this_file_only):
    '''
    Collect names of all subdirs and all information on files.
    '''
    subdirs = []
    entries = scandir.scandir(dir_to_scan)
    for entry in entries:
        if entry.is_dir(follow_symlinks = False):
            if '.git' in entry.path or '.svn' in entry.path:
                continue
            else:
                subdirs.append(entry.path)
        elif entry.is_file() and (this_file_only is None or this_file_only == entry.path):
            f_info = get_file_information(entry, inpath, include_checksum)
            files_info.append(f_info)
            if not do_more_files(files_info, file_limit):
                break
    return subdirs, files_info
    
def get_file_information(f, inpath, include_checksum):
    '''
    Grabs path and size from scandir file object. 
    Will compute file's checksum if asked.
    '''
    f_path = os.path.relpath(f.path, inpath).strip()
    f_size = str(f.stat().st_size)
    f_info = [f_path, f_size]
    if include_checksum:
        with open(f.path, 'rU') as infile:
            f_checksum = str(mmh3.hash128(infile.read(), 2017))
        f_info.append(f_checksum)
    return f_info

def write_log(name, files_info, outpath):
    '''
    Write file information to outpath under a nice header.
    '''
    out_name = misc.make_heading(name)
    if files_info is not None:
        out_files_info = ['|'.join(l) for l in files_info]
        out_files_info = '\n'.join(out_files_info)
    else:
        out_files_info = ''
    with open(outpath, 'ab') as f:
        f.write(out_name)
        f.write(out_files_info)
        f.write('\n\n')
    return None


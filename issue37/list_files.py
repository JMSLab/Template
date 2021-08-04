from pathlib import Path
import subprocess
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('list_dirs',
                    nargs    = '*',
                    type     = str,
                    metavar  = 'LIST_DIRS',
                    default  = ['.'],
                    help     = "Directory to list")
parser.add_argument('--no-git',
                    dest     = 'no_git',
                    action   = 'store_true',
                    help     = "Do not use git to search for files",
                    required = False)
parser.add_argument('--patterns',
                    dest     = 'patterns',
                    type     = str,
                    nargs    = '*',
                    default  = ['*'],
                    help     = "Patterns to match",
                    required = False)
parser_args = vars(parser.parse_args())


def main():
    for size, file_path in list_files(**parser_args):
        print(f"{sizeof_fmt(size):>9} {file_path}")


def list_files(list_dirs=['.'], no_git=False, patterns=['*']):
    list_files = []
    for list_dir in list_dirs:
        for pattern in patterns:
            if no_git:
                list_files += [str(f) for f in Path(list_dir).glob(f"**/{pattern}") if f.is_file()]
            else:
                list_files += list_git_files(os.path.join(list_dir, pattern))

    return sorted(list_file_sizes(list_files), reverse=True)


def list_git_files(list_pattern):
    cmd_files  = f"git ls-files -- {list_pattern}"
    try:
        return subprocess.check_output(cmd_files, shell=True).splitlines()
    except subprocess.CalledProcessError:
        return []


def list_file_sizes(file_list):
    list_files = []
    for file_path in file_list:
        try:
            file_path = file_path.decode('utf-8')
        except:
            pass
        list_files += [(os.stat(file_path).st_size, file_path)]

    return list_files


def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


if __name__ == "__main__":
    main()

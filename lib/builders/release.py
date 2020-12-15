import re
import os
import sys
import _release_tools
from _exception_classes import ReleaseError
from misc import load_yaml_value, check_and_expand_path

def main(version = None,
         user_yaml = 'config_user.yaml', 
         release_files = [],
         dont_zip = False,
         readme = None, 
         scons_local_path = 'run.py'):

    # Check if user specified a scons_local_path
    if scons_local_path == 'run.py':
        check_none = lambda scons_local_path, regex: bool(re.match(regex, scons_local_path, re.IGNORECASE))
        try:
            scons_local_path = next(arg for arg in sys.argv if re.search('^scons_local_path=', arg))
            scons_local_path = re.sub('^scons_local_path=', '', scons_local_path)
            if check_none(scons_local_path, 'None') or check_none(scons_local_path, 'False'):
                scons_local_path = None
        except:
            pass

    # Check if repository is up-to-date and ready for release. Stop if not.
    # Order matters because SCons check changes logs.
    if not _release_tools.git_up_to_date():
        raise ReleaseError('Git working tree not clean.')
    elif not _release_tools.scons_up_to_date(scons_local_path):
        raise ReleaseError('SCons targets not up to date.')  

    # Extract information about the clone from its .git directory
    try: 
        repo, organisation, branch = _release_tools.extract_dot_git()
    except: 
        try: 
            repo, organisation, branch = _release_tools.extract_dot_git(path = '../.git')
        except: 
            raise ReleaseError("Could not find .git/config in the current directory or parent directory.")

    # Determine the version number
    if version is None:
        try:
            version = next(arg for arg in sys.argv if re.search("^version=", arg))
        except:
            raise ReleaseError('No version specified.')
        version = re.sub('^version=', '', version)

    # Determine whether the user has specified the no_zip option
    if dont_zip == False:
        dont_zip = 'no_zip' in sys.argv
    zip_release = not dont_zip

    # Read a list of files to release to release_dir
    if release_files == []:
        for root, _, files in os.walk('./release'):
            for file_name in files:
                # Do not release .DS_Store
                if not re.search("\.DS_Store", file_name):
                    release_files.append(os.path.join(root, file_name))

    # Specify the local release directory
    release_dir = load_yaml_value(user_yaml, 'release_directory')
    release_dir = check_and_expand_path(release_dir)

    if branch == 'master':
        name   = repo
        branch = ''
    else:
        name = "%s-%s" % (repo, branch)
    local_release = '%s/%s/' % (release_dir, name)
    local_release = local_release + version + '/'

    # Get GitHub token:
    github_token = load_yaml_value(user_yaml, 'github_token')
    
    _release_tools.release(vers              = version, 
                           DriveReleaseFiles = release_files,
                           local_release     = local_release, 
                           org               = organisation, 
                           repo              = repo,
                           target_commitish  = branch,
                           zip_release       = zip_release,
                           github_token      = github_token)

if __name__ == '__main__':
    main()

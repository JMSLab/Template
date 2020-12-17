
Copied from [`gslab_scons`](https://github.com/gslab-econ/gslab_python/tree/master/gslab_scons)

## Notes on release.py

Make a release from a SCons directory by running the module `release`. 

### Basic use

A user can either run the following from the command line within the directory of interest (e.g. `/paper_slides`) or write a Python script to call the module (see "Python wrapper" section below). If using the command line, run the following:

```sh
python -m gslab_scons.release version=<version name here> readme=<readme path here>
```
    
where `<version name here>` is the name of the version that will be released, and `<readme path>` is the path from the current directory to the repository readme file (default to `./README.md`). As an example, to release version v1.2.1 of a directory with the README file one level up, navigate to the root of the directory and run:

```sh
python -m gslab_scons.release version=v1.2.1 readme=../README.md
```

An automatic location for release must be specified in `config_user.yaml` with 

```yaml
release_directory: <release location here>
```

For example, to automatically release to Dropbox set

```
release_directory: /Users/you/Dropbox/release
``` 

### Check stability

Before releasing, the module checks that your repository is up-to-date by executing (in order) a
* `git status`
* SCons dry run

By default, we run SCons from `run.py`, but you can specify another script through `scons_local_path=<relative path to script here>`. Set this argument to `None` or `False` if you want to run `scons` using your global installation. Executing a dry run may update log files packed into the SConstruct, which could affect the `git status` in repeated runs.

### Other options

Including the option `no_zip` will prevent files from being zipped before they are released to the specified location.  

This release procedure will warn you when a versioned file is larger than 2MB and when the directory's versioned content is larger than 500MB in total.  

Instead of entering the GitHub token as a password when using `release`, you can store it in `config_user.yaml` as

```yaml
github_token: <your token here>
```

### Python wrapper

If you wish to wrap the `release` module in a Python script to help pass arguments, use the syntax

```python
from gslab_scons import release
release.main(version = '<version name here>',
             readme  = '../readme.md')
```

For a complete list of arguments that you can pass to `release.main()`, visit `release.py`.

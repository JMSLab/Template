## JMSLab Template

A template for research projects developed in JMSLab.

### Prerequisites

You will need, at a minimum, the following freely available tools:

- [SCons](https://scons.org) to execute scripts and track dependencies.
- [Python](https://www.python.org/downloads) 3.8.X or above to run SCons.
    - You will also need to install the additional dependencies in `./source/lib/requirements.txt`
    - Custom builders for SCons are also written in Python.
- [git](https://git-scm.com/downloads) for version control.
    - And [git-lfs](https://git-lfs.github.com/) for versioning large files.
- [LyX](https://www.lyx.org/Download) for writing documents.

In addition, each project may use other specialized tools (e.g. R, Stata, Matlab, LaTeX).

### Quick start

1. Open the command-line and clone the repository. For example,

    ```
    git clone https://github.com/JMSLab/Template ProjectName
    cd ProjectName
    ```

2. Create a folder called `temp` for temporary files.

3. Create a symbolic link called `drive` to _a local copy_ the project's Dropbox drive (datastore), if one exists for the project.

    - Do _not_ link a "live" copy (i.e. one that is synchronized to the internet) of the datastore. Otherwise, each time the repository is compiled, even if you are just testing something, the data will be replaced for everyone using the datastore.

    - You should work with a local, off-line copy of the datastore before modifying the live copy.

4. Install Python dependencies:

    ```
    pip install -r source/lib/requirements.txt
    ```

5. Install any additional tools required for the project (e.g. R, Stata, Matlab, LaTeX).

6. Make sure that all the required program executables are in your system's path. 

    - The default names that SCons assumes for the programs are in `source/lib/builders/executables.txt`.

    - To have SCons use a custom executable name or path, define a command-line variable named `JMSLAB_EXE_PROGRAM=/path/to/executable`. e.g. `JMSLAB_EXE_STATA=StataSE.exe` or `JMSLAB_EXE_STATA="C:\Program Files (x86)\Stata16\StataSE.exe"`.

7. To compile the project, open the command-line and run `scons` from the project's root folder.

### Repository Structure

- `source/` contains source scripts and (small) raw data. All of our data cleaning and analysis, and much of our data gathering, takes place here. 

    - Do not create any new top-level folders inside of source;  new tasks should be sorted into one of the existing sub-folders.

    - Each folder in source has an analogous output folder in `output/` and/or `drive/`. For instance, the code in `source/analysis/plots/` saves output to `output/analysis/plots/`.

- `output/` and `drive/` should mimic the folder structure in source.

    - With the exception of large raw files, every file here is produced by `source/`, and folders correspond to an analogous source folder in `source/`.

    - `drive/` is not under version control and a project's large files, including raw files, are in `drive/`. Hence large raw files (and any accompanying documentation) would not have a corresponding entry in `source/`.

- `temp/` is often used by scripts to store temporary data files.

- Issue folders: When working on issues, you may create an issue folder at the top of the directory (e.g. `./issue1_task_name`). Code and deliverables related to the issue are organized inside the issue folder, but anything that is meant to be integrated into the project should be sorted into a sub-folder in `./source`.

### SConscript files

In order to integrate a new script into the SCons build, you need to modify the SConscript file in the corresponding `source/` sub-folder.  For example, to add `source/derived/wb_clean/takelogs.do` to the SCons build, we need an entry to `source/derived/SConscript`. In this case:

```
target = ['#output/derived/wb_clean/gdp_education_logs.csv']
source = ['#source/derived/wb_clean/takelogs.do',
          '#output/derived/wb_clean/gdp_education.csv']
env.Stata(target, source)
```

- `target` is a list with all of the files produced by the script.

- `source` is a list with the script's name and all of the files used as input (the script must be the first element of the list).

- `env.Stata` is the Stata builder provided by this template; this is imported and saved in `env` in the `SConstruct` file at the root of the project. 

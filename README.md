## JMSLab Template

A template for research projects developed by JMSLab.

### Prerequisites

- [Python](https://www.python.org/downloads) 3.8.X or above to run [SCons](https://scons.org).
    - You will need to install the dependencies in `source/lib/requirements.txt`, including SCons and other required packages (see [quick start](#quick-start) below).
    - Custom builders for SCons are also written in Python.
- [git](https://git-scm.com/downloads) for version control.
    - And [git-lfs](https://git-lfs.github.com/) for versioning large files.
- [LyX](https://www.lyx.org/Download) for writing documents.

In addition, each project may use other specialized tools. For the working example in this template, install:

- [R](https://www.r-project.org/)
- [Stata](https://www.stata.com/install-guide/)
- [Matlab](https://www.mathworks.com/help/install/install-products.html)

### Quick start

1. Open the command-line and clone the repository. For example,

    ```
    git clone https://github.com/JMSLab/Template ProjectName
    cd ProjectName
    ```

2. Create a symbolic link called `drive` to _a local copy_ the project's datastore, if one exists for the project (e.g. a Dropbox or Google Drive folder).

    - Do _not_ link a "live" copy of the datastore (i.e. one that is synchronized to the internet). Work with a local, off-line copy before modifying the live copy;  otherwise the data may get unintentionally overwritten for everyone using the datastore. 

3. Install Python dependencies:

    ```
    pip install -r source/lib/requirements.txt
    ```

4. Make sure that all the required program executables are in your system's path. 

    - The default names that SCons assumes for the programs are in `source/lib/builders/executables.txt`.

    - To have SCons use a custom executable name or path, define a command-line variable named `JMSLAB_EXE_PROGRAM=/path/to/executable`. e.g. `JMSLAB_EXE_STATA=StataSE.exe` or `JMSLAB_EXE_STATA="C:\Program Files (x86)\Stata16\StataSE.exe"`.

5. To compile the project, open the command-line and run `scons` from the project's root folder.

    - To run a given script or create a given file, run `scons path/to/script_or_file`; this will recursively run all the dependencies required to run the script or create the file.

### Repository Structure

- `source/` contains source scripts and (small) raw data. All of the data cleaning and analysis, and much of the data gathering, takes place here. 

    - Do not create any new top-level folders inside of source;  new tasks should be sorted into one of the existing sub-folders.

    - Each folder in source has an analogous output folder in `output/` and/or `drive/`. For instance, the code in `source/analysis/plots/` saves output to `output/analysis/plots/`.

- `output/` and `drive/` should mimic the folder structure in `source/`.

    - `drive/` is not under version control; a project's large files are stored here.

    - With the exception of large raw files, every file in these folders is produced by `source/`, and their folders correspond to an analogous source folder in `source/`.

- `temp/` may be used by scripts to store temporary or intermediate files.

- _Issue folders_: When working on issues, you may create a temporary issue folder at the top of the directory (e.g. `./issue1_task_name`).

    - Code and deliverables related to the issue are organized inside the issue folder.

    - However, anything that is meant to be integrated into the project should be sorted into a sub-folder in `source/`.

    - Further, the issue folder must be deleted before merging the issue branch.

### SConscript files

In order to integrate a new script into the SCons build, you need to modify the SConscript file in the corresponding `source/` sub-folder.  For example, to add `source/derived/wb_clean/takelogs.do` to the SCons build, add an entry to `source/derived/SConscript`. In this case:

```
target = ['#output/derived/wb_clean/gdp_education_logs.csv']
source = ['#source/derived/wb_clean/takelogs.do',
          '#output/derived/wb_clean/gdp_education.csv']
env.Stata(target, source)
```

- `target` is a list with all of the files produced by the script.

- `source` is a list with the script's name and all of the files used as input; the script must be the first element of the list.

- `env.Stata` is the Stata builder provided in `source/lib/builders`; this is imported and saved as part of the `env` object in the `SConstruct` file at the root of the project. 

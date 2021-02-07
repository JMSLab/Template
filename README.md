## JMSLab Template

A template for research projects developed by JMSLab.

### Prerequisites

- We recommend installing [Anaconda](https://www.anaconda.com/products/individual) 3.8 or above to get Python.
    - We use Python to run [SCons](https://scons.org); custom SCons builders are also written in Python.
    - You will need to install the dependencies in `source/lib/requirements.txt` (including SCons). See [quick start](#quick-start) below.
- [git](https://git-scm.com/downloads) for version control.
    - And [git-lfs](https://git-lfs.github.com/) for versioning large files.
- [LyX](https://www.lyx.org/Download) for writing documents.

In addition, each project may use other specialized tools. For the working example in this template, install:

- [R](https://www.r-project.org/)
- [Stata](https://www.stata.com/install-guide/)
- [Matlab](https://www.mathworks.com/help/install/install-products.html)

### Repository Structure

- `source/` contains source scripts and (small) raw data.

- `output/` and `drive/` should mimic the folder structure in `source/`.

    - For instance, the code in `source/analysis/plots/` saves output to `output/analysis/plots/`.

    - `drive/` is not under version control; a project's large files are stored here.

    - With the exception of large raw files, every file in these folders is produced by `source/`.

- `temp/` is not under version control; create the folder after cloning the repository.  `temp/` may used by scripts to store temporary or intermediate files.

- _Issue folders_: When working on issue branches, you may create an issue folder at the top of the directory under version control (e.g. `./issue1_short_task_name`).

    - Code and (small) deliverables related to the issue are organized inside the issue folder. See [this example](https://github.com/JMSLab/Template/blob/4b8219865376fd0e153ce6ba91e9eed882de01b5/issue10_readme).

    - The issue folder should be deleted after the issue is resolved and is not merged into the main branch.

### Quick start

1. Open the command-line and clone the repository. For example,

    ```
    git clone https://github.com/JMSLab/Template ProjectName
    cd ProjectName
    ```

2. Create a symbolic link called `drive` to _a local copy_ the project's datastore, if one exists for the project (e.g. a Dropbox or Google Drive folder).

    - Do _not_ link a "live" copy of the datastore (i.e. one that is synchronized to the internet). Work with a local, off-line copy before modifying the live copy;  otherwise the data may get unintentionally overwritten for everyone using the datastore.

3. Install dependencies:

    ```
    pip install -r source/lib/requirements.txt
    ```

    (If using `conda`, run `conda install --file source/lib/requirements.txt`.)  Requirements for other languages, should there be any, will be found in `source/lib/requirements.{ext}` with `{ext}` equal to `do` (Stata), `r` (R), `m` (Matlab), and so on.

4. Make sure that all the required program executables are in your system's path.

    - The default names that SCons assumes for the programs are in `source/lib/JMSLab/builders/executables.yml`.

    - To have SCons use a custom executable name or path, define a command-line (environment) variable named `JMSLAB_EXE_PROGRAM`. e.g. On Windows, `SET JMSLAB_EXE_STATA=StataSE.exe` or `SET JMSLAB_EXE_STATA=C:\Program Files (x86)\Stata16\StataSE.exe`.

5. To compile the project, open the command-line and run `scons` from the project's root folder.

    - To run a given script or create a given file, run `scons path/to/script_or_file`; this will recursively run all the dependencies required to run the script or create the file.  e.g.  `scons output/derived/wb_clean/gdp_education.csv`.

### SConscript files

In order to integrate a new script into the SCons build, you need to modify the SConscript file in the corresponding `source/` sub-folder.  For example, to add `source/derived/wb_clean/takelogs.do` to the SCons build, add an entry to `source/derived/SConscript`. In this case:

```python
target = ['#output/derived/wb_clean/gdp_education_logs.csv']
source = ['#source/derived/wb_clean/takelogs.do',
          '#output/derived/wb_clean/gdp_education.csv']
env.Stata(target, source)
```

- `target` is a list with all of the files produced by the script.

- `source` is a list with the script's name and all of the files used as input; the script _must_ be the first element of the list.

- `env.Stata` is the Stata builder provided in `source/lib/JMSLab/builders`; this is imported and saved as part of the `env` object in the `SConstruct` file at the root of the project.

'''

This directory contains the JMSLab SCons' library's unit tests. These
are modified versions of the unit tests in gslab_scons.  Tests should
be run from JMSLab's parent directory (should be ../..) via:

    python -m unittest discover

You may need to modify the Stata executable; for example (note lack
of quotes on Windows):

    - On Windows (CMD): SET JMSLAB_EXE_STATA=/path to/stata.exe
    - On *nix (bash):   export JMSLAB_EXE_STATA="/path to/stata"

Individual tests can be run via

    python -m unittest JMSLab.tests.test_build_latex
    python -m unittest JMSLab.tests.test_build_lyx
    python -m unittest JMSLab.tests.test_build_matlab
    python -m unittest JMSLab.tests.test_build_r
    python -m unittest JMSLab.tests.test_build_python
    python -m unittest JMSLab.tests.test_build_stata
    python -m unittest JMSLab.tests.test_build_tables
    python -m unittest JMSLab.tests.test_log
    python -m unittest JMSLab.tests.test_misc
'''

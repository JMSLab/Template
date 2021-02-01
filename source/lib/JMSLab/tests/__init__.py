'''

This directory contains the JMSLab SCons' library's unit tests. These
are modified versions of the unit tests in gslab_scons. First install
pytest and mock (e.g. `pip install pytest mock`), then run:

    pytest

To run a single script, run `pytest path/to/script.py`, e.g.

    pytest test_build_python.py

You may need to modify the Stata executable; for example (note lack
of quotes on Windows):

    - On Windows (CMD): SET JMSLAB_EXE_STATA=/path to/stata.exe
    - On *nix (bash):   export JMSLAB_EXE_STATA="/path to/stata"
'''

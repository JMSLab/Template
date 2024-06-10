'''
SCons builder library for JMSLab
================================

This is a Python library containing general-purpose SCons builders for  
various software packages. Its builders work on both Unix and Windows   
platforms.                                                              

This package was based on gslab_scons and updated to Python 3. Please
consult the docstrings of the builders belonging to this module for
additional information on their functionalities.
'''
import os
from . import misc
from .log import start_log, end_log

from .builders.build_r         import build_r
from .builders.build_latex     import build_latex
from .builders.build_lyx       import build_lyx
from .builders.build_stata     import build_stata
from .builders.build_tables    import build_tables
from .builders.build_python    import build_python
from .builders.build_matlab    import build_matlab

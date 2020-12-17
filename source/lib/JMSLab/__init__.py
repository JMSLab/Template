'''
gslab_scons - a SCons builder library
=====================================

gslab_scons is a Python library containing general-purpose SCons builders 
for various software packages. Its builders work on both Unix and Windows 
platforms. 

Please consult the docstrings of the gslab_scons builders belonging to
this module for additonal information on their functionalities.
'''
import os
import misc
from .log                      import start_log, end_log
from .log_paths_dict           import log_paths_dict, record_dir
from .scons_debrief            import scons_debrief
from .check_prereq             import check_prereq
from .builders.build_r         import build_r
from .builders.build_latex     import build_latex
from .builders.build_lyx       import build_lyx
from .builders.build_stata     import build_stata
from .builders.build_tables    import build_tables
from .builders.build_python    import build_python
from .builders.build_matlab    import build_matlab
from .builders.build_anything  import build_anything

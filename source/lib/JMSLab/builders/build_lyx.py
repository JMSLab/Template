import os
import shutil

from gslab_builder import GSLabBuilder


def build_lyx(target, source, env):
    '''Compile a pdf from a LyX file

    This function is a SCons builder that compiles a .lyx file
    as a pdf and places it at the path specified by target.

    Parameters
    ----------
    target: string or list 
        The target of the SCons command. This should be the path
        of the pdf that the builder is instructed to compile. 
    source: string or list
        The source of the SCons command. This should
        be the .lyx file that the function will compile as a PDF.
    env: SCons construction environment, see SCons user guide 7.2
    '''
    builder_attributes = {
        'name': 'LyX',
        'valid_extensions': ['.lyx'],
        'exec_opts':  '-e pdf2'
    }
    builder = LyxBuilder(target, source, env, **builder_attributes)
    builder.execute_system_call()
    return None

class LyxBuilder(GSLabBuilder):
    '''
    '''
    def add_call_args(self):
        '''
        '''
        args = '%s %s > %s' % (self.cl_arg, os.path.normpath(self.source_file), os.path.normpath(self.log_file))
        self.call_args = args
        return None


    def do_call(self):
        '''
        '''
        super(LyxBuilder, self).do_call()
        new_pdf = os.path.splitext(self.source_file)[0] + '.pdf'
        new_pdf_path = os.path.normpath('%s/%s' % (self.target_dir, os.path.basename(new_pdf)))
        shutil.move(new_pdf, new_pdf_path)
        return None
        
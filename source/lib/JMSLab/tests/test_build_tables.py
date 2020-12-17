#! /usr/bin/env python
import unittest
import sys
import os
import shutil
import re
import mock

# Ensure that Python can find and load the GSLab libraries
os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path.append('../..')

import gslab_scons.builders.build_tables as gs
from gslab_scons._exception_classes import BadExtensionError, ExecCallError
from gslab_make.tests import nostderrout


class TestBuildTables(unittest.TestCase):

    def setUp(self):
        if not os.path.exists('./build/'):
            os.mkdir('./build/')

    def table_fill_side_effect(self, input, template, output):
        return ""

    def table_fill_side_effect_error(self, input, template, output):
        return "traceback"

    @mock.patch('gslab_scons.builders.build_tables.tablefill')
    def test_standard(self, mock_tablefill):
        '''
        Test that build_tables() correctly prepares and passes
        inputs to the gslab_fill.tablefill() function
        '''

        mock_tablefill.side_effect = self.table_fill_side_effect
        # Specify the sources and the target arguments of build_tables()
        source = ['./input/tablefill_template.lyx', 
                  './input/tables_appendix.txt',
                  './input/tables_appendix.txt']
        target = ['./build/tablefill_template_filled.lyx']
        
        # Call build_tables() and check that it behaved as expected.
        gs.build_tables(target, source, {})
        self.check_call(source, target, mock_tablefill)

        # The target can also be a tuple
        target = ('./build/tablefill_template_filled.lyx')
        gs.build_tables(target, source, {})
        self.check_call(source, target, mock_tablefill)

        # The target can also be a tex file
        target = ('./build/tablefill_template_filled.tex')
        gs.build_tables(target, source, {})
        self.check_call(source, target, mock_tablefill)

    def check_call(self, source, target, mock_tablefill):
        '''
        This method checks that the build_tables() behaves as expected
        using its source argument, its target argument, and a mock 
        for gslab_fill.table_fill()
        '''
        mock_tablefill.assert_called_once()

        # Check that build_tables() passed arguments to tablefill() correctly.
        kwargs = mock_tablefill.call_args[1]

        # i) input should be the sources (except the first) joined by spaces
        inputs = kwargs['input'].split()
        for path in source[1:len(source)]:
            self.assertIn(str(path), inputs)
        self.assertEqual(len(source) - 1, len(inputs))

        # ii) The template argument should be the first source
        self.assertEqual(str(source[0]), kwargs['template'])

        # iii) The output argument should be build_tables()'s target argument.
        if isinstance(target, str):
            target = [target]
        self.assertEqual(target[0], kwargs['output'])

        mock_tablefill.reset_mock()

    @mock.patch('gslab_scons.builders.build_tables.tablefill')
    def test_default_string_target(self, mock_tablefill):
        '''
        Test that build_tables() constructs LyX tables correctly when
        its target argument is a string.
        '''
        mock_tablefill.side_effect = self.table_fill_side_effect
        source = ['./input/tablefill_template.lyx', 
                  './input/tables_appendix.txt', 
                  './input/tables_appendix_two.txt']
        target = './build/tablefill_template_filled.lyx'
        gs.build_tables(target, source, {})

        self.check_call(source, target, mock_tablefill)      

    @mock.patch('gslab_scons.builders.build_tables.tablefill')
    def test_error_traceback(self, mock_tablefill):
        '''
        Test that build_tables() properly outputs traceback.
        '''
        mock_tablefill.side_effect = self.table_fill_side_effect_error
        source = ['./input/tablefill_template.lyx', 
                  './input/tables_appendix.txt', 
                  './input/tables_appendix_two.txt']
        target = './build/tablefill_template_filled.lyx'
        with self.assertRaises(ExecCallError), nostderrout():
            gs.build_tables(target, source, {})


    def test_target_extension(self):
        '''Test that build_tables() recognises an inappropriate file extension'''

        # Specify the sources and the target.
        source = ['./input/tablefill_template.lyx', 
                  './input/tables_appendix.txt', 
                  './input/tables_appendix_two.txt']
        target =  './build/tablefill_template_filled.BAD'
        
        # Calling build_tables() with a target argument whose file extension
        # is unexpected should raise a BadExtensionError.
        with self.assertRaises(BadExtensionError), nostderrout():
            gs.build_tables(target, source, '')    
       
    @mock.patch('gslab_scons.builders.build_tables.tablefill')
    def test_unintended_inputs(self, mock_tablefill):
        '''
        Test build_tables()'s behaviour when provided with 
        inputs other than those we intend it to be given. 
        '''
        std_source = ['./input/tablefill_template.lyx', 
                      './input/tables_appendix.txt']
        std_target = './build/tablefill_template_filled.lyx'

        mock_tablefill.side_effect = self.table_fill_side_effect

        #== env =============
        for env in ['', None, Exception, "the environment", (1, 2, 3)]:
            with self.assertRaises(TypeError):
                gs.build_tables(std_target, std_source, env = env)
                self.check_call(std_source, std_target, mock_tablefill)    

        #== target ==========
        # Target argument is not a string or container of strings
        with self.assertRaises(TypeError):
            gs.build_tables(1, std_source, None)
        with self.assertRaises(TypeError):
            gs.build_tables(None, std_source, None)    
        #  Target is a container of non-strings
        with self.assertRaises(TypeError):
            gs.build_tables((True, False, False), std_source, None)

        #== source ==========
        # The source isn't a .lyx path
        source = ['nonexistent_file']
        with self.assertRaises(BadExtensionError):
            gs.build_tables(std_target, source, {})

        # The source is a container of nonstrings.
        source = (True, False, False)
        with self.assertRaises(TypeError):
            gs.build_tables(std_target, source, {})

        # source is a non-strings non-iterable with no len() value
        source = 1
        with self.assertRaises(TypeError):
            gs.build_tables(std_target, source, {})

    def tearDown(self):
        if os.path.exists('./build/'):
            shutil.rmtree('./build/')


if __name__ == '__main__':
    unittest.main()

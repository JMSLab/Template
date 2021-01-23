#! /usr/bin/env python

from unittest import mock
from pathlib import Path

import unittest
import shutil
import re
import os

# Import testing helper modules
from ..builders.build_tables import build_tables, tablefill
from .._exception_classes import BadExtensionError, ExecCallError

# Define path to the builder for use in patching
path = 'JMSLab.builders.build_tables'
tablefill_patch = mock.patch('%s.tablefill' % path)

# Run tests from test folder
TESTDIR = Path(__file__).resolve().parent
os.chdir(TESTDIR)


class TestBuildTables(unittest.TestCase):

    def setUp(self):
        (TESTDIR / 'build').mkdir(exist_ok = True)

    def table_fill_side_effect(self, input, template, output):
        self.mock_output = tablefill(input = input, template = template, output = output)
        return self.mock_output

    def table_fill_side_effect_error(self, input, template, output):
        self.mock_output = "traceback"
        return self.mock_output

    @tablefill_patch
    def test_standard(self, mock_tablefill):
        '''
        Test that build_tables() correctly prepares and passes
        inputs to the tablefill() function
        '''

        mock_tablefill.side_effect = self.table_fill_side_effect
        # Specify the sources and the target arguments of build_tables()
        source = ['input/tablefill_template.lyx',
                  'input/tables_appendix.txt',
                  'input/tables_appendix.txt']
        target = ['build/tablefill_template_filled.lyx']

        # Call build_tables() and check that it behaved as expected.
        build_tables(target, source, {})
        self.check_call(source, target, mock_tablefill)

        # The target can also be a tuple
        target = ('build/tablefill_template_filled.lyx')
        build_tables(target, source, {})
        self.check_call(source, target, mock_tablefill)

        # The target can also be a tex file
        target = ('build/tablefill_template_filled.tex')
        build_tables(target, source, {})
        self.check_call(source, target, mock_tablefill)

    @tablefill_patch
    def test_default_string_target(self, mock_tablefill):
        '''
        Test that build_tables() constructs LyX tables correctly when
        its target argument is a string.
        '''
        mock_tablefill.side_effect = self.table_fill_side_effect
        source = ['input/tablefill_template.lyx',
                  'input/tables_appendix.txt',
                  'input/tables_appendix_two.txt']
        target = 'build/tablefill_template_filled.lyx'
        build_tables(target, source, {})

        self.check_call(source, target, mock_tablefill)

    @tablefill_patch
    def test_error_traceback(self, mock_tablefill):
        '''
        Test that build_tables() properly outputs traceback.
        '''
        mock_tablefill.side_effect = self.table_fill_side_effect_error
        source = ['input/tablefill_template.lyx',
                  'input/tables_appendix.txt',
                  'input/tables_appendix_two.txt']
        target = 'build/tablefill_template_filled.lyx'
        with self.assertRaises(ExecCallError):
            build_tables(target, source, {})

    def test_target_extension(self):
        '''Test that build_tables() recognises an inappropriate file extension'''

        # Specify the sources and the target.
        source = ['input/tablefill_template.BAD',
                  'input/tables_appendix.txt',
                  'input/tables_appendix_two.txt']
        target = 'build/tablefill_template_filled.lyx'

        # Calling build_tables() with a target argument whose file extension
        # is unexpected should raise a BadExtensionError.
        with self.assertRaises(BadExtensionError):
            build_tables(target, source, {})

    @tablefill_patch
    def test_unintended_inputs(self, mock_tablefill):
        '''
        Test build_tables()'s behaviour when provided with
        inputs other than those we intend it to be given.
        '''
        std_source = ['input/tablefill_template.lyx',
                      'input/tables_appendix.txt']
        std_target = 'build/tablefill_template_filled.lyx'

        mock_tablefill.side_effect = self.table_fill_side_effect

        # == env =============
        for env in ['', None, Exception, "the environment", (1, 2, 3)]:
            with self.assertRaises(TypeError):
                build_tables(std_target, std_source, env = env)
                self.check_call(std_source, std_target, mock_tablefill)

        # == target ==========
        # Target argument is not a string or container of strings
        with self.assertRaises(TypeError):
            build_tables(1, std_source, None)
        with self.assertRaises(TypeError):
            build_tables(None, std_source, None)
        #  Target is a container of non-strings
        with self.assertRaises(TypeError):
            build_tables((True, False, False), std_source, None)

        # == source ==========
        # The source isn't a .lyx path
        source = ['nonexistent_file']
        with self.assertRaises(BadExtensionError):
            build_tables(std_target, source, {})

        # The source is a container of nonstrings.
        source = (True, False, False)
        with self.assertRaises(TypeError):
            build_tables(std_target, source, {})

        # source is a non-strings non-iterable with no len() value
        source = 1
        with self.assertRaises(TypeError):
            build_tables(std_target, source, {})

    @tablefill_patch
    def test_input(self, mock_tablefill):
        '''
        Test that build_tables() correctly runs given actual input (no
        mock runs; this is meant to give a successful run with existing
        pre-formatted files).

        This also checks that the data was correctly filled.
        '''

        mock_tablefill.side_effect = self.table_fill_side_effect
        for ext in ['lyx', 'tex']:
            source = [f'input/tablefill_template.{ext}',
                      'input/tables_appendix.txt',
                      'input/tables_appendix_two.txt']
            target = f'build/tablefill_template_filled.{ext}'
            build_tables(target, source, {})
            message = self.mock_output

            self.assertIn('filled successfully', message)

            with open(Path('input', f'tablefill_template.{ext}'), 'r') as td:
                tag_data = td.readlines()

            with open(Path('build', f'tablefill_template_filled.{ext}'), 'r') as fd:
                filled_data = fd.readlines()

            self.assertEqual(len(tag_data), len(filled_data))
            for n in range(len(tag_data)):
                if ext == 'tex':
                    self.tag_compare_latex(tag_data[n], filled_data[n])
                elif ext == 'lyx':
                    self.tag_compare_lyx(tag_data[n], filled_data[n])

    @tablefill_patch
    def test_breaks_rounding_string(self, mock_tablefill):
        '''
        Test that giving a bad tag gives an error, as expected.
        '''

        mock_tablefill.side_effect = self.table_fill_side_effect
        for ext in ['lyx', 'tex']:
            with self.assertRaises(ExecCallError):
                source = [f'input/tablefill_template_breaks.{ext}',
                          'input/tables_appendix.txt',
                          'input/tables_appendix_two.txt']
                target = f'build/tablefill_template_filled.{ext}'
                build_tables(target, source, {})
                error = self.mock_output
                self.assertIn('InvalidOperation', error)

    @tablefill_patch
    def test_illegal_syntax(self, mock_tablefill):
        '''
        Test that giving bad input gives an error.
        '''

        mock_tablefill.side_effect = self.table_fill_side_effect

        for ext in ['lyx', 'tex']:
            with self.assertRaises(ExecCallError):

                # non-existent input 1
                source = [f'input/tablefill_template_breaks.{ext}',
                          'input/fake_file.txt',
                          'input/tables_appendix_two.txt']
                target = f'build/tablefill_template_filled.{ext}'
                build_tables(target, source, {})
                error = self.mock_output
                self.assertIn('IOError', error)

                # non-existent input 2
                source = [f'input/tablefill_template_breaks.{ext}',
                          'input/tables_appendix_two.txt',
                          'input/fake_file.txt']
                target = f'build/tablefill_template_filled.{ext}'
                build_tables(target, source, {})
                error = self.mock_output
                self.assertIn('IOError', error)

    @tablefill_patch
    def test_argument_order(self, mock_tablefill):
        '''
        Test that the  order of the input tables does not matter.
        '''

        mock_tablefill.side_effect = self.table_fill_side_effect
        for ext in ['lyx', 'tex']:
            source = [f'input/tablefill_template.{ext}',
                      'input/tables_appendix.txt',
                      'input/tables_appendix_two.txt']
            target = f'build/tablefill_template_filled.{ext}'
            build_tables(target, source, {})
            message = self.mock_output
            self.assertIn('filled successfully', message)

            with open(Path('build', f'tablefill_template_filled.{ext}'), 'r') as filled_file:
                filled_data_args1 = filled_file.readlines()

            source = [f'input/tablefill_template.{ext}',
                      'input/tables_appendix_two.txt',
                      'input/tables_appendix.txt']
            target = f'build/tablefill_template_filled.{ext}'
            build_tables(target, source, {})
            message = self.mock_output
            self.assertIn('filled successfully', message)

            with open(Path('build', f'tablefill_template_filled.{ext}'), 'r') as filled_file:
                filled_data_args2 = filled_file.readlines()

            self.assertEqual(filled_data_args1, filled_data_args2)

    def check_call(self, source, target, mock_tablefill):
        '''
        This method checks that the build_tables() behaves as expected
        using its source argument, its target argument, and a mock
        for table_fill()
        '''
        mock_tablefill.assert_called_once()

        # Check that build_tables() passed arguments to tablefill() correctly.
        kwargs = mock_tablefill.call_args[1]

        # i) input should be the sources (except the first) joined by spaces
        inputs = list(map(Path, kwargs['input'].split()))
        for path in source[1:len(source)]:
            self.assertIn(Path(str(path)), inputs)
        self.assertEqual(len(source) - 1, len(inputs))

        # ii) The template argument should be the first source
        self.assertEqual(Path(str(source[0])), Path(kwargs['template']))

        # iii) The output argument should be build_tables()'s target argument.
        if isinstance(target, str):
            target = [target]

        self.assertEqual(Path(target[0]), Path(kwargs['output']))

        mock_tablefill.reset_mock()

    def tag_compare_latex(self, tag_line, filled_line):
        '''
        Compare a tag line in latex with the fileld line.
        '''
        tag_line    = tag_line.split('&')
        filled_line = filled_line.split('&')
        for col in range(len(tag_line)):
            if re.match(r'^.*#\d+#', tag_line[col]) or re.match(r'^.*#\d+,#', tag_line[col]):
                entry_tag = re.split('#', tag_line[col])[1]
                decimal_places = int(entry_tag.replace(',', ''))
                if decimal_places > 0:
                    self.assertTrue(re.search(r'\.', filled_line[col]))
                    decimal_part = re.split(r'\.', filled_line[col])[1]
                    non_decimal = re.compile(r'[^\d.]+')
                    decimal_part = non_decimal.sub('', decimal_part)
                    self.assertEqual(len(decimal_part), decimal_places)
                else:
                    self.assertFalse(re.search(r'\.', filled_line[col]))
                if re.match(r'^.*#\d+,#', tag_line[col]):
                    integer_part = re.split(r'\.', filled_line[col])[0]
                    if len(integer_part) > 3:
                        self.assertEqual(integer_part[-4], ',')

    def tag_compare_lyx(self, tag_line, filled_line):
        '''
        Compare a tag line in LyX with the fileld line.
        '''
        if re.match(r'^.*#\d+#', tag_line) or re.match(r'^.*#\d+,#', tag_line):
            entry_tag = re.split('#', tag_line)[1]
            decimal_places = int(entry_tag.replace(',', ''))
            if decimal_places > 0:
                self.assertTrue(re.search(r'\.', filled_line))
                decimal_part = re.split(r'\.', filled_line)[1]
                non_decimal = re.compile(r'[^\d.]+')
                decimal_part = non_decimal.sub('', decimal_part)
                self.assertEqual(len(decimal_part), decimal_places)
            else:
                self.assertFalse(re.search(r'\.', filled_line))
            if re.match(r'^.*#\d+,#', tag_line):
                integer_part = re.split(r'\.', filled_line)[0]
                if len(integer_part) > 3:
                    self.assertEqual(integer_part[-4], ',')

    def tearDown(self):
        shutil.rmtree(TESTDIR / 'build')


if __name__ == '__main__':
    unittest.main()

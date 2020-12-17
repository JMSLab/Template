import unittest
import sys
import os
import re
import mock
import tempfile
import shutil
# Import module containing gslab_scons testing side effects
import _side_effects as fx

# Ensure that Python can find and load the GSLab libraries
os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path.append('../..')

import gslab_scons
import gslab_scons._release_tools as tools
from gslab_scons._exception_classes import ReleaseError
from gslab_make.tests import nostderrout


class TestReleaseTools(unittest.TestCase):

    @mock.patch('gslab_scons._release_tools.requests.session')
    @mock.patch('gslab_scons._release_tools.open')
    @mock.patch('gslab_scons._release_tools.os.path.isfile')
    def test_upload_asset_standard(self, mock_isfile, mock_open, mock_session):
        '''
        Test that upload_asset() correctly prepares a request
        to upload a release asset to GitHub.
        '''
        # Allow upload_asset() to work without an actual release asset file
        mock_isfile.return_value = True
        mock_open.return_value   = 'file_object'

        # There are three connected requests-related mocks at play here:
        # i) mock_session: the requests.session() function
        # ii) the session object returned by requests.session
        # iii) the mocked post() method of the mocked session object
        mock_session.return_value = mock.MagicMock(post = mock.MagicMock())

        tools.upload_asset(github_token = 'test_token', 
                           org          = 'gslab-econ', 
                           repo         = 'gslab_python', 
                           release_id   = 'test_release', 
                           file_name    = 'release.txt', 
                           content_type = 'text/markdown')

        # Check that upload_asset called a session object's post() method
        # once and with the correct arguments.
        mock_session.return_value.post.assert_called_once()

        keyword_args    = mock_session.return_value.post.call_args[1]
        positional_args = mock_session.return_value.post.call_args[0]

        self.assertEqual(keyword_args['files']['file'],            'file_object')
        self.assertEqual(keyword_args['headers']['Authorization'], 'token test_token')
        self.assertEqual(keyword_args['headers']['Content-Type'],  'text/markdown')
        
        # Check that the first positional argument matches the desired upload path
        desired_upload_path = ''.join(['https://uploads.github.com/repos/',
                                       'gslab-econ/gslab_python/releases/',
                                       'test_release/assets?name=release.txt'])
        self.assertEqual(positional_args[0], desired_upload_path)

    @mock.patch('gslab_scons._release_tools.requests.session')
    def test_upload_asset_bad_file(self, mock_session):
        '''
        Test that upload_asset() raises an error when its file_name
        argument isn't valid.
        '''
        mock_session.return_value = mock.MagicMock(post = mock.MagicMock())

        with self.assertRaises(ReleaseError), nostderrout():
            tools.upload_asset(github_token = 'test_token', 
                               org          = 'gslab-econ', 
                               repo         = 'gslab_python', 
                               release_id   = 'test_release', 
                               file_name    = 'nonexistent_file', 
                               content_type = 'text/markdown')

    @mock.patch('gslab_scons._release_tools.subprocess.call')
    def test_up_to_date(self, mock_call):
        '''
        Test that up_to_date() correctly recognises
        an SCons directory as up-to-date or out of date.
        '''
        # The mode argument needs to be one of the valid options
        with self.assertRaises(ReleaseError), nostderrout():
            gslab_scons._release_tools.up_to_date(mode = 'invalid')  

        # The mock of subprocess call should write pre-specified text
        # to stdout. This mock prevents us from having to set up real
        # SCons and git directories.
        mock_call.side_effect = \
            fx.make_call_side_effect('Your branch is up-to-date')
        self.assertTrue(gslab_scons._release_tools.up_to_date(mode = 'git'))

        mock_call.side_effect = \
            fx.make_call_side_effect('modified:   .sconsign.dblite')
        self.assertFalse(gslab_scons._release_tools.up_to_date(mode = 'git'))

        mock_call.side_effect = \
            fx.make_call_side_effect("scons: `.' is up to date.")
        self.assertTrue(gslab_scons._release_tools.up_to_date(mode = 'scons'))
        
        mock_call.side_effect = \
            fx.make_call_side_effect('python some_script.py')
        self.assertFalse(gslab_scons._release_tools.up_to_date(mode = 'scons'))

        # The up_to_date() function shouldn't work in SCons or git mode
        # when it is called outside of a SCons directory or a git 
        # repository, respectively.       
        mock_call.side_effect = \
            fx.make_call_side_effect("Not a git repository")
        with self.assertRaises(ReleaseError), nostderrout():
            gslab_scons._release_tools.up_to_date(mode = 'git')

        mock_call.side_effect = \
            fx.make_call_side_effect("No SConstruct file found")
        with self.assertRaises(ReleaseError), nostderrout():
            gslab_scons._release_tools.up_to_date(mode = 'scons')  

 
    @mock.patch('gslab_scons._release_tools.open')
    def test_extract_dot_git(self, mock_open):
        '''
        Test that extract_dot_git() correctly extracts repository
        information from a .git folder's config file.
        '''

        mock_open.side_effect = fx.dot_git_open_side_effect()

        repo_info = tools.extract_dot_git('.git')
        self.assertEqual(repo_info[0], 'repo')
        self.assertEqual(repo_info[1], 'org')
        self.assertEqual(repo_info[2], 'branch')

        # Ensure that extract_dot_git() raises an error when the directory
        # argument is not a .git folder.
        # i) The directory argument identifies an empty folder
        with self.assertRaises(ReleaseError):
            repo_info = tools.extract_dot_git('not/git')

        # ii) Mock the .git/config file so that url information is missing
        #      from its "[remote "origin"]" section. (We parse organisaton,
        #      repo, and branch information from this url.)
        mock_open.side_effect = fx.dot_git_open_side_effect(url = False)
        with self.assertRaises(ReleaseError):
            repo_info = tools.extract_dot_git('.git')


if __name__ == '__main__':
    unittest.main()

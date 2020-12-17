import unittest
import sys
import os
import re
import mock
import shutil
import requests
import copy
# Import modules containing gslab_scons test helper functions
import _test_helpers as helpers
import _side_effects as fx

# Ensure that Python can find and load the GSLab libraries
os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path.append('../..')

import gslab_scons
import gslab_scons._release_tools as tools
from gslab_scons._exception_classes import ReleaseError

#== Preliminaries ===================================================
# Create a patch for use in testing release()
# This patch allows test methods to introduce mocks in the place of
# numerous system commands used in release(). These mocks should be
# specified as arguments in test methods in the opposite order as the
# patches are listed below. 
#
# Note that time.sleep is just mocked to do nothing.
path = 'gslab_scons._release_tools'
patch_collection = \
    lambda f: mock.patch('%s.time.sleep'    % path, mock.MagicMock())(\
              mock.patch('%s.os.path.isdir' % path)(\
              mock.patch('%s.shutil.rmtree' % path)(                  \
              mock.patch('%s.upload_asset'  % path)(                  \
              mock.patch('%s.requests.session' % path)(               \
              mock.patch('%s.getpass.getpass' % path)(
              mock.patch('%s.os.makedirs' % path)(
              mock.patch('%s.shutil.copy' % path)(
              mock.patch('%s.shutil.make_archive' % path)(
              mock.patch('%s.shutil.move' % path)(\
              mock.patch('gslab_scons.misc.check_and_expand_path')(\
                f \
              )))))))))))

# Standard release() arguments
standard_args = {'vers':              'test_version',
                 'DriveReleaseFiles': ['paper.pdf', 'plot.pdf'],
                 'local_release':     'root/release/repo-test_branch',
                 'org':               'org',
                 'repo':              'repo',
                 'target_commitish':  'test_branch',
                 'zip_release':       True}

# This is mocked-up output from requests.session.get(path) based on 
# members of standard_args
org_repo = (standard_args['org'], standard_args['repo'])
#====================================================================

class TestReleaseFunction(unittest.TestCase):

    @patch_collection
    def test_release_standard(self, 
                              mock_cepath,
                              mock_move, 
                              mock_make_archive, 
                              mock_copy, 
                              mock_makedirs, 
                              mock_getpass, 
                              mock_session,
                              mock_upload, 
                              mock_rmtree,
                              mock_isdir):
        '''
        Test that release() correctly prepares a release
        that uploads zipped files to Google Drive.
        '''
        # Mock functions called by release() to simulate an actual call
        mock_getpass.return_value = 'test_token'
        mock_session.return_value = mock.MagicMock(post = mock.MagicMock(),
                                                   get  = mock.MagicMock())

        args = copy.deepcopy(standard_args)
        release_data = helpers.mock_release_data(args)
        mock_session.return_value.get.return_value.content = release_data

        # When org/repo refers to a nonexistent GitHub repository, 
        # make the release request fail. 
        mock_session.return_value.post.side_effect = fx.post_side_effect

        # Give mock_upload a side effect preserving release assets listing
        mock_upload.side_effect = fx.upload_asset_side_effect

        args['zip_release'] = True

        self.check_release(args, mock_session, mock_upload, mock_copy,
                           mock_make_archive, mock_move)

        # Test release() when DriveReleaseFiles is a string
        args['DriveReleaseFiles'] = 'plot.pdf'
        self.check_release(args, mock_session, mock_upload, mock_copy,
                           mock_make_archive, mock_move)

        # Test release() when required directories don't exist
        local_release = args['local_release']
        mock_isdir.return_value = False

        self.check_release(args, mock_session, mock_upload, mock_copy,
                           mock_make_archive, mock_move)

        # Did release() create the local_release subdirectory?
        mock_makedirs.assert_any_call(local_release)
        # Did it create the temporary directory for to-be-zipped release files?
        mock_makedirs.assert_any_call('release_content')

    def check_release(self, args, mock_session, mock_upload, mock_copy, 
                      mock_make_archive, mock_move):
        '''
        This helper method checks that test.release() works correctly
        with a given collection of arguments and a system configuration
        mocked by its assorted mock_* arguments.  
        '''
        
        for mock_object in [mock_session, mock_upload, mock_copy,
                           mock_make_archive, mock_move]:
            mock_object.reset_mock()

        tools.release(**args)

        mock_session.return_value.post.assert_called_once()
        post_args = mock_session.return_value.post.call_args

        # Check that the first positional argument of session.post() is 
        # the url to which we desire to make our release.
        desired_release_url = \
            'https://test_token:@api.github.com/repos/org/repo/releases'
        self.assertEqual(post_args[0][0], desired_release_url)

        # Check that the correct data was passed to session.post()
        data = post_args[1]['data']
        self.assertTrue(re.search('"body": ""', data))
        self.assertTrue(re.search('"name": "%s"' % args['vers'], data))
        self.assertTrue(re.search('"target_commitish": "%s"' % \
                                  args['target_commitish'], data))
        self.assertTrue(re.search('"tag_name": "%s"' % args['vers'], data))
        self.assertTrue(re.search('"prerelease": false', data))
        self.assertTrue(re.search('"draft": false', data))

        # Check that release() called upload_asset() with the correct arguments
        mock_upload.assert_called_once()
        # We expect test_ID to be the release ID given the mocked-up return value
        # of session.get()
        self.assertEqual(mock_upload.call_args[1]['release_id'], 'test_ID')

        # Check that release() prepared files for release correctly,
        # If we are zipping before releasing, then we should move
        # our release files into an intermediate folder to be zipped.
        if args['zip_release']:
            base = 'release_content'
        # Otherwise, we should move them directly into our 
        # local_release directory.
        else:
            base = args['local_release']

        drive_files = args['DriveReleaseFiles']
        if isinstance(drive_files, basestring):
            drive_files = [drive_files]

        for filename in drive_files:
            mock_copy.assert_any_call(filename, '%s/%s' % (base, filename))

        # ...that it zipped them if zip_release == True, ...
        if args['zip_release']:
            mock_make_archive.assert_called_with('release_content', 'zip', 
                                                 'release_content')
            # ...and that it moved them to the local_release directory
            mock_move.assert_called_with('release_content.zip', 
                                         '%s/release.zip' % args['local_release'])       
        else:
            mock_make_archive.assert_not_called()

        # Check that the assets listed in the file whose path is
        # passed to upload_asset() are those specified by release()'s 
        # DriveReleaseFiles argument.
        if args['DriveReleaseFiles']:
            with open('assets_listing.txt', 'rU') as assets:
                lines = assets.readlines()
    
            for line in lines:
                if not line == lines[0]:
                    # Extract the filename from the line of the assets listing
                    filename = os.path.basename(line.strip())
                    # Check that the filename is listed.
                    self.assertIn(filename, args['DriveReleaseFiles'])

            os.remove('assets_listing.txt')

    @patch_collection
    def test_release_nozip(self,
                           mock_cepath,
                           mock_move, 
                           mock_make_archive, 
                           mock_copy, 
                           mock_makedirs, 
                           mock_getpass, 
                           mock_session,
                           mock_upload, 
                           mock_rmtree,
                           mock_isdir):
        '''
        Test that release() correctly prepares a release
        that uploads unzipped files to Google Drive.
        '''
        # Mock functions called by release() to simulate an actual call
        mock_getpass.return_value = 'test_token'
        args = copy.deepcopy(standard_args)
        args['zip_release'] = False

        release_data = helpers.mock_release_data(args)
        mock_session.return_value.get.return_value.content = release_data

        # Give mock_upload a side effect preserving release assets listing
        mock_upload.side_effect = fx.upload_asset_side_effect

        self.check_release(args, mock_session, mock_upload, mock_copy,
                           mock_make_archive, mock_move)

    @patch_collection
    def test_release_no_drive(self,
                              mock_cepath,
                              mock_move, 
                              mock_make_archive, 
                              mock_copy, 
                              mock_makedirs, 
                              mock_getpass, 
                              mock_session,
                              mock_upload, 
                              mock_rmtree,
                              mock_isdir):
        '''
        Test that release() correctly prepares a release
        that does not upload files to Google Drive.
        '''
        # Mock functions called by release() to simulate an actual call
        args = copy.deepcopy(standard_args)
        args['DriveReleaseFiles'] = []

        release_data = helpers.mock_release_data(args)
        mock_session.return_value.get.return_value.content = release_data

        # Test without DriveReleaseFiles
        tools.release(**args)
        # Check that no file operations occur when no files are specified for release
        # to Google Drive.
        mock_copy.assert_not_called()      
        mock_makedirs.assert_not_called()
        mock_rmtree.assert_not_called()
        mock_make_archive.assert_not_called()
        mock_move.assert_not_called()
        mock_upload.assert_not_called()    

    @patch_collection
    def test_release_unintended_inputs(self,
                                       mock_cepath,
                                       mock_move, 
                                       mock_make_archive, 
                                       mock_copy, 
                                       mock_makedirs, 
                                       mock_getpass, 
                                       mock_session,
                                       mock_upload, 
                                       mock_rmtree,
                                       mock_isdir):
        '''
        Test that release() responds as expected to 
        unintended inputs.
        '''
        # Mock functions called by release() to simulate an actual call
        mock_getpass.return_value = 'test_token'
        args = copy.deepcopy(standard_args)

        release_data = helpers.mock_release_data(args)
        mock_session.return_value.get.return_value.content = release_data
        mock_session.return_value.post.side_effect = fx.post_side_effect

        args = copy.deepcopy(standard_args)

        # Inappropriate local_release argument and DriveReleaseFiles is empty.
        test_args = copy.deepcopy(args)
        test_args['DriveReleaseFiles'] = []
        test_args['local_release']     = 1
        try:
            tools.release(**test_args)
        except:
            self.fail("Running release() with an invalid local_release "
                      "argument and without files to be released to Google "
                      "Drive shouldn't raise an error!")

        # local_release is of an inappropriate type 
        self.check_failure({'local_release': 1}, AttributeError)

        # org/repo referss to a nonexistent GitHub repository
        self.check_failure({'org': 'orgg'}, requests.exceptions.HTTPError)
        self.check_failure({'repo': 1}, requests.exceptions.HTTPError)

        # Some error-inducing DriveReleaseFiles arguments
        self.check_failure({'DriveReleaseFiles': True}, TypeError)
        self.check_failure({'DriveReleaseFiles': [1, 2, 3]}, AttributeError)

    def check_failure(self, changes, expected_error):
        '''
        Check that release() fails with `expected_error` when
        its arguments deviate from standard ones as specified in `changes`.
        '''
        test_args = copy.deepcopy(standard_args)

        for changed_arg in changes.keys():
            test_args[changed_arg] = changes[changed_arg]

        with self.assertRaises(expected_error):
            tools.release(**test_args)  
    

if __name__ == '__main__':
    unittest.main()

# coding=utf-8
import unittest
import sys
import os
import time

sys.path.append(os.path.join("..", "src", "bin"))

from file_meta_data import FilePathField, FileMetaDataModularInput, DataSizeField
from file_info_app.modular_input import Field, FieldValidationException, DurationField

class TestDurationField(unittest.TestCase):
    """
    Tests the duration field.
    """

    def test_duration_valid(self):
        """
        Tests the conversion of the duration string to an integer.
        """
        duration_field = DurationField("test_duration_valid", "title", "this is a test")

        self.assertEqual(duration_field.to_python("1m"), 60)
        self.assertEqual(duration_field.to_python("5m"), 300)
        self.assertEqual(duration_field.to_python("5 minute"), 300)
        self.assertEqual(duration_field.to_python("5"), 5)
        self.assertEqual(duration_field.to_python("5h"), 18000)
        self.assertEqual(duration_field.to_python("2d"), 172800)
        self.assertEqual(duration_field.to_python("2w"), 86400 * 7 * 2)

    def test_url_field_invalid(self):
        """
        Ensure that invalid URL fields are detected.
        """

        duration_field = DurationField("test_url_field_invalid", "title", "this is a test")

        self.assertRaises(FieldValidationException, lambda: duration_field.to_python("1 treefrog"))
        self.assertRaises(FieldValidationException, lambda: duration_field.to_python("minute"))

class TestFileMetaDataModularInput(unittest.TestCase):
    """
    Tests for the input class.
    """

    def test_is_expired(self):
        """
        Make sure that the input can determine when the last result is expired.
        """

        self.assertFalse(FileMetaDataModularInput.is_expired(time.time(), 30))
        self.assertTrue(FileMetaDataModularInput.is_expired(time.time() - 31, 30))

    def test_get_files_data(self):
        """
        Test loading of file data for a directory.
        """

        results = FileMetaDataModularInput.get_files_data(".")
        self.assertTrue(len(results) > 0)

    def test_get_file_data(self):
        """
        Test loading of file data for a file.
        """

        result, _ = FileMetaDataModularInput.get_file_data("..")
        self.assertEquals(result['is_directory'], 1)

    def test_get_files_data_file_count(self):
        """
        Test loading of file count.
        """

        results, _ = FileMetaDataModularInput.get_files_data("../src")

        self.assertGreaterEqual(len(results), 5)

        for result in results:
            if result['path'].endswith('file_info_app'):
                self.assertGreaterEqual(result['file_count'], 2)

            if result['path'].endswith('bin'):
                self.assertGreaterEqual(result['file_count'], 1)

    def test_get_files_data_missing_root_directory(self):
        """
        Ensure that the root directory is included in the results.

        http://lukemurphey.net/issues/1023
        """

        results, _ = FileMetaDataModularInput.get_files_data("../src/bin")

        self.assertGreaterEqual(len(results), 5)

        # By default. assume the root directory was not found
        root_directory_included = False

        for result in results:

            if result['path'].endswith('bin'):
                root_directory_included = True

                self.assertGreaterEqual(result['file_count'], 1)
                self.assertGreaterEqual(result['file_count_recursive'], 3)
                self.assertEqual(result['directory_count_recursive'], 1)

        if not root_directory_included:
            self.fail("Root directory was not included in the results")

    def test_get_files_data_missing_invalid_directory(self):
        """
        Ensure that the input correctly handles the case where the directory requested doesn't exist.
        """

        # This shouldn't throw an exception
        results, _ = FileMetaDataModularInput.get_files_data("../src/bin/does_not_exist")
        self.assertEquals(results, [])

    def test_get_file_data_file_count_on_root(self):
        """
        Ensure that the input correctly handles the case where the directory requested does exist.
        """

        result, _ = FileMetaDataModularInput.get_file_data("../src/bin")
        self.assertGreaterEqual(result['file_count'], 1)
        self.assertGreaterEqual(result['directory_count'], 1)

    def test_get_files_data_only_if_later_all(self):
        """
        Test only get files onlky if they are after the given time.
        """

        results, _ = FileMetaDataModularInput.get_files_data("../src/bin", must_be_later_than=10)

        self.assertGreaterEqual(len(results), 5)

        # By default. assume the root directory was not found
        root_directory_included = False

        for result in results:

            if result['path'].endswith('bin'):
                root_directory_included = True

                self.assertGreaterEqual(result['file_count'], 1)
                self.assertGreaterEqual(result['file_count_recursive'], 3)
                self.assertEqual(result['directory_count_recursive'], 1)

        if not root_directory_included:
            self.fail("Root directory was not included in the results")

    def print_results(self, results):
        """
        Print the provided results that came from the input (useful for debugging)
        """

        print "\n\nPrinting results of length", len(results)
        for result in results:

            appendix = ""

            if result['is_directory'] == 1:
                appendix = "(directory)"

            print result['path'], appendix

    def test_get_files_depth_limit(self):
        """
        Get files from a directory but limit to a depth limit.
        https://lukemurphey.net/issues/2041
        """

        results, _ = FileMetaDataModularInput.get_files_data("test_dir", must_be_later_than=10,
                                                             depth_limit=2)
        self.assertGreaterEqual(len(results), 7)

        # By default. assume the root directory was not found
        root_directory_included = False

        for result in results:

            if result['path'].endswith('test_dir'):
                root_directory_included = True

                self.assertEqual(result['file_count'], 2)
                self.assertEqual(result['file_count_recursive'], 4)
                self.assertEqual(result['directory_count_recursive'], 3)

            if result['path'].endswith('dir_1'):

                self.assertGreaterEqual(result['file_count'], 1)
                self.assertNotIn('file_count_recursive', result)
                self.assertNotIn('directory_count_recursive', result)

        if not root_directory_included:
            self.fail("Root directory was not included in the results")

    def test_get_files_depth_limit_single(self):
        """
        Get the files data but only for the first level.
        https://lukemurphey.net/issues/2041
        """

        results, _ = FileMetaDataModularInput.get_files_data("test_dir", must_be_later_than=10,
                                                             depth_limit=1)
        self.assertGreaterEqual(len(results), 5)

        # By default. assume the root directory was not found
        root_directory_included = False

        for result in results:

            if result['path'].endswith('test_dir'):
                root_directory_included = True

                self.assertEqual(result['file_count'], 2)
                self.assertEqual(result['file_count_recursive'], 2)
                self.assertEqual(result['directory_count_recursive'], 2)

            if result['path'].endswith('dir_1'):
                self.assertEqual(result['file_count'], 1)
                self.assertNotIn('file_count_recursive', result)
                self.assertNotIn('directory_count_recursive', result)

        if not root_directory_included:
            self.fail("Root directory was not included in the results")

    def test_get_files_data_only_if_later_none(self):
        """
        Test getting files but only those after the given time (which should return none since the
        time is in the future)
        """

        max_time = time.time() + 86400
        results = FileMetaDataModularInput.get_files_data("../src/bin", must_be_later_than=max_time)

        self.assertGreaterEqual(len(results), 0)

    def test_get_files_data_return_latest_time(self):
        """
        Test getting the files data and confirm that the latest time of the files observed is
        correct.
        """

        results, latest_time = FileMetaDataModularInput.get_files_data("../src/bin", latest_time=0)

        self.assertGreaterEqual(len(results), 5)
        self.assertGreaterEqual(latest_time, 1435391730)

        # By default. assume the root directory was not found
        root_directory_included = False

        for result in results:

            if result['path'].endswith('bin'):
                root_directory_included = True

                self.assertGreaterEqual(result['file_count'], 1)
                self.assertGreaterEqual(result['file_count_recursive'], 3)
                self.assertEqual(result['directory_count_recursive'], 1)

        if not root_directory_included:
            self.fail("Root directory was not included in the results")

    def test_get_file_hash(self):
        """
        Test getting the file hash from the file.
        """

        self.assertEqual(FileMetaDataModularInput.get_file_hash("test_dir/1.txt"), "5154aaa49392fb275ce7e12a7d3e00901cf9cf3ab10491673f97322f")

    def test_get_files_hash(self):
        """
        Test getting the hash via the files data.
        """

        results, _ = FileMetaDataModularInput.get_files_data("test_dir/dir_1", latest_time=0,
                                                                       file_hash_limit=10000000)
        file_found = False
        for result in results:

            if result['path'].endswith('5.txt'):
                file_found = True
                self.assertEqual(result['sha224'], "66f826f054e6b3e2edbaddd34ae7f257d9a1dc1fecdf9bbfc576edf4")
    
        self.assertTrue(file_found)    

    def test_get_files_hash_limit(self):
        """
        Test getting the hash but only for files that are under the given size.
        """

        results, _ = FileMetaDataModularInput.get_files_data("../src/bin", latest_time=0,
                                                             file_hash_limit=400)

        for result in results:

            if result['path'].endswith('modular_input.py'):
                if 'sha224' in result:
                    self.fail("Hash should have been skipped")

    def test_remove_substrs(self):
        """
        Test removing the sub-strings from the string.
        """

        self.assertEqual(FileMetaDataModularInput.remove_substrs("ACCESS_ALLOWED_ACE_TYPE", ["_ACE_TYPE"]), "ACCESS_ALLOWED")
        self.assertEqual(FileMetaDataModularInput.remove_substrs("INHERIT_ONLY_ACE", ["_ACE", "_ACE_TYPE"]), "INHERIT_ONLY")

class TestFileSizeField(unittest.TestCase):
    """
    Tests the file size field.
    """

    def test_file_size_valid(self):
        """
        Test converting a file size to an integer.
        """

        file_size_field = DataSizeField("test_file_size_valid", "title", "this is a test")

        self.assertEqual(file_size_field.to_python("1m"), 1024 * 1024)
        self.assertEqual(file_size_field.to_python("5m"), 1024 * 1024 * 5)
        self.assertEqual(file_size_field.to_python("5mb"), 1024 * 1024 * 5)
        self.assertEqual(file_size_field.to_python("5 mb"), 1024 * 1024 * 5)
        self.assertEqual(file_size_field.to_python("5 MB"), 1024 * 1024 * 5)
        self.assertEqual(file_size_field.to_python("5MB"), 1024 * 1024 * 5)

        self.assertEqual(file_size_field.to_python("5"), 5)
        self.assertEqual(file_size_field.to_python("1k"), 1024)

    def test_file_size_invalid(self):
        """
        Ensure that invalid file sizes are correctly detected as invalid.
        """

        file_size_field = DataSizeField("test_file_size_invalid", "title", "this is a test")

        with self.assertRaises(FieldValidationException):
            file_size_field.to_python("1 treefrog")

        with self.assertRaises(FieldValidationException):
            file_size_field.to_python("mb")

class TestFileMetaDataWindows(unittest.TestCase):
    """
    Tests the loading of file meta-data on Windows.
    """

    def test_get_windows_acl_data_file(self):
        """
        Ensure that file ACL data for Windows is returned.
        """

        output = FileMetaDataModularInput.get_windows_acl_data("../src/bin/file_meta_data.py")

        self.assertEqual(output["owner_sid"][0:5], "S-1-5")
        self.assertEqual(output["group_sid"][0:5], "S-1-5")
        self.assertEqual(output["ace_0_type"], ["ACCESS_ALLOWED"])
        self.assertGreaterEqual(output["ace_0_permissions"].index("FILE_GENERIC_READ"), 0)
 
    def test_get_windows_acl_data_dir(self):
        """
        Ensure that directory ACL data for Windows is returned.
        """

        output = FileMetaDataModularInput.get_windows_acl_data("../src/bin")

        self.assertEqual(output["owner_sid"][0:5], "S-1-5")
        self.assertEqual(output["group_sid"][0:5], "S-1-5")
        self.assertEqual(output["ace_0_type"], ["ACCESS_ALLOWED"])
        self.assertGreaterEqual(output["ace_0_permissions"].index("READ_CONTROL"), 0)

class TestFileMetaDataNix(unittest.TestCase):
    """
    Tests the loading of file meta-data on Unix.
    """

    def test_get_nix_acl_data_file(self):
        """
        Ensure that file ACL data for Unix is returned.
        """

        output = FileMetaDataModularInput.get_nix_acl_data("../src/bin/file_meta_data.py")

        self.assertGreaterEqual(output["owner_uid"], 1)
        self.assertGreaterEqual(len(output["owner"]), 1)
        self.assertGreaterEqual(output["group_uid"], 0)
        self.assertGreaterEqual(output["permission_mask"], 0)

    def test_get_nix_acl_data_dir(self):
        """
        Ensure that directory ACL data for Unix is returned.
        """

        output = FileMetaDataModularInput.get_nix_acl_data("../src/bin")

        self.assertGreaterEqual(len(output["owner"]), 1)
        self.assertGreaterEqual(output["group_uid"], 0)
        self.assertGreaterEqual(output["permission_mask"], 0)


def run_tests():
    """
    Run the tests.
    """

    loader = unittest.TestLoader()
    suites = []
    suites.append(loader.loadTestsFromTestCase(TestFileMetaDataModularInput))
    suites.append(loader.loadTestsFromTestCase(TestFileSizeField))
    suites.append(loader.loadTestsFromTestCase(TestDurationField))

    if os.name == 'nt':
        suites.append(loader.loadTestsFromTestCase(TestFileMetaDataWindows))
    else:
        print "Warning: Windows specific tests will be skipped since this host is not running Windows"

    if os.name == 'posix':
        suites.append(loader.loadTestsFromTestCase(TestFileMetaDataNix))
    else:
        print "Warning: POSIX specific tests will be skipped since this host is not running Unix or Linux"

    unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(suites))

if __name__ == "__main__":
    run_tests()

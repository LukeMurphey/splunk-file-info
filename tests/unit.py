# coding=utf-8
import unittest
import sys
import os
import time
import shutil
import re
import tempfile
import threading
import unicodedata
from StringIO import StringIO

sys.path.append( os.path.join("..", "src", "bin") )

from file_meta_data import FilePathField, FileMetaDataModularInput, DataSizeField
from file_info_app.modular_input import Field, FieldValidationException

class TestDurationField(unittest.TestCase):
    
    def test_duration_valid(self):
        duration_field = DurationField( "test_duration_valid", "title", "this is a test" )
        
        self.assertEqual( duration_field.to_python("1m"), 60 )
        self.assertEqual( duration_field.to_python("5m"), 300 )
        self.assertEqual( duration_field.to_python("5 minute"), 300 )
        self.assertEqual( duration_field.to_python("5"), 5 )
        self.assertEqual( duration_field.to_python("5h"), 18000 )
        self.assertEqual( duration_field.to_python("2d"), 172800 )
        self.assertEqual( duration_field.to_python("2w"), 86400 * 7 * 2 )
        
    def test_url_field_invalid(self):
        duration_field = DurationField( "test_url_field_invalid", "title", "this is a test" )
        
        self.assertRaises( FieldValidationException, lambda: duration_field.to_python("1 treefrog") )
        self.assertRaises( FieldValidationException, lambda: duration_field.to_python("minute") )   
    
class TestFileMetaDataModularInput(unittest.TestCase):
    
    def get_test_dir(self):
        return os.path.dirname(os.path.abspath(__file__))
    
    def test_is_expired(self):
        self.assertFalse( FileMetaDataModularInput.is_expired(time.time(), 30) )
        self.assertTrue( FileMetaDataModularInput.is_expired(time.time() - 31, 30) )
    
    def test_get_files_data(self):
        
        results = FileMetaDataModularInput.get_files_data(".")
        self.assertTrue( len(results) > 0 )
        
    def test_get_file_data(self):
        
        result, _ = FileMetaDataModularInput.get_file_data("..")
        self.assertEquals( result['is_directory'], 1 )
        
    def test_get_files_data_file_count(self):
        results, _ = FileMetaDataModularInput.get_files_data("../src")
        
        self.assertGreaterEqual( len(results), 5 )
        
        for result in results:
            if result['path'].endswith('file_info_app'):
                self.assertGreaterEqual( result['file_count'], 2 )
                
            if result['path'].endswith('bin'):
                self.assertGreaterEqual( result['file_count'], 1 )
     
    def test_get_files_data_missing_root_directory(self):
        # http://lukemurphey.net/issues/1023
        
        results, _ = FileMetaDataModularInput.get_files_data("../src/bin")
        
        self.assertGreaterEqual( len(results), 5 )
        
        # By default. assume the root directory was not found
        root_directory_included = False
        
        for result in results:
                
            if result['path'].endswith('bin'):
                root_directory_included = True
                
                self.assertGreaterEqual( result['file_count'], 1 )
                self.assertGreaterEqual( result['file_count_recursive'], 3 )
                self.assertEqual( result['directory_count_recursive'], 1 )
                
        if not root_directory_included:
            self.fail("Root directory was not included in the results")
    
    def test_get_files_data_missing_invalid_directory(self):
        
        # This shouldn't throw an exception
        results, _ = FileMetaDataModularInput.get_files_data("../src/bin/does_not_exist")
        self.assertEquals( results, [] )
    
    def test_get_file_data_file_count_on_root(self):
        
        result, _ = FileMetaDataModularInput.get_file_data("../src/bin")
        self.assertGreaterEqual( result['file_count'], 1 )
        self.assertGreaterEqual( result['directory_count'], 1 )
    
    def test_get_files_data_only_if_later_all(self):
        
        results, _ = FileMetaDataModularInput.get_files_data("../src/bin", must_be_later_than=10)
        
        self.assertGreaterEqual( len(results), 5 )
        
        # By default. assume the root directory was not found
        root_directory_included = False
        
        for result in results:
                
            if result['path'].endswith('bin'):
                root_directory_included = True
                
                self.assertGreaterEqual( result['file_count'], 1 )
                self.assertGreaterEqual( result['file_count_recursive'], 3 )
                self.assertEqual( result['directory_count_recursive'], 1 )
                
        if not root_directory_included:
            self.fail("Root directory was not included in the results")
            
    def test_get_files_data_only_if_later_none(self):
        
        results = FileMetaDataModularInput.get_files_data("../src/bin", must_be_later_than=time.time() + 86400)
        
        self.assertGreaterEqual( len(results), 0 )
            
    def test_get_files_data_return_latest_time(self):
        
        results, latest_time = FileMetaDataModularInput.get_files_data("../src/bin", latest_time=0)
        
        self.assertGreaterEqual( len(results), 5 )
        self.assertGreaterEqual( latest_time, 1435391730 )
        
        # By default. assume the root directory was not found
        root_directory_included = False
        
        for result in results:
                
            if result['path'].endswith('bin'):
                root_directory_included = True
                
                self.assertGreaterEqual( result['file_count'], 1 )
                self.assertGreaterEqual( result['file_count_recursive'], 3 )
                self.assertEqual( result['directory_count_recursive'], 1 )
                
        if not root_directory_included:
            self.fail("Root directory was not included in the results")
            
    def test_get_file_hash(self):
        self.assertEqual(FileMetaDataModularInput.get_file_hash("../src/bin/file_info_app/modular_input.py"), "63c9c5dcf8e231fc7a997bd8f33352b2a0d3a43251620105db92fb1c")
            
    def test_get_files_hash(self):
        
        results, latest_time = FileMetaDataModularInput.get_files_data("../src/bin", latest_time=0, file_hash_limit=10000000)
        
        for result in results:
                
            if result['path'].endswith('modular_input.py'):
                self.assertEqual( result['sha224'], "63c9c5dcf8e231fc7a997bd8f33352b2a0d3a43251620105db92fb1c" )
                
    def test_get_files_hash_limit(self):
        
        results, latest_time = FileMetaDataModularInput.get_files_data("../src/bin", latest_time=0, file_hash_limit=400)
        
        for result in results:
                
            if result['path'].endswith('modular_input.py'):
                if 'sha224' in result:
                    self.fail("Hash should have been skipped")
            
class TestFileSizeField(unittest.TestCase):
    
    def test_file_size_valid(self):
        file_size_field = DataSizeField( "test_file_size_valid", "title", "this is a test" )
        
        self.assertEqual( file_size_field.to_python("1m"), 1024 * 1024 )
        self.assertEqual( file_size_field.to_python("5m"), 1024 * 1024 * 5 )
        self.assertEqual( file_size_field.to_python("5mb"), 1024 * 1024 * 5 )
        self.assertEqual( file_size_field.to_python("5 mb"), 1024 * 1024 * 5 )
        self.assertEqual( file_size_field.to_python("5 MB"), 1024 * 1024 * 5 )
        self.assertEqual( file_size_field.to_python("5MB"), 1024 * 1024 * 5 )
        
        self.assertEqual( file_size_field.to_python("5"), 5 )
        self.assertEqual( file_size_field.to_python("1k"), 1024 )
        
    def test_file_size_invalid(self):
        file_size_field = DataSizeField( "test_file_size_invalid", "title", "this is a test" )
        
        with self.assertRaises(FieldValidationException):
            file_size_field.to_python("1 treefrog")
            
        with self.assertRaises(FieldValidationException):
            file_size_field.to_python("mb")
        
class TestFileMetaDataWindows(unittest.TestCase):
    
    def test_get_windows_acl_data_file(self):
        output = FileMetaDataModularInput.get_windows_acl_data("../src/bin/file_meta_data.py")
        
        self.assertEqual(output["owner_sid"][0:5], "S-1-5" )
        self.assertEqual(output["group_sid"][0:5], "S-1-5" )
        self.assertEqual(output["ace_0_type"], "ACCESS_ALLOWED_ACE_TYPE" )
        self.assertGreaterEqual(output["ace_0_permissions"].index("FILE_GENERIC_READ" ), 0)
        
    def test_get_windows_acl_data_dir(self):
        output = FileMetaDataModularInput.get_windows_acl_data("../src/bin")
        
        self.assertEqual(output["owner_sid"][0:5], "S-1-5" )
        self.assertEqual(output["group_sid"][0:5], "S-1-5" )
        self.assertEqual(output["ace_0_type"], "ACCESS_ALLOWED_ACE_TYPE" )
        self.assertGreaterEqual(output["ace_0_permissions"].index("READ_CONTROL" ), 0)
        
if __name__ == "__main__":
    loader = unittest.TestLoader()
    suites = []
    suites.append(loader.loadTestsFromTestCase(TestFileMetaDataModularInput))
    suites.append(loader.loadTestsFromTestCase(TestFileSizeField))
    
    if os.name == 'nt':
        suites.append(loader.loadTestsFromTestCase(TestFileMetaDataWindows))
    else:
        print "Warning: Windows specific tests will be skipped since this host is not running Windows"
    
    unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(suites))
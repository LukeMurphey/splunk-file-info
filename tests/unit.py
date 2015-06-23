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
sys.path.append( os.path.join("..", "src", "bin", "file_info_app") )

from file_meta_data import FilePathField, FileMetaDataModularInput
from modular_input import Field, FieldValidationException

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
        
        result = FileMetaDataModularInput.get_file_data("..")
        self.assertEquals( result['is_directory'], 1 )
        
if __name__ == "__main__":
    loader = unittest.TestLoader()
    suites = []
    suites.append(loader.loadTestsFromTestCase(TestFileMetaDataModularInput))
    
    unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(suites))
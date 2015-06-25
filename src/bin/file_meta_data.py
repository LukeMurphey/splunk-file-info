import sys
import time
import re
import urllib2
import os

from file_info_app.modular_input import ModularInput, DurationField, BooleanField, Field

class FilePathField(Field):
    """
    Represents a file or directory path.
    """
    
    def to_python(self, value):
        Field.to_python(self, value)
        
        return value
    
    def to_string(self, value):
        return value.geturl()

class FileMetaDataModularInput(ModularInput):
    """
    The file meta-data modular input retrieves file meta-data into Splunk.
    """
    
    def __init__(self):

        scheme_args = {'title': "File Meta-data",
                       'description': "Import file and directory meta-data (size, modification dates, etc.)",
                       'use_external_validation': "true",
                       'streaming_mode': "xml",
                       'use_single_instance': "true"}
        
        args = [
                FilePathField("file_path", "File or directory path", "The path of the to get information on", empty_allowed=False),
                BooleanField("recurse", "Recursively iterate sub-directories", "Indicates whether sub-directories ought to be recursed ", empty_allowed=False),
                DurationField("interval", "Interval", "The interval defining how often to import the feed; can include time units (e.g. 15m for 15 minutes, 8h for 8 hours)", empty_allowed=False)
                ]
        
        ModularInput.__init__( self, scheme_args, args, logger_name='file_meta_data_modular_input' )
        
    @classmethod
    def boolean_to_int(cls, boolean):
        if boolean:
            return 1
        else:
            return 0
        
    @classmethod
    def get_files_data(cls, file_path, logger=None):
        
        results = []
        
        for root, dirs, files in os.walk(file_path, topdown=True):
                
                for name in files:
                    info = cls.get_file_data(os.path.join(root, name), logger)
                    
                    if info is not None:
                        results.append(info)
                    
                for name in dirs:
                    info = cls.get_file_data(os.path.join(root, name), logger)
                    
                    if info is not None:
                        results.append(info)
                    
        return results
        
    @classmethod
    def get_file_data(cls, file_path, logger=None):
        
        result = {}
        
        # Determine if the file is a directory
        result['is_directory'] = cls.boolean_to_int(os.path.isdir(file_path))
        
        # Get the absolute path
        result['path'] = os.path.abspath(file_path) 
        
        # Get the meta-data
        try:
            stat_info = os.stat(file_path)
        except WindowsError, OSError:
            # File not found or inaccessible
            return None
        
        for attribute in dir(stat_info):
            if attribute.startswith("st_"):
                    
                if 'time' in attribute:
                    result[attribute[3:]] = time.ctime(getattr(stat_info, attribute))
                    
                    # Include the time in raw format
                    result[attribute[3:] + "_epoch"] = getattr(stat_info, attribute)
                else:
                    result[attribute[3:]] = getattr(stat_info, attribute)

        return result
        
        
    def run(self, stanza, cleaned_params, input_config):
        
        # Make the parameters
        interval             = cleaned_params["interval"]
        file_path            = cleaned_params["file_path"]
        recurse              = cleaned_params.get("recurse", True)
        sourcetype           = cleaned_params.get("sourcetype", "file_meta_data")
        host                 = cleaned_params.get("host", None)
        index                = cleaned_params.get("index", "default")
        source               = stanza
        
        if self.needs_another_run(input_config.checkpoint_dir, stanza, interval):
            
            # Get the date of the latest entry imported
            try:
                checkpoint_data = self.get_checkpoint_data(input_config.checkpoint_dir, stanza, throw_errors=True)
            except IOError:
                checkpoint_data = None
            except ValueError:
                self.logger.exception("Exception generated when attempting to load the check-point data")
                checkpoint_data = None
            
            # Get the file information
            if recurse:
                results = self.get_files_data(file_path, logger=self.logger)
            else:
                results = [self.get_file_data(file_path, logger=self.logger)]
                
            self.logger.info("Successfully retrieved file data, count=%i, path=%s", len(results), file_path)
            
            # Output the event
            for result in results:
                
                # Add the time
                result['time'] = time.strftime("%a %b %d %H:%M:%S %Y")
                
                self.output_event(result, stanza, index=index, source=source, sourcetype=sourcetype, host=host, unbroken=True, close=True)
                
            # Get the time that the input last ran
            if checkpoint_data is not None and 'last_ran' in checkpoint_data:
                last_ran = checkpoint_data['last_ran']
            else:
                last_ran = None
            
            self.save_checkpoint_data(input_config.checkpoint_dir, stanza, { 'last_run' : self.get_non_deviated_last_run(last_ran, interval, stanza)})
            
if __name__ == '__main__':
    
    file_meta_data_input = None
    
    try:
        file_meta_data_input = FileMetaDataModularInput()
        file_meta_data_input.execute()
        sys.exit(0)
    except Exception as e:
        
        # This logs general exceptions that would have been unhandled otherwise (such as coding errors)
        if file_meta_data_input is not None:
            file_meta_data_input.logger.exception("Unhandled exception was caught, this may be due to a defect in the script")
        
        raise e
        
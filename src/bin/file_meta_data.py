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
                BooleanField("recurse", "Recursively iterate sub-directories", "Indicates whether sub-directories ought to be recursed", empty_allowed=False),
                BooleanField("only_if_changed", "Changed items only", "Only include items when one of the time fields is changed", empty_allowed=False),
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
    def get_files_data(cls, file_path, logger=None, latest_time=None, must_be_later_than=None):
        
        results = []
        
        total_file_count = 0
        total_dir_count = 0
        
        if latest_time is not None:
            latest_time_derived = latest_time
        else:
            latest_time_derived = 0
            only_include_later = False
            
        this_latest_time = None
        
        for root, dirs, files in os.walk(file_path, topdown=True):
                
                for name in files:
                    info, this_latest_time = cls.get_file_data(os.path.join(root, name), logger, latest_time_derived, must_be_later_than)
                    
                    # Sum up the file count
                    total_file_count += len(files)
                    
                    if info is not None:
                        results.append(info)
                        
                    if this_latest_time is not None:
                        latest_time_derived = this_latest_time
                    
                for name in dirs:
                    info, this_latest_time = cls.get_file_data(os.path.join(root, name), logger, latest_time_derived, must_be_later_than)
                    
                    # Sum up the directory count
                    total_dir_count += len(dirs)
                    
                    if info is not None:
                        results.append(info)
                                      
                    if this_latest_time is not None:
                        latest_time_derived = this_latest_time
                        
        # Handle the root directory too
        root_result, latest_time_derived = cls.get_file_data(file_path, logger, latest_time_derived, must_be_later_than)
        
        if root_result is not None:
            root_result['file_count_recursive'] = total_file_count
            root_result['directory_count_recursive'] = total_dir_count
            results.append(root_result)
        
        # Return the latest time if it was provided
        if latest_time is not None:
            return results, latest_time_derived
        else:
            return results
        
    @classmethod
    def get_file_data(cls, file_path, logger=None, latest_time=None, must_be_later_than=None):
        
        try:
            result = {}
            
            # Determine if the file is a directory
            is_directory = os.path.isdir(file_path)
            result['is_directory'] = cls.boolean_to_int(is_directory)
            
            if is_directory:
                path, dirs, files = os.walk(file_path).next()
                result['file_count'] = len(files)
                result['directory_count'] = len(dirs)
            
            # Get the absolute path
            result['path'] = os.path.abspath(file_path) 
            
            # Get the meta-data
            stat_info = os.stat(file_path)
            
            # By default, assume the item is not later than the latest_time parameter unless we prove otherwise
            is_item_later_than_latest_date = False
            this_latest_time = 0
            
            for attribute in dir(stat_info):
                if attribute.startswith("st_"):
                        
                    if 'time' in attribute:
                        result[attribute[3:]] = time.ctime(getattr(stat_info, attribute))
                        
                        # Save the latest value of the time field
                        if latest_time is not None and getattr(stat_info, attribute) > latest_time:
                            latest_time = getattr(stat_info, attribute)
                        
                        # Determine if any of the modification or creation times are later than the filter
                        if attribute != "st_atime" and getattr(stat_info, attribute) > must_be_later_than:
                            logger.info("Time is later than filter, %s=%r, must_be_later_than=%r, path=%r", attribute, getattr(stat_info, attribute), must_be_later_than, file_path)
                            is_item_later_than_latest_date = True
                        
                        # Include the time in raw format
                        result[attribute[3:] + "_epoch"] = getattr(stat_info, attribute)
                    else:
                        result[attribute[3:]] = getattr(stat_info, attribute)
    
            # Return just the result if it was provided
            if latest_time is None and is_item_later_than_latest_date:
                return result
            
            # Return just the none as the result if the it doesn't pass the filter
            elif latest_time is None and not is_item_later_than_latest_date:
                return result
            
            # Return both the result and the latest time if items passed the filer
            elif latest_time is not None and is_item_later_than_latest_date:
                return result, latest_time
            
            # Return no result
            else: # if latest_time is not None and not is_item_later_than_latest_date:
                return None, latest_time
    
        except OSError:
            # File not found or inaccessible
            if logger:
                logger.info('Unable to access path="%s"', file_path)
                
            if latest_time is not None:
                return None, latest_time
            else:
                return None
        
    def save_checkpoint(self, checkpoint_dir, stanza, last_run, latest_file_system_date):
        """
        Save the checkpoint state.
        
        Arguments:
        checkpoint_dir -- The directory where checkpoints ought to be saved
        stanza -- The stanza of the input being used
        last_run -- The time when the analysis was last performed
        latest_file_system_date -- The latest date observed on the file-system
        """
                
        self.save_checkpoint_data(checkpoint_dir, stanza, { 'last_run' : last_run,
                                                            'latest_file_system_date' : latest_file_system_date
                                                           })
        
    def get_latest_file_system_date(self, checkpoint_dir, stanza):
        """
        Get the latest date observed on the file-system.
        
        Arguments:
        checkpoint_dir -- The directory where checkpoints ought to be saved and stored
        stanza -- The stanza of the input being used
        """
        
        data = self.get_checkpoint_data(checkpoint_dir, stanza)
        
        if data is not None:
            return data.get('latest_file_system_date', 0)
        else:
            return 0
        
    def run(self, stanza, cleaned_params, input_config):
        
        # Make the parameters
        interval             = cleaned_params["interval"]
        file_path            = cleaned_params["file_path"]
        recurse              = cleaned_params.get("recurse", True)
        only_if_changed      = cleaned_params.get("only_if_changed", False)
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
            
            # Load the latest_time
            if checkpoint_data is not None:
                latest_time = checkpoint_data.get('latest_file_system_date', 0)
            else:
                latest_time = 0
            
            # Set up the filter to indicate which items are considered new
            if only_if_changed:
                must_be_later_than = latest_time
            else:
                must_be_later_than = None
            
            # Get the file information
            if recurse:
                results, new_latest_time = self.get_files_data(file_path, logger=self.logger, latest_time=latest_time, must_be_later_than=must_be_later_than)
            else:
                results, new_latest_time = [self.get_file_data(file_path, logger=self.logger, latest_time=latest_time, must_be_later_than=must_be_later_than)]
                
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
            
            # Identify the correct latest time
            if new_latest_time > latest_time:
                latest_time = new_latest_time
            
            self.save_checkpoint(input_config.checkpoint_dir, stanza, self.get_non_deviated_last_run(last_ran, interval, stanza), latest_time)
            
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
        
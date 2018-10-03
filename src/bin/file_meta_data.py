import sys
import time
import re
import os
import hashlib
import collections

try:
    import win32security, ntsecuritycon
    win_imports_available = True
except:
    win_imports_available = False

try:
    import pwd
    nix_import_available = True
except:
    nix_import_available = False

path_to_mod_input_lib = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'modular_input.zip')
sys.path.insert(0, path_to_mod_input_lib)

from modular_input import ModularInput, DurationField, BooleanField, IntegerField, WildcardField, Field, FieldValidationException

class FilePathField(Field):
    """
    Represents a file or directory path.
    """

    def to_python(self, value, session_key=None):
        Field.to_python(self, value, session_key=None)

        return value

    def to_string(self, value):
        return value.geturl()

class DataSizeField(Field):
    """
    This field represents data size as represented by a string such as 1mb for 1 megabyte.

    The string is converted to an integer indicating the number of bytes.
    """

    DATA_SIZE_RE = re.compile("(?P<size>[0-9]+)\s*(?P<units>[a-z]*)", re.IGNORECASE)

    KB = 1024
    MB = 1024 * KB
    GB = 1024 * MB
    TB = 1024 * GB
    PB = 1024 * TB
    EB = 1024 * PB

    UNITS = {
        'kb' : KB,
        'k'  : KB,
        'mb' : MB,
        'm'  : MB,
        'gb' : GB,
        'g'  : GB,
        'tb' : TB,
        't'  : TB,
        'pb' : PB,
        'p'  : PB,
        'eb' : EB,
        'e'  : EB,
        'b'  : 1
    }

    def to_python(self, value, session_key=None):
        Field.to_python(self, value, session_key=None)

        # Parse the size
        m = DataSizeField.DATA_SIZE_RE.match(value)

        # Make sure the duration could be parsed
        if m is None:
            raise FieldValidationException("The value of '%s' for the '%s' parameter is not a valid size of data" % (str(value), self.name))

        # Get the units and duration
        d = m.groupdict()

        units = d['units'].lower()

        # Parse the value provided
        try:
            size = int(d['size'])
        except ValueError:
            raise FieldValidationException("The size '%s' for the '%s' parameter is not a valid number" % (d['duration'], self.name))

        # Make sure the units are valid
        if len(units) > 0 and units not in DataSizeField.UNITS:
            raise FieldValidationException("The unit '%s' for the '%s' parameter is not a valid unit of duration" % (units, self.name))

        # Convert the units to seconds
        if len(units) > 0:
            return size * DataSizeField.UNITS[units]
        else:
            return size

    def to_string(self, value):
        return str(value)

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
            FilePathField("file_path", "File or directory path",
                          "The path of the to get information on", empty_allowed=False),
            BooleanField("recurse", "Recursively iterate sub-directories",
                         "Indicates whether sub-directories ought to be recursed",
                         empty_allowed=False),
            BooleanField("only_if_changed", "Changed items only",
                         "Only include items when one of the time fields is changed",
                         empty_allowed=False),
            DurationField("interval", "Interval",
                          "The interval defining how often to import the feed; can include time units (e.g. 15m for 15 minutes, 8h for 8 hours)",
                          empty_allowed=False),
            BooleanField("include_file_hash", "Compute file hash",
                         "Compute a hash on the file (SHA224)", empty_allowed=False),
            DataSizeField("file_hash_limit", "File-size hash limit",
                          "Only include items when one of the time fields is changed",
                          empty_allowed=False),
            IntegerField("depth_limit", "Depth Limit",
                         "A limit on how many directories deep to get results for",
                         none_allowed=True, empty_allowed=True),
            WildcardField("file_filter", "File Name Filter",
                         "A wildcard for which files will be included",
                         none_allowed=True, empty_allowed=True)
            ]

        ModularInput.__init__(self, scheme_args, args, logger_name='file_meta_data_modular_input')

    @classmethod
    def boolean_to_int(cls, boolean):
        """
        Convert a boolean to an integer.
        """

        if boolean:
            return 1
        else:
            return 0

    @classmethod
    def get_files_data(cls, file_path, logger=None, latest_time=None, must_be_later_than=None,
                       file_hash_limit=0, depth_limit=0, file_filter=None):
        """
        Get the data for the files within the directory.
        """

        results = []

        total_file_count = 0
        total_dir_count = 0

        if latest_time is not None:
            latest_time_derived = latest_time
        else:
            latest_time_derived = 0

        this_latest_time = None

        # Make sure the file path is encoded properly
        file_path = file_path.encode("utf-8")

        try:

            # Get the information
            for root, dirs, files in os.walk(file_path, topdown=True):

                file_path_depth = os.path.normpath(file_path).count(os.sep)
                current_depth = os.path.normpath(root).count(os.sep)
                current_depth_relative = current_depth - file_path_depth

                # Stop if we hit the depth limit
                if depth_limit is None or depth_limit <= 0 or current_depth_relative < depth_limit:

                    for name in files:

                        # Continue only if the files matches the filter (if one is defined)
                        if file_filter is None or file_filter.match(os.path.join(root, name)):

                            info, this_latest_time = cls.get_file_data(os.path.join(root, name),
                                                                    logger, latest_time_derived,
                                                                    must_be_later_than,
                                                                    file_hash_limit)

                            if info is not None:
                                results.append(info)

                            if this_latest_time is not None:
                                latest_time_derived = this_latest_time

                    # Sum up the file count
                    total_file_count += len(files)

                    for name in dirs:
                        info, this_latest_time = cls.get_file_data(os.path.join(root, name),
                                                                   logger, latest_time_derived,
                                                                   must_be_later_than,
                                                                   file_hash_limit)

                        if info is not None:
                            results.append(info)

                        if this_latest_time is not None:
                            latest_time_derived = this_latest_time

                    # Sum up the directory count
                    total_dir_count += len(dirs)

            # Handle the root directory too
            root_result, latest_time_derived = cls.get_file_data(file_path, logger,
                                                                 latest_time_derived,
                                                                 must_be_later_than,
                                                                 file_hash_limit)

            if root_result is not None:
                root_result['file_count_recursive'] = total_file_count
                root_result['directory_count_recursive'] = total_dir_count
                results.append(root_result)

            # Return the results and the latest time
            return results, latest_time_derived

        except Exception as exception:
            # General exception when attempting to proess this path
            if logger:
                logger.exception('Error when processing path="%s", reason="%s"', file_path,
                                 str(exception))

            return None, latest_time_derived

    @classmethod
    def get_file_hash(cls, file_path, logger=None):
        """
        Get the hash for the given file.
        """

        try:

            sha224 = hashlib.sha224()

            with open(file_path, 'rb') as file:
                sha224.update(file.read())

            return sha224.hexdigest()
        except:
            if logger:
                logger.exception("Unable to compute the file hash, path=%r", file_path)

            return None

    @classmethod
    def remove_substrs(cls, original_string, substrs):
        """
        Remove the given sub-string from the string.
        """

        for sub in substrs:
            original_string = original_string.replace(sub, "")

        return original_string

    @classmethod
    def get_nix_acl_data(cls, file_path, stat_info=None):
        """
        Get the Unix ACL data for the given path.
        """

        # Stop if this isn't Unix
        if not nix_import_available:
            return

        output = collections.OrderedDict()

        if stat_info is None:
            stat_info = os.stat(file_path)

        # Get the owner
        output['owner_uid'] = pwd.getpwuid(stat_info.st_uid)[0]
        output['owner'] = pwd.getpwuid(stat_info.st_uid)[0]

        # Get the group
        output['group_uid'] = stat_info.st_gid
        # This is disabled because grp isn't available on Splunk's python
        # output['group'] = grp.getgrgid(stat_info.st_gid)[0]

        # Get the permissions
        output['permission_mask'] = oct(stat_info.st_mode & 0777)

        return output

    @classmethod
    def get_windows_acl_data(cls, file_path, add_as_mv=True):
        """
        Get the Windows ACL data for the given path.
        """

        # Stop if we cannot import the Windows libraries for dumping ACLs. This is likely this host
        # isn't running Windows.
        if not win_imports_available:
            return None

        output = collections.OrderedDict()

        # Get the owner
        sd = win32security.GetFileSecurity(file_path, win32security.OWNER_SECURITY_INFORMATION)
        sid = sd.GetSecurityDescriptorOwner()
        sid_resolved = win32security.LookupAccountSid(None, sid)

        output['owner'] = sid_resolved[0] + '\\' + sid_resolved[1]
        output['owner_sid'] = str(sid).replace('PySID:', '')

        # Get the group
        security_desc = win32security.GetFileSecurity(file_path,
                                                      win32security.GROUP_SECURITY_INFORMATION)
        sid = security_desc.GetSecurityDescriptorGroup()
        sid_resolved = win32security.LookupAccountSid(None, sid)

        output['group'] = sid_resolved[0] + '\\' + sid_resolved[1]
        output['group_sid'] = str(sid).replace('PySID:', '')

        # Get the ACEs
        security_desc = win32security.GetFileSecurity(file_path,
                                                      win32security.DACL_SECURITY_INFORMATION)
        dacl = security_desc.GetSecurityDescriptorDacl()

        if dacl is not None:

            for ace_no in range(0, dacl.GetAceCount()):
                ace = dacl.GetAce(ace_no)

                entry = []
                ace_type = []
                substr_removals = ["_ACE_TYPE", "_ACE", "_ACE_FLAG"]

                for i in ("ACCESS_ALLOWED_ACE_TYPE", "ACCESS_DENIED_ACE_TYPE",
                          "SYSTEM_AUDIT_ACE_TYPE", "SYSTEM_ALARM_ACE_TYPE"):
                    if getattr(ntsecuritycon, i) == ace[0][0]:
                        entry.append(cls.remove_substrs(i, substr_removals))
                        ace_type.append(cls.remove_substrs(i, substr_removals))

                for i in ("OBJECT_INHERIT_ACE", "CONTAINER_INHERIT_ACE",
                          "NO_PROPAGATE_INHERIT_ACE", "INHERIT_ONLY_ACE",
                          "SUCCESSFUL_ACCESS_ACE_FLAG", "FAILED_ACCESS_ACE_FLAG"):
                    if getattr(ntsecuritycon, i) & ace[0][1] == getattr(ntsecuritycon, i):
                        entry.append(cls.remove_substrs(i, substr_removals))

                # Files and directories do permissions differently
                permissions_file = ("DELETE", "READ_CONTROL", "WRITE_DAC", "WRITE_OWNER",
                                    "SYNCHRONIZE", "FILE_GENERIC_READ", "FILE_GENERIC_WRITE",
                                    "FILE_GENERIC_EXECUTE", "FILE_DELETE_CHILD")

                permissions_dir = ("DELETE", "READ_CONTROL", "WRITE_DAC", "WRITE_OWNER",
                                   "SYNCHRONIZE", "FILE_ADD_SUBDIRECTORY", "FILE_ADD_FILE",
                                   "FILE_DELETE_CHILD", "FILE_LIST_DIRECTORY", "FILE_TRAVERSE",
                                   "FILE_READ_ATTRIBUTES", "FILE_WRITE_ATTRIBUTES", "FILE_READ_EA",
                                   "FILE_WRITE_EA")

                permissions_dir_inherit = ("DELETE", "READ_CONTROL", "WRITE_DAC", "WRITE_OWNER",
                                           "SYNCHRONIZE", "GENERIC_READ", "GENERIC_WRITE",
                                           "GENERIC_EXECUTE", "GENERIC_ALL")

                if os.path.isfile(file_path):
                    permissions = permissions_file
                else:
                    permissions = permissions_dir

                    # Directories also contain an ACE that is inherited by children (files)
                    # within them
                    if ace[0][1] & ntsecuritycon.OBJECT_INHERIT_ACE == ntsecuritycon.OBJECT_INHERIT_ACE and ace[0][1] & ntsecuritycon.INHERIT_ONLY_ACE == ntsecuritycon.INHERIT_ONLY_ACE:
                        permissions = permissions_dir_inherit

                ace_permissions = []

                for i in permissions:
                    if getattr(ntsecuritycon, i) & ace[1] == getattr(ntsecuritycon, i):
                        entry.append(cls.remove_substrs(i, substr_removals))
                        ace_permissions.append(cls.remove_substrs(i, substr_removals))

                sid = win32security.LookupAccountSid(None, ace[2])

                if add_as_mv:
                    output['ace_' + str(ace_no) + "_type"] = ace_type
                    output['ace_' + str(ace_no) + "_permissions"] = ace_permissions
                else:
                    output['ace_' + str(ace_no) + "_type"] = " ".join(ace_type)
                    output['ace_' + str(ace_no) + "_permissions"] = " ".join(ace_permissions)

                output['ace_' + str(ace_no) + "_sid"] = str(ace[2]).replace('PySID:', '')
                output['ace_' + str(ace_no) + "_account"] = sid[0] + '\\' + sid[1]

        return output

    @classmethod
    def get_file_data(cls, file_path, logger=None, latest_time=None, must_be_later_than=None,
                      file_hash_limit=0):
        """
        Get the data for this specific file.
        """

        try:
            result = collections.OrderedDict()

            # Determine if the file is a directory
            is_directory = os.path.isdir(file_path)
            result['is_directory'] = cls.boolean_to_int(is_directory)

            if is_directory:
                try:
                    path, dirs, files = os.walk(file_path).next()

                    result['file_count'] = len(files)
                    result['directory_count'] = len(dirs)

                except StopIteration:
                    # Unable to access this directory
                    logger.info('Unable to get the list of files for directory="%s"', file_path)

            # Get the absolute path
            result['path'] = os.path.abspath(file_path)

            # Get the meta-data
            stat_info = os.stat(file_path)

            # Get the file hash
            if not is_directory and file_hash_limit > 0 and stat_info.st_size <= file_hash_limit:

                # Try to get the hash
                file_hash = cls.get_file_hash(file_path, logger)

                # Insert the result if we got one
                if file_hash is not None:
                    result["sha224"] = file_hash

            # By default, assume the item is not later than the latest_time parameter unless we
            # prove otherwise
            is_item_later_than_latest_date = False

            for attribute in dir(stat_info):
                if attribute.startswith("st_"):

                    if 'time' in attribute:
                        result[attribute[3:]] = time.ctime(getattr(stat_info, attribute))

                        # Save the latest value of the time field
                        if latest_time is not None and getattr(stat_info, attribute) > latest_time:
                            latest_time = getattr(stat_info, attribute)

                        # Determine if any of the modification or creation times are later than
                        # the filter
                        if attribute != "st_atime" and getattr(stat_info, attribute) > must_be_later_than:
                            if logger:
                                logger.info("Time is later than filter, %s=%r, must_be_later_than=%r, path=%r", attribute, getattr(stat_info, attribute), must_be_later_than, file_path)
                            is_item_later_than_latest_date = True

                        # Include the time in raw format
                        result[attribute[3:] + "_epoch"] = getattr(stat_info, attribute)
                    else:
                        result[attribute[3:]] = getattr(stat_info, attribute)

            # Get the Windows ACL info (if we can)
            windows_acl_info = None

            try:
                cls.get_windows_acl_data(file_path)
            except Exception as exception:
                logger.warn("Unable to get the ACL data, reason=%s", str(exception))

            if windows_acl_info is not None:
                result.update(windows_acl_info)

            # Get the Unix ACL info (if we can)
            nix_acl_info = None

            try:
                cls.get_nix_acl_data(file_path, stat_info=stat_info)
            except Exception as exception:
                logger.warn("Unable to get the ACL data, reason=%s", str(exception))

            if nix_acl_info is not None:
                result.update(nix_acl_info)

            # Return both the result and the latest time if items passed the filer
            if is_item_later_than_latest_date:
                return result, latest_time

            # Return no result
            else: # if latest_time is not None and not is_item_later_than_latest_date:
                return None, latest_time

        except OSError as exception:
            # File not found or inaccessible
            if logger:
                logger.warn('Unable to access path="%s", reason="%s"', file_path, str(exception))

            return None, latest_time

        except Exception as exception:
            # General exception when attempting to proess this path
            if logger:
                logger.exception('Error when processing path="%s", reason="%s"',
                                 file_path, str(exception))

            return None, latest_time

    def save_checkpoint(self, checkpoint_dir, stanza, last_run, latest_file_system_date):
        """
        Save the checkpoint state.

        Arguments:
        checkpoint_dir -- The directory where checkpoints ought to be saved
        stanza -- The stanza of the input being used
        last_run -- The time when the analysis was last performed
        latest_file_system_date -- The latest date observed on the file-system
        """

        self.save_checkpoint_data(checkpoint_dir,
                                  stanza,
                                  {
                                      'last_run' : last_run,
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
        """
        Run the input.
        """

        # Make the parameters
        interval = cleaned_params["interval"]
        file_path = cleaned_params["file_path"]
        recurse = cleaned_params.get("recurse", True)
        only_if_changed = cleaned_params.get("only_if_changed", False)
        file_hash_limit = cleaned_params.get("file_hash_limit", 500 * DataSizeField.MB)
        include_file_hash = cleaned_params.get("include_file_hash", False)
        depth_limit = cleaned_params.get("depth_limit", 0)
        file_filter = cleaned_params.get("file_filter", None)
        sourcetype = cleaned_params.get("sourcetype", "file_meta_data")
        host = cleaned_params.get("host", None)
        index = cleaned_params.get("index", "default")
        source = stanza

        if self.needs_another_run(input_config.checkpoint_dir, stanza, interval):

            self.logger.debug('Running input against path="%s"', file_path)

            # Get the date of the latest entry imported
            try:
                checkpoint_data = self.get_checkpoint_data(input_config.checkpoint_dir, stanza,
                                                           throw_errors=True)
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

            # If we are not to include the file hash, then set the size limit to zero (which
            # disables it)
            if not include_file_hash:
                file_hash_limit = -1

            # Make sure the file path is encoded properly
            file_path = file_path.encode("utf-8")

            # Get the file information
            if recurse:
                results, new_latest_time = self.get_files_data(file_path, logger=self.logger,
                                                               latest_time=latest_time,
                                                               must_be_later_than=must_be_later_than,
                                                               file_hash_limit=file_hash_limit,
                                                               depth_limit=depth_limit,
                                                               file_filter=file_filter)
            else:
                result, new_latest_time = self.get_file_data(file_path, logger=self.logger,
                                                             latest_time=latest_time,
                                                             must_be_later_than=must_be_later_than,
                                                             file_hash_limit=file_hash_limit,
                                                             file_filter=file_filter)

                # Make the results array from the single result
                results = [result]

            # Log the result
            if results is None:
                self.logger.info("Completed retrieval of file data, no files found, count=%i, path=%s",
                                 0, file_path)
            else:
                self.logger.info("Completed retrieval of file data, count=%i, path=%s",
                                 len(results), file_path)

                # Output the event
                for result in results:

                    if result is not None:

                        # Add the time
                        result['time'] = time.strftime("%a %b %d %H:%M:%S %Y")

                        self.output_event(result, stanza, index=index, source=source,
                                          sourcetype=sourcetype, host=host, unbroken=True,
                                          close=True)

            # Get the time that the input last ran
            if checkpoint_data is not None and 'last_ran' in checkpoint_data:
                last_ran = checkpoint_data['last_ran']
            else:
                last_ran = None

            # Identify the correct latest time
            if new_latest_time > latest_time:
                latest_time = new_latest_time

            self.save_checkpoint(input_config.checkpoint_dir, stanza,
                                 self.get_non_deviated_last_run(last_ran, interval, stanza),
                                 latest_time)

if __name__ == '__main__':

    FILE_INPUT = None

    try:
        FILE_INPUT = FileMetaDataModularInput()
        FILE_INPUT.execute()
        sys.exit(0)
    except Exception as exception:

        # This logs general exceptions that would have been unhandled otherwise (such as coding
        # errors)
        if FILE_INPUT is not None:
            FILE_INPUT.logger.exception("Unhandled exception was caught, this may be due to a defect in the script")

        raise exception

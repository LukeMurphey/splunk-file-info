

import logging
import sys
import os
import re
import json
import base64
import tempfile

from splunk.clilib.bundle_paths import make_splunkhome_path
from splunk import ResourceNotFound
import splunk.entity as entity
from splunk.rest import simpleRequest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from file_info_app import rest_handler

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "file_info_app"))
sys.path.append(os.path.join("bin", "file_info_app"))

if 'SPLUNK_HOME' in os.environ:
    sys.path.append(os.path.join(os.environ['SPLUNK_HOME'], "etc", "apps", "file_meta_data", "bin", "file_info_app"))

sys.path.append(make_splunkhome_path(['etc', 'apps', "file_meta_data", "bin", "file_info_app", "file_processors"]))
print(sys.path)
from file_info_app.file_processors import get_info

def setup_logger(level):
    """
    Setup a logger for the REST handler
    """

    logger = logging.getLogger('splunk.appserver.file_analysis_rest_handler.rest_handler')
    logger.propagate = False # Prevent the log messages from being duplicated in the python.log file
    logger.setLevel(level)

    log_file_path = make_splunkhome_path(['var', 'log', 'splunk', 'file_analysis_rest_handler.log'])
    file_handler = logging.handlers.RotatingFileHandler(log_file_path, maxBytes=25000000,
                                                        backupCount=5)

    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

logger = setup_logger(logging.DEBUG)
logger.warning(sys.path)
logger.warning(os.getcwd())

class FileAnalysisRestHandler(rest_handler.RESTHandler):

    DEFAULT_NAMESPACE ="file_meta_data"
    DEFAULT_OWNER = "nobody"

    def __init__(self, command_line, command_arg):
        super(FileAnalysisRestHandler, self).__init__(command_line, command_arg, logger)

    def is_file_name_valid(self, lookup_file):     
        """
        Indicate if the lookup file is valid (doesn't contain invalid characters such as "..").
        """
         
        allowed_path = re.compile("^[-A-Z0-9_ ]+([.][-A-Z0-9_ ]+)*$", re.IGNORECASE)
        
        if not allowed_path.match(lookup_file):
            return False
        else:
            return True

    def get_file(self, request_info, **kwargs):
        return self.render_json({
                                    'hellow' : 'here!',
                                    })
    def post_file(self, request_info, file_name=None, file_contents=None, **kwargs):
        # Stop if the file was not provided
        if file_contents is None or len(file_contents.strip()) == 0:
            return self.render_error_json('The file was not provided')

        # Remove the mime-type prefix
        try:
            file_contents = file_contents.split(',')[1]
        except IndexError:
            return self.render_error_json('Unable to parse the file contents.')

        # Save the file to disk
        td = tempfile.TemporaryDirectory()
        full_file_path = os.path.join(td.name, file_name)
        
        logger.info("Created temp file for analyzing file_name=%s, temp_file=%s", file_name, full_file_path)

        f = open(full_file_path, "w+b")
        f.write(base64.b64decode(file_contents))
        f.close()

        # Do the analysis
        try:
            data = get_info(full_file_path, True, True)
 
            # Return a response
            return self.render_json(data)

        except:
            return self.render_error_json("Unable to process the file")



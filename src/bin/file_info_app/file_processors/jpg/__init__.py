

import os
import sys
# Append the libraries so they can be imported
sys.path.append(os.path.join("bin", "file_info_app"))

if 'SPLUNK_HOME' in os.environ:
    sys.path.append(os.path.join(os.environ['SPLUNK_HOME'], "etc", "apps", "file_meta_data", "bin", "file_info_app"))

import exifread
from file_info_app.file_processors.field_names import *

def get_jpg_info(file_path, return_strings, return_data):

    data = {}

    with open(file_path, 'rb') as f:
        # Get the data
        if return_data:
            tags = exifread.process_file(f)
            for tag in tags.keys():
                value = str(tags[tag])

                if len(value) < 200:
                    addToDataIfNotNone(data, normalizeFieldName(tag), value)

    return data

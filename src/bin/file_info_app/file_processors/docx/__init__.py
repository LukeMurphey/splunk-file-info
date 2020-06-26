

import os
import sys
# Append the libraries so they can be imported
sys.path.append(os.path.join("bin", "file_info_app"))

if 'SPLUNK_HOME' in os.environ:
    sys.path.append(os.path.join(os.environ['SPLUNK_HOME'], "etc", "apps", "file_meta_data", "bin", "file_info_app"))

from docx import Document
from ..field_names import *

def get_docx_info(file_path, return_strings, return_data):

    data = {}

    with open(file_path, 'rb') as f:
        document = Document(file_path)

        # Get the data
        if return_data:
            pass

        # Get the strings
        if return_strings:
            for idx, para in enumerate(document.paragraphs):
                text = para.text
                addToDataIfNotNone(data, STRINGS_PARAGRAPH_NUMBER % idx, text)
   
    return data

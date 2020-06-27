

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
            addToDataIfNotNone(data, AUTHOR, document.core_properties.author)
            addToDataIfNotNone(data, CATEGORY, document.core_properties.category)
            addToDataIfNotNone(data, COMMENTS, document.core_properties.comments)
            addToDataIfNotNone(data, CONTENT_STATUS, document.core_properties.content_status)
            addToDataIfNotNone(data, IDENTIFIER, document.core_properties.identifier)
            addToDataIfNotNone(data, KEYWORDS, document.core_properties.keywords)
            addToDataIfNotNone(data, LANGUAGE, document.core_properties.language)
            addToDataIfNotNone(data, MODIFIED_BY, document.core_properties.last_modified_by)
            addToDataIfNotNone(data, REVISION, document.core_properties.revision)
            addToDataIfNotNone(data, SUBJECT, document.core_properties.subject)
            addToDataIfNotNone(data, TITLE, document.core_properties.title)
            addToDataIfNotNone(data, VERSION, document.core_properties.version)

            # These are all dates
            addToDataIfNotNone(data, PRINTED, document.core_properties.last_printed)
            addToDataIfNotNone(data, MODIFIED, document.core_properties.modified)
            addToDataIfNotNone(data, CREATED, document.core_properties.created)

        # Get the strings
        if return_strings:
            for idx, para in enumerate(document.paragraphs):
                text = para.text
                addToDataIfNotNone(data, STRINGS_PARAGRAPH_NUMBER % idx, text)
   
    return data

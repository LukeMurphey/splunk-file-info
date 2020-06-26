

import os
import sys
# Append the libraries so they can be imported
sys.path.append(os.path.join("bin", "file_info_app"))

if 'SPLUNK_HOME' in os.environ:
    sys.path.append(os.path.join(os.environ['SPLUNK_HOME'], "etc", "apps", "file_meta_data", "bin", "file_info_app"))

from PyPDF2 import PdfFileReader
from file_info_app.file_processors.field_names import *

def get_pdf_info(file_path, return_strings, return_data):

    data = {}

    with open(file_path, 'rb') as f:
        pdf = PdfFileReader(f)

        # Get the data
        if return_data:
            info = pdf.getDocumentInfo()
            
            addToDataIfNotNone(data, PAGE_COUNT, info.author)
            addToDataIfNotNone(data, CREATOR, info.creator)
            addToDataIfNotNone(data, PRODUCER, info.producer)
            addToDataIfNotNone(data, SUBJECT, info.subject)
            addToDataIfNotNone(data, TITLE, info.title)
            addToDataIfNotNone(data, PAGE_COUNT, pdf.getNumPages())
            addToDataIfNotNone(data, ENCRYPTED, pdf.isEncrypted)

        # Get the strings
        if return_strings:
            for p in range(1, pdf.getNumPages()):
                page = pdf.getPage(p)
                text = page.extractText()

                if text is not None and len(text) > 0:
                    addToDataIfNotNone(data, STRINGS_PAGE_NUMBER % p, text)
   
    return data

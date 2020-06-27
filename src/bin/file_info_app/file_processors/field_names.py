import datetime
import re

PAGE_COUNT = 'page_count'
AUTHOR = 'author'
CREATOR = 'creator'
PRODUCER = 'producer'
SUBJECT = 'subject'
TITLE = 'title'
ENCRYPTED = 'encrypted'

CATEGORY = 'category'
COMMENTS = 'comments'
CONTENT_STATUS = 'content_state'
CREATED = 'created'
IDENTIFIER = 'identifier'
KEYWORDS = 'keywords'
LANGUAGE = 'language'
MODIFIED_BY = 'last_modified_by'
PRINTED = ' last_printed'
MODIFIED = 'modified'
REVISION = 'revision'
VERSION = 'version'

STRINGS_PAGE_NUMBER = 'strings_page_%i'
STRINGS_PARAGRAPH_NUMBER = 'strings_paragraph_%i'

def normalizeFieldName(field_name):
    new_field = field_name.lower()
    return re.sub('[^A-Za-z0-9]', '_', new_field)

def addToDataIfNotNone(data, field_name, field_value, normalize_field=False):
    if field_value is not None:
        # Normalize the field name if necessary
        if normalize_field:
            field_name = normalizeFieldName(field_name)

        if field_value is True:
            data[field_name] = "true"
        elif field_value is False:
            data[field_name] = "true"
        elif isinstance(field_value, datetime.datetime):
            data[field_name] = field_value.strftime("%m/%d/%Y, %H:%M:%S")
        elif isinstance(field_value, str):
            data[field_name] = field_value #.encode('utf-8', 'backslashreplace').decode('utf-8')
        else:
            data[field_name] = field_value

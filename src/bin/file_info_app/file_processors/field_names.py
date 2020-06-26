
PAGE_COUNT = 'page_count'
AUTHOR = 'author'
CREATOR = 'creator'
PRODUCER = 'producer'
SUBJECT = 'subject'
TITLE = 'title'
ENCRYPTED = 'encrypted'

STRINGS_PAGE_NUMBER = 'strings_page_%i'
TYPE_PAGE_NUMBER = 'type_page_%i'

def addToDataIfNotNone(data, field_name, field_value):
    if field_value is not None:
        if field_value is True:
            data[field_name] = "true"
        elif field_value is False:
            data[field_name] = "true"
        else:
            data[field_name] = field_value

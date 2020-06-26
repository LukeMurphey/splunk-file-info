
import mimetypes
from pdf import get_pdf_info
from docx import get_docx_info

processor_map = {
    'application/pdf' : get_pdf_info,
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': get_docx_info,
}

def get_info(file_path, extract_strings, extract_data, logger=None):
    try:
        # Determine the mime-type of the file
        guessed_type = mimetypes.guess_type(file_path, strict=True)

        # Get the processor to run
        processor = None
        if guessed_type is not None:
            processor = processor_map.get(guessed_type[0], None)

        if processor is not None:
            return processor(file_path, extract_strings, extract_data)
        elif logger is not None:
            logger.info('No processor found for file_path=%s', file_path)
    except:
        if logger is not None:
            logger.exception('Exception generated when attempting to get the file data for file_path=%s', file_path)
        else:
            raise

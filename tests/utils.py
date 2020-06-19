import pdfplumber

from config import Config
from app.utils.utils import getUUID
from app.files import (
    FileStorageObject,
    DocxFile,
)


def create_one_pargraph_docx(paragraph_content):
    docx_document = DocxFile(folder=Config.TESTS_TEMP_FOLDER)
    docx_document.add_paragraph(paragraph_content)
    docx_document.save()
    docx_storage_object = FileStorageObject(
        docx_document.path, docx_document.full_name, "application/msword")
    return docx_document, docx_storage_object


def save_response_pdf(response):
    # Save generated pdf document
    response_document_path = Config.TESTS_TEMP_FOLDER + "/" + getUUID()+".pdf"
    print(response_document_path)
    stream = response.get_data()
    f = open(response_document_path, 'wb')
    f.write(stream)
    f.close()
    return response_document_path


def extract_text_from_pdf(response_document_path):
    pdf = pdfplumber.open(response_document_path)
    page = pdf.pages[0]
    text = page.extract_text()
    text = repr(text).replace("'", "")
    pdf.close()
    return text


def process_response_document(response):
    response_document_path = save_response_pdf(response)
    response_document_content = extract_text_from_pdf(response_document_path)
    return response_document_path, response_document_content

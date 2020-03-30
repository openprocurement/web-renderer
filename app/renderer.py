from flask import Flask
import json
import os
import time
from docxtpl import DocxTemplate
from app import app, jinja_env
from app.utils.utils import (
    generate_file_name,
    make_path,
    convert_to_pdf,
    does_file_exists,
    is_file_empty,
)
from app.utils.template_utils import(
    format_date,
    convert_amount_to_words,
    to_float,
)
from app.constants import (
    GENERATED_DOC_EXTENSION,
    GENERATED_DOC_PREFIX,
    TEMPLATE_PREFIX,
    TEMPLATE_FILE_EXTENSION,
    TEST_PREFIX,
)
from app.handlers import format_exception
from app.exceptions import (
    InvalidDocumentFomat,
    DocumentRenderError,
    DocumentSavingError,
)


class RenderObject:

    def __init__(self, json=None, template_file=None):
        self.context = json
        self.template_file = template_file


class RenderDocxObject:

    def __init__(self, json=None, template_file=None):
        self.make_context(json)
        self.template_file = template_file
        self.form_docx_template()
        self.init_template_functions()

    def make_context(self, json):
        self.context = json

    def init_template_functions(self):
        jinja_env.filters['format_date'] = format_date
        jinja_env.filters['convert_amount_to_words'] = convert_amount_to_words
        jinja_env.filters['to_float'] = to_float

    def form_docx_template(self):
        docx_template_path = self.template_file.full_file_path
        self.docx_template = DocxTemplate(docx_template_path)
        is_file_empty(self.docx_template)

    def make_generated_doc_path(self):
        self.generated_doc_path = self.template_file.full_file_path.replace(
            TEMPLATE_PREFIX, GENERATED_DOC_PREFIX)

    def render_document_to_docx(self):
        self.make_generated_doc_path()
        self.docx_template.render(self.context, jinja_env)
        self.docx_template.save(self.generated_doc_path)
        if does_file_exists(self.generated_doc_path):
            app.logger.info('Template is rendered to docx.')
        else:
            raise DocumentRenderError()

    def convert_document_to_pdf(self):
        convert_to_pdf(self.generated_doc_path)
        self.generated_pdf_path = self.generated_doc_path.replace(
            TEMPLATE_FILE_EXTENSION, GENERATED_DOC_EXTENSION)
        if does_file_exists(self.generated_doc_path):
            app.logger.info('Template is rendered to pdf')
        else:
            raise DocumentRenderError()

    def render(self):
        self.render_document_to_docx()
        self.convert_document_to_pdf()


class File:

    def __init__(self, file_storage_object, file_name=TEST_PREFIX):
        self.file_storage_object = file_storage_object
        self.file_name = file_name
        self.form_file_extension()
        self.form_full_path()

    def save_file(self):
        self.file_storage_object.save(self.full_file_path)
        if does_file_exists(self.full_file_path):
            app.logger.info('Template is saved.')
        else:
            raise DocumentSavingError()

    def form_file_extension(self):
        if "." in self.file_storage_object.filename:
            self.file_extension = self.file_storage_object.filename.split('.')[
                1]
        else:
            raise InvalidDocumentFomat()

    def create_file_name(self, template_type=TEST_PREFIX):
        self.file_name = generate_file_name(template_type)

    def form_full_path(self):
        file_full_name = self.file_name + "." + self.file_extension
        self.full_file_path = make_path(file_full_name)

    def convert_file_to_pdf(self, timeout=None):
        convert_to_pdf(self.full_file_path)


class TemplateFile(File):

    def __init__(self, file_storage_object, file_name=TEST_PREFIX):
        self.file_storage_object = file_storage_object
        self.create_file_name()
        super().form_file_extension()
        super().form_full_path()
        self.save_file()

    def create_file_name(self, template_type=TEMPLATE_PREFIX):
        self.file_name = generate_file_name(template_type)

    def save_file(self):
        if self.file_extension == TEMPLATE_FILE_EXTENSION:
            return super().save_file()
        else:
            raise InvalidDocumentFomat()

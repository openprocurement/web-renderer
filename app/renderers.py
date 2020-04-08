from flask import Flask
import json
import os
import time
import re
from copy import deepcopy
from app import app
from app.render_environment.template_environment import (
    DocxTemplateLocal as DocxTemplate,
)
from app.utils.utils import (
    Path,
    FileUtils,
    Regex,
    file_decorator,
)
from app.utils.converters import(
    GeneralConverter,
)
from app.constants import (
    GeneralConstants,
)
from app.handlers import format_exception
from app.exceptions import (
    InvalidDocumentFomat,
    DocumentRenderError,
    DocumentSavingError,
    HTMLNotFoundError,
)
from app.constants import (
    RegexConstants,
    HTMLConstants,
)

# File objects


class File:

    def __init__(self, file_storage_object, file_name=GeneralConstants.TEST_PREFIX):
        self.file_storage_object = file_storage_object
        self.file_name = file_name
        self.form_file_extension()
        self.form_full_path()

    def save_file(self):
        self.file_storage_object.save(self.full_file_path)
        if FileUtils.does_file_exists(self.full_file_path):
            app.logger.info('Template is saved.')
        else:
            raise DocumentSavingError()

    def form_file_extension(self):
        if "." in self.file_storage_object.filename:
            self.file_extension = self.file_storage_object.filename.split('.')[
                1]
        else:
            raise InvalidDocumentFomat()

    def create_file_name(self, template_type=GeneralConstants.TEST_PREFIX):
        self.file_name = Path.generate_file_name(template_type)

    def form_full_path(self):
        file_full_name = self.file_name + "." + self.file_extension
        self.full_file_path = Path.make_path(file_full_name)

    def convert_file_to_pdf(self, timeout=None):
        GeneralConverter.convert_to_pdf(self.full_file_path)


class TemplateFile(File):

    def __init__(self, file_storage_object, file_name=GeneralConstants.TEST_PREFIX):
        self.file_storage_object = file_storage_object
        self.create_file_name()
        super().form_file_extension()
        super().form_full_path()
        self.save_file()

    def create_file_name(self, template_type=GeneralConstants.TEMPLATE_PREFIX):
        self.file_name = Path.generate_file_name(template_type)

    def save_file(self):
        if self.file_extension == GeneralConstants.TEMPLATE_FILE_EXTENSION:
            return super().save_file()
        else:
            raise InvalidDocumentFomat()


# Renderers

class RenderObject:

    def __init__(self, template_file=None):
        self.template_file = template_file


class DocxToPDFRenderer(RenderObject):

    def __init__(self, json=None, template_file=None):
        self.make_context(json)
        self.template_file = TemplateFile(template_file)
        self.form_docx_template()
        self.render()

    def make_context(self, json):
        self.context = json

    def form_docx_template(self):
        docx_template_path = self.template_file.full_file_path
        self.docx_template = DocxTemplate(docx_template_path)
        FileUtils.is_file_empty(self.docx_template)

    def make_generated_doc_path(self):
        self.generated_doc_path = self.template_file.full_file_path.replace(
            GeneralConstants.TEMPLATE_PREFIX, GeneralConstants.GENERATED_DOC_PREFIX)

    def render_document_to_docx(self):
        self.make_generated_doc_path()
        self.docx_template.render_document(self.context)
        self.docx_template.save(self.generated_doc_path)
        if FileUtils.does_file_exists(self.generated_doc_path):
            app.logger.info('Template is rendered to docx.')
        else:
            raise DocumentRenderError()

    def convert_document_to_pdf(self):
        GeneralConverter.convert_to_pdf(self.generated_doc_path)
        self.generated_pdf_path = self.generated_doc_path.replace(
            GeneralConstants.TEMPLATE_FILE_EXTENSION, GeneralConstants.GENERATED_DOC_EXTENSION)
        if FileUtils.does_file_exists(self.generated_doc_path):
            app.logger.info('Template is rendered to pdf')
        else:
            raise DocumentRenderError()

    def render(self):
        self.render_document_to_docx()
        self.convert_document_to_pdf()


class DocxToHTMLRenderer(RenderObject):

    REGEX_TO_REPLACE = [
        # change dict access from dict['field'] to dict.field
        [RegexConstants.ARRAY_FIELDS, RegexConstants.FIRST],
        [RegexConstants.A_LINKS, ""],  # replace all <a> links
        [RegexConstants.TEMPLATE_FORMULA,  # change {{ field }} to TextField
         RegexConstants.TEXT_FIELD],
        [RegexConstants.ALL_TRS, ""],  # replace tr's
        [RegexConstants.ALL_FOR_LOOP_BODY, ""],  # replace all for loops
        # replace all filters: {{ field | filter }}
        [RegexConstants.TEMPLATE_FILTER, ""],
    ]
    HTML_HEADERS = [
        HTMLConstants.IMPORT_FORM_FIELD_MACROS,
        HTMLConstants.BLOCK_TEMPLATE_CONTENT,
    ]
    HTML_FOOTERS = [
        HTMLConstants.END_BLOCK_TEMPLATE_CONTENT,
    ]

    def __init__(self, template_file):
        self.make_template_file(template_file)
        self.render_to_html()

    def make_template_file(self, template_file):
        template_file = Path.make_full_file_path(template_file)
        with file_decorator(template_file, "rb", HTMLNotFoundError):
            self.template_file = open(template_file, "rb")
            self.convert_to_html()
            app.logger.info('Template is rendered to html.')

    def replace_regex(self):
        self.formatted_html = Regex.replace_regex_list(
            self.formatted_html, DocxToHTMLRenderer.REGEX_TO_REPLACE)
        app.logger.info('Template is reformatted.')

    def add_header(self):
        html_headers = ' '.join(DocxToHTMLRenderer.HTML_HEADERS)
        html_footers = ' '.join(DocxToHTMLRenderer.HTML_FOOTERS)
        self.formatted_html = html_headers + self.formatted_html + html_footers

    def convert_to_html(self):
        document = GeneralConverter.convert_to_html(self.template_file)
        self.init_html = document.value
        self.formatted_html = self.init_html

    def encode_html(self):
        self.unicode_html = self.formatted_html.encode('utf8')
        app.logger.info('Template is encoded.')

    def make_file_path(self):
        self.html_file_name = Path.generate_file_name()
        self.html_file_full_path = Path.make_full_html_path(
            self.html_file_name)

    def save_html(self):
        with file_decorator(self.html_file_full_path, "wb", HTMLNotFoundError):
            template_file = open(self.html_file_full_path, "wb")
            template_file.write(self.unicode_html)
        app.logger.info('Template is saved.')

    def render_to_html(self):
        self.replace_regex()
        self.add_header()
        self.encode_html()
        self.make_file_path()
        self.save_html()

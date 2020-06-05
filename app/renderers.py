import json
import os
import time
import re
from copy import deepcopy

from flask import Flask
from app import app
from app.render_env.templates import (
    DocxTemplateLocal as DocxTemplate,
)
from app.utils.utils import (
    FileManager,
    Regex,
)
from app.converters.general_converters import(
    DocxToHTMLConverter,
    DocxToPdfConverter,
)
from app.converters.converter_to_tag_schema import(
    HTMLToJSONTagSchemeConverter,
)
from app.converters.converter_to_json_schema import(
    HTMLToJSONSchemaConverter,
)
from app.constants import (
    GeneralConstants,
    RegexConstants,
    HTMLConstants,
)
from app.files import (
    TemplateFile,
    HTMLFile,
)
from app.handlers import format_exception
from app.exceptions import (
    InvalidDocumentFomat,
    DocumentRenderError,
    DocumentSavingError,
    HTMLNotFoundError,
)
from app.attachers import(
    PdfAttacher,
)

# Renderers

class ObjectRenderer:

    def __init__(self, template_file=None):
        self.template_file = template_file


class DocxToPDFRenderer(ObjectRenderer):

    def __init__(self, json=None, template_file=None, include_attachments=None, template_type=None):
        self.json = json
        self.template_file = TemplateFile(template_file, template_type=template_type)
        self.include_attachments = include_attachments
        self.docx_template = DocxTemplate(self.template_file)
        self.render()


    def render_to_docx(self):
        self.docx_template.render(self.json.data)
        self.docx_template.save()
        if FileManager.does_file_exists(self.docx_template.full_path):
            app.logger.info('Template is rendered to docx.')
        else:
            raise DocumentRenderError()

    def render_to_pdf(self):
        self.docx_converter = DocxToPdfConverter(self.docx_template)
        self.generated_pdf = self.docx_converter.pdf_document
        if FileManager.does_file_exists(self.docx_converter.pdf_document.full_path):
            app.logger.info('Template is rendered to pdf')
        else:
            raise DocumentRenderError()

    def add_attachments_to_pdfa(self):
        if self.include_attachments:
            self.pdf_attacher = PdfAttacher(self.docx_converter.pdf_document.full_name)
            # adding attachments
            self.pdf_attacher.add_attachment(self.json.full_name)
            self.pdf_attacher.add_attachment(self.docx_template.full_name)
            # writing output
            self.pdf_attacher.write_output()
            self.generated_pdf = self.pdf_attacher.output_file
            app.logger.info('Attachments are added.')

    def render(self):
        self.render_to_docx()
        self.render_to_pdf()
        self.add_attachments_to_pdfa()


class BaseHTMLRenderer(ObjectRenderer):

    REGEX_TO_REPLACE = []

    def __init__(self, template_file_name):
        self.template_file = TemplateFile.get_obj_by_name(template_file_name)
        self.render()

    def convert_to_html(self):
        self.html_converter = DocxToHTMLConverter(
            self.template_file.storage_object)
        self.init_html = self.html_converter.html.value
        self.formatted_html = self.html_converter.replace_regexes(
            self.__class__.REGEX_TO_REPLACE)
        app.logger.info('Template is rendered to html.')

    def convert(self):
        pass

    def render(self):
        self.convert_to_html()
        self.convert()


class DocxToHTMLRenderer(BaseHTMLRenderer):

    REGEX_TO_REPLACE = [
        # change dict access from dict['field'] to dict.field
        [RegexConstants.ARRAY_FIELDS, RegexConstants.FIRST],
        [RegexConstants.A_LINKS, ""],  # replace all <a> links
        [RegexConstants.TEMPLATE_FORMULA,  # change {{ field }} to TextField
         RegexConstants.TEXT_FIELD],
        [RegexConstants.ALL_TRS, ""],  # replace tr's
        [RegexConstants.FOR_LOOP_BODY, ""],  # replace all for loops
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

    def __init__(self, template_file_name):
        super().__init__(template_file_name)

    def reformat_html(self):
        html_headers = ' '.join(self.__class__.HTML_HEADERS)
        html_footers = ' '.join(self.__class__.HTML_FOOTERS)
        self.formatted_html = html_headers + self.formatted_html + html_footers

    def encode_html(self):
        self.unicode_html = self.formatted_html.encode()
        app.logger.info('Template is encoded.')

    def save_html(self):
        self.html_file = HTMLFile('wb', content=self.unicode_html)
        self.html_file.write()
        app.logger.info('Template is saved.')

    def convert(self):
        self.reformat_html()
        self.encode_html()
        self.save_html()


class DocxToTagSchemaRenderer(BaseHTMLRenderer):

    REGEX_TO_REPLACE = [
        [RegexConstants.ARRAY_FIELDS, RegexConstants.FIRST],
        [RegexConstants.A_LINKS, ""],
    ]

    def __init__(self, template_file_name):
        super().__init__(template_file_name)

    def convert(self):
        self.json_schema = HTMLToJSONTagSchemeConverter().convert(self.formatted_html)
        app.logger.info('Template is reformatted to json.')


class DocxToJSONSchemaRenderer(BaseHTMLRenderer):

    REGEX_TO_REPLACE = [
        [RegexConstants.ARRAY_FIELDS, RegexConstants.FIRST],
        [RegexConstants.A_LINKS, ""],
        [RegexConstants.TEMPLATE_FILTER, ""],
    ]

    def __init__(self, template_file_name, hide_empty_fields):
        self.hide_empty_fields = hide_empty_fields
        super().__init__(template_file_name)

    def convert(self):
        self.json_schema = HTMLToJSONSchemaConverter(
            self.hide_empty_fields).convert(self.formatted_html)
        app.logger.info('Template is reformatted to json.')

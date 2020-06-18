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
    does_file_exists,
    replace_regex_list,
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
    JSONFile,
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
from app.decorators import(
    form_data,
)
# Renderers

class ObjectRenderer:

    def __init__(self, template_file=None):
        self.template_file = template_file


@form_data
class DocxToPDFRenderer(ObjectRenderer):

    def __init__(self, json=None, template_file=None, include_attachments=None, document_names=None, session_id=None):
        cls = self.__class__
        self.session_id = session_id
        self.document_names = document_names
        self.json = JSONFile(name=session_id, read_method='w', data=json, \
                             output_name=self.document_names[cls.CONTRACT_DATA])
        self.template_file = TemplateFile(name=session_id, storage_object=template_file,\
                                          output_name=self.document_names[cls.CONTRACT_TEMPLATE])
        self.include_attachments = include_attachments
        self.docx_template = DocxTemplate(self.template_file)
        self.render()


    def render_to_docx(self):
        self.docx_template.render(self.json.data)
        self.docx_template.save()
        if does_file_exists(self.docx_template.full_path):
            app.logger.info('Template is rendered to docx.')
        else:
            raise DocumentRenderError()

    def render_to_pdf(self):
        self.pdf_document = DocxToPdfConverter(self.docx_template.template_file,
                            output_name=self.document_names[self.__class__.CONTRACT_PROFORMA]).pdf_document
        if does_file_exists(self.pdf_document.full_path):
            app.logger.info('Template is rendered to pdf')
        else:
            raise DocumentRenderError()

    def add_attachments_to_pdfa_file(self):
        if self.include_attachments:
            self.pdf_attacher = PdfAttacher(self.pdf_document)
            # adding attachments
            self.pdf_attacher.add_attachment(self.json)
            self.pdf_attacher.add_attachment(self.template_file)
            # writing output
            self.pdf_attacher.write_output()
            self.pdf_document = self.pdf_attacher.pdfa_file
            app.logger.info('Attachments are added.')

    def render(self):
        self.render_to_docx()
        self.render_to_pdf()
        self.add_attachments_to_pdfa_file()


class BaseHTMLRenderer(ObjectRenderer):

    REGEX_TO_REPLACE = []

    def __init__(self, template_file_name, session_id=None):
        self.session_id = session_id
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

    def __init__(self, template_file_name, session_id=None):
        super().__init__(template_file_name, session_id=session_id)

    def reformat_html(self):
        html_headers = ' '.join(self.__class__.HTML_HEADERS)
        html_footers = ' '.join(self.__class__.HTML_FOOTERS)
        self.formatted_html = html_headers + self.formatted_html + html_footers

    def encode_html(self):
        self.unicode_html = self.formatted_html.encode()
        app.logger.info('Template is encoded.')

    def save_html(self):
        self.html_file = HTMLFile(name=self.session_id, read_method='wb', data=self.unicode_html)
        self.html_file.write()
        self.html_file.close()
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

    def __init__(self, template_file_name, session_id=None):
        super().__init__(template_file_name, session_id=session_id)

    def convert(self):
        self.json_schema = HTMLToJSONTagSchemeConverter().convert(self.formatted_html)
        app.logger.info('Template is reformatted to json.')


class DocxToJSONSchemaRenderer(BaseHTMLRenderer):

    REGEX_TO_REPLACE = [
        [RegexConstants.ARRAY_FIELDS, RegexConstants.FIRST],
        [RegexConstants.A_LINKS, ""],
        [RegexConstants.TEMPLATE_FILTER, ""],
    ]

    def __init__(self, template_file_name, hide_empty_fields, session_id=None):
        self.hide_empty_fields = hide_empty_fields
        super().__init__(template_file_name, session_id=session_id)

    def convert(self):
        self.json_schema = HTMLToJSONSchemaConverter(
            self.hide_empty_fields).convert(self.formatted_html)
        app.logger.info('Template is reformatted to json.')

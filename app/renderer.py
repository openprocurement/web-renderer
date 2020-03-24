from flask import Flask
import json
import os
import time
from docxtpl import DocxTemplate
from app import app, jinja_env
from app.utils import format_date, generate_file_name, make_path, generate_file_path, convert_to_pdf
from app.constants import GENERATED_DOC_EXTENSION, GENERATED_DOC_PREFIX, TEMPLATE_PREFIX, TEMPLATE_FILE_EXTENSION, TEST_PREFIX


class RenderObject:

    def __init__(self, json=None, template_file=None):
        self.context = json
        self.template_file = template_file


class RenderDocxObject:

    def __init__(self, json=None, template_file=None):
        self.context = self.make_doc_context(json)
        self.template_file = template_file
        self.form_docx_template()
        self.init_functions()

    def make_doc_context(self, json):
        context = {}
        tender = json['data']
        context['contract'] = tender['contracts'][0]
        context['contract'].pop('documents', None)
        context['contract']['supplier'] = context['contract']['suppliers'][0]
        context['tender'] = {'procuringEntity': tender['procuringEntity']}
        return context

    def form_docx_template(self):
        docx_template_path = self.template_file.full_file_path
        self.docx_template = DocxTemplate(docx_template_path)

    def init_functions(self):
        jinja_env.filters['format_date'] = format_date

    def make_generated_doc_path(self):
        self.generated_doc_path = self.template_file.full_file_path.replace(
            TEMPLATE_PREFIX, GENERATED_DOC_PREFIX)

    def render_document_to_docx(self):
        self.make_generated_doc_path()
        self.docx_template.render(self.context, jinja_env)
        self.docx_template.save(self.generated_doc_path)

    def render(self):
        self.render_document_to_docx()
        convert_to_pdf(self.generated_doc_path)
        self.generated_pdf_path = self.generated_doc_path.replace(
            TEMPLATE_FILE_EXTENSION, GENERATED_DOC_EXTENSION)


class File:

    def __init__(self, file_storage_object, file_name=TEST_PREFIX):
        self.file_storage_object = file_storage_object
        self.file_name = file_name
        self.form_file_extension()
        self.form_full_path()

    def save_file(self):
        self.file_storage_object.save(self.full_file_path)

    def form_file_extension(self):
        self.file_extension = self.file_storage_object.filename.split('.')[1]

    def create_file_name(self, template_type=TEST_PREFIX):
        self.file_name = generate_file_name(template_type)

    def form_full_path(self):
        file_full_name = self.file_name+"."+self.file_extension
        self.full_file_path = make_path(file_full_name)

    def convert_to_pdf(self, timeout=None):
        convert_to_pdf(self.full_file_path)


class TemplateFile(File):

    def __init__(self, file_storage_object, file_name=TEST_PREFIX):
        self.file_storage_object = file_storage_object
        self.create_file_name()
        super().form_file_extension()
        super().form_full_path()
        super().save_file()

    def create_file_name(self, template_type=TEMPLATE_PREFIX):
        self.file_name = generate_file_name(template_type)

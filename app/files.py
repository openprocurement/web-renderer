from flask import Flask
import json
import os
import time
import re
from copy import deepcopy
from app import app
from app.utils.utils import (
    Path,
    FileUtils,
)
from app.constants import (
    GeneralConstants,
)
from app.handlers import format_exception
from app.exceptions import (
    InvalidDocumentFomat,
    DocumentSavingError,
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


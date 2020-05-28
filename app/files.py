import json
import os
import time
import re
from copy import deepcopy
from werkzeug.datastructures import FileStorage
from docx import Document
from docx.shared import Inches

from flask import Flask
from app import app
from app.utils.utils import (
    Path,
    FileUtils,
    getUUID,
)
from app.constants import (
    GeneralConstants,
)
from app.handlers import format_exception
from app.exceptions import (
    InvalidDocumentFomat,
    DocumentSavingError,
)

# File storage objects


class FileStorageObject(FileStorage):

    def __init__(self, path, file_name, content_type, stream=None):
        self.path = os.path.join(path)
        self.stream = open(path, "rb") if stream is None else stream
        self.file_name = file_name
        super().__init__(stream=self.stream,
                         filename=self.file_name,
                         content_type=content_type,)


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


class DocxFile:
    """
        Docx document class.
    """

    def __init__(self, name=None, folder=None):
        self.name = name
        self.folder = folder
        self.object = Document()

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        if name is not None:
            self.__name = name
        else:
            self.__name = str(getUUID()) + "." + \
                GeneralConstants.TEMPLATE_FILE_EXTENSION

    @property
    def path(self):
        return self.folder + self.name

    def save(self):
        self.object.save(self.path)

    def add_paragraph(self, data):
        p = self.object.add_paragraph(data)

    def add_heading(self, data, level):
        heading = self.object.add_heading(data, level=level)

    def add_table(row_number, col_number, table_data):
        """
            The method for table adding.
            Input:
                row_number- a row number including header row
                col_number - a column nomber including header row
                table_data - a matrix (list of lists)
        """
        table = self.object.add_table(rows=1, cols=3)
        for row in range(0, row_number):
            for column in range(0, col_number):
                table.rows[row].cells[column].text = str(
                    table_data[row][column])
            table.add_row().cells

    def add_page_break(self):
        self.object.add_page_break()

    def getAllText(self):
        return self.__class__.getAllText(document=self.object)

    def getTableContent(self, table_number):
        return self.__class__.getTableContent(table_number, document=self.object)

    def getAllTablesContent(self, table_number):
        return self.__class__.getAllTablesContent(document=self.object)

    @classmethod
    def getAllText(cls, filename=None, document=None):
        if(document is None):
            document = Document(filename)
        fullText = []
        for para in document.paragraphs:
            fullText.append(para.text)
        return '\n'.join(fullText)

    @classmethod
    def getTableContent(cls, table_number, filename=None, document=None):
        if(document is None):
            document = Document(filename)
        if table < table_number:
            table = document.tables[table_number]
        data = []
        keys = None
        for i, row in enumerate(table.rows):
            text = (cell.text for cell in row.cells)
            if i == 0:
                keys = tuple(text)
                continue
            row_data = dict(zip(keys, text))
            data.append(row_data)
        return data

    @classmethod
    def getAllTablesContent(cls, filename=None, document=None):
        if(document is None):
            document = Document(filename)
        data = []
        for table_number in range(0, len(document.tables)):
            table_data = cls.getTableContent(table_number, document=document)
            data.append(table_data)
        return data

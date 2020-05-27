from flask import Flask
import json
import os
import io
import time
import re
import json
from copy import deepcopy
from app import app
from app.utils.utils import (
    FileUtils,
    getNow,
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

# File objects


class BaseFile():
    
    def __init__(self, storage_object=None, full_path=None, method=None):
        self.full_path = full_path
        self.read_method = method
        self.storage_object = storage_object

    @property
    def storage_object(self):
        if (self.__storage_object is None):
            self.__storage_object = open(self.full_path, self.read_method)
        return self.__storage_object

    @storage_object.setter
    def storage_object(self, storage_obj):
        self.__storage_object = storage_obj

    def read(self):
        if 'r' in self.read_method:
            self.body = self.storage_object.read()

    def save(self):
        self.storage_object.save()

    def change_mode(self, method):
        self.method = method
        self.storage_object = open(self.full_path, self.method)

    def write(self, data):
        self.storage_object.write(data)

    def close(self):
        self.storage_object.close()


class File(BaseFile):

    def __init__(self, storage_object=None, name=None, extension=None, read_method=None):
        self.name = name
        self.extension = extension
        self.read_method = read_method
        super().__init__(storage_object, self.full_path, self.read_method)

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

    @property
    def extension(self):
        return self.__extension

    @extension.setter
    def extension(self, extension):
        self.__extension = extension

    @property
    def full_name(self):
        self.__full_name = self.name + "." + self.extension
        return self.__full_name

    @property
    def path(self):
        self.__path = GeneralConstants.UPLOAD_FOLDER + \
            self.full_name
        return self.__path

    @path.setter
    def path(self, path):
        self.__path = path

    @property
    def full_path(self):
        self.__full_path = GeneralConstants.UPLOADS_PATH + GeneralConstants.RENDERED_FILES_FOLDER + \
            self.full_name
        return self.__full_path

    @full_path.setter
    def full_path(self, full_path):
        self.__full_path = full_path

    def save(self):
        if not isinstance(self.storage_object, io.BufferedReader):
            self.storage_object.save(self.full_path)
        if FileUtils.does_file_exists(self.full_path):
            app.logger.info('File is saved.')
        else:
            raise DocumentSavingError()


class GeneratedFile(File):

    """
        File class that provides methods for generating file name, paths.

    """
    def __init__(self, storage_object=None, timestamp=None, uuid=None, read_method='rb', template_type=GeneralConstants.TEMPLATE_PREFIX, extension=None):
        self.storage_object = storage_object
        self.template_type = template_type
        self.timestamp = getNow() if timestamp is None else timestamp
        self.uuid = getUUID() if uuid is None else uuid
        self.extension = self.form_file_extension() if extension is None else extension
        self.read_method = read_method

    @property
    def name(self):
        self.__name = "_".join([self.template_type, self.timestamp, self.uuid])
        return self.__name

    @property
    def template_type(self):
        return self.__template_type

    @template_type.setter
    def template_type(self, template_type):
        self.__template_type = template_type

    def generate_file_name(self):
        self.timestamp = getNow()
        self.uuid = getUUID()
        self.name = "_".join([self.template_type, self.timestamp, self.uuid])

    def form_file_extension(self):
        if "." in self.storage_object.filename:
            return self.storage_object.filename.split('.')[1]
        else:
            raise InvalidDocumentFomat()

    @classmethod
    def get_obj_by_name(cls, file_name, template_type=GeneralConstants.TEMPLATE_PREFIX, extension=GeneralConstants.TEMPLATE_FILE_EXTENSION):
        """
            The class method for creating GeneratedFile obj from only file_name.
        """     
        timestamp, uuid = file_name.split(template_type)[1].split("_")[1:]
        return cls(timestamp=timestamp, uuid=uuid, template_type=template_type, extension=extension)


class TemplateFile(GeneratedFile):
    """
        Docx template file class.
    """
    def __init__(self, storage_object=None, timestamp=None, uuid=None, template_type=GeneralConstants.TEMPLATE_PREFIX, extension=None):
        super().__init__(storage_object=storage_object, timestamp=timestamp,
                         uuid=uuid, template_type=template_type, extension=extension)
        self.save()

    def save(self):
        if self.extension == GeneralConstants.TEMPLATE_FILE_EXTENSION:
            return super().save()
        else:
            raise InvalidDocumentFomat()


class HTMLFile(GeneratedFile):

    def __init__(self, read_method, content=None, storage_object=None, timestamp=None, uuid=None, template_type=GeneralConstants.TEMPLATE_PREFIX, extension=GeneralConstants.HTML_EXTENSION):
        super().__init__(storage_object=storage_object, timestamp=timestamp,
                         uuid=uuid, read_method=read_method,  template_type=template_type, extension=extension)
        self.content = content

    @property
    def path(self):
        self.__path = GeneralConstants.TEMP_FOLDER + \
            self.name + "." + self.extension
        return self.__path

    @property
    def full_path(self):
        self.__full_path = GeneralConstants.UPLOADS_PATH + GeneralConstants.TEMPLATES_TEMP_FOLDER + \
            self.name + "." + self.extension
        return self.__full_path

    def write(self):
        self.storage_object.write(self.content)


class JSONFile(GeneratedFile):

    def __init__(self, read_method, data=None, storage_object=None, timestamp=None, uuid=None, template_type=GeneralConstants.TEMPLATE_PREFIX, extension=GeneralConstants.JSON_EXTENSION):
        super().__init__(read_method=read_method, storage_object=storage_object,
                         timestamp=timestamp, uuid=uuid, template_type=template_type, extension=extension)
        self.data = data

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, data):
        if data is not None:
            self.__data = json.loads(data)
        with open(self.full_path, self.read_method) as f:
            json.dump(self.__data, f, indent=3)


class PdfFile(File):

    def __init__(self, path, read_method):
        super().__init__(path=path, read_method=read_method)
        self.read()


class AttachmentFile(File):
    """
        File class that is used for attachments.
    """
    def __init__(self, full_name, read_method):
        self.name = full_name.split('.')[0]
        self.extension = full_name.split('.')[1]
        self.read_method = read_method
        super().__init__(name=self.name, extension=self.extension, read_method=self.read_method)
        self.read()

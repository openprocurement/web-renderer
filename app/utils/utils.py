import os
from os import path
import subprocess
from flask import Flask
from datetime import datetime
import re
from pprint import pprint
from contextlib import contextmanager
from app import app
from app.constants import (
    GeneralConstants,
    RegexConstants,
)
from app.exceptions import (
    DocumentConvertionError,
    TemplateNotFound,
    JSONNotFound,
    TemplateIsEmpty,
    FileNameIsCyrillic,
    UndefinedVariableJinja,
    HTMLNotFoundError,
)


class Path:

    @classmethod
    def generate_file_name(cls, basename=GeneralConstants.TEMPLATE_PREFIX):
        suffix = datetime.now().strftime("%y%m%d_%H%M%S%f")
        file_name = "_".join([basename, suffix])
        return file_name

    @classmethod
    def make_path(cls, file_name):
        return GeneralConstants.UPLOAD_FOLDER + file_name

    @classmethod
    def make_full_file_path(cls, template_file, folder=GeneralConstants.RENDERED_FILES_FOLDER, extension=GeneralConstants.TEMPLATE_FILE_EXTENSION):
        return GeneralConstants.UPLOADS_PATH + folder + template_file + "." + extension

    @classmethod
    def make_full_html_path(cls, template_file, folder=GeneralConstants.TEMPLATES_TEMP_FOLDER, extension=GeneralConstants.HTML_EXTENSION):
        return cls.make_full_file_path(template_file, folder, extension)


class FileUtils:

    @classmethod
    def does_file_exists(cls, file):
        if path.exists(file):
            return True
        return False

    @classmethod
    def is_file_empty(cls, context):
        fullText = []
        for paragraph in context.paragraphs:
            fullText.append(paragraph.text)
        fullText = ''.join(fullText)
        if len(fullText) == 0:
            raise TemplateIsEmpty()
        return False

    @classmethod
    def is_file_name_cyrillic(cls, file_name):
        if (re.match(RegexConstants.CYRILLIC_TEXT, file_name)):
            raise FileNameIsCyrillic()
        return False

    @classmethod
    def is_file_attached(cls, file):
        try:
            if file.filename == '':
                raise TemplateNotFound()
            cls.is_file_name_cyrillic(file.filename)
        except AttributeError:
            raise TemplateNotFound()
        return True

    @classmethod
    def is_json_attached(cls, json_data):
        try:
            if len(json_data) == 0:
                raise JSONNotFound()
        except TypeError:
            raise JSONNotFound()
        return True

    @classmethod
    def does_data_attached(cls, file, json_data):
        cls.is_file_attached(file)
        cls.is_json_attached(json_data)
        return True


class FileManager:

    TEMP_FOLDERS = [
        GeneralConstants.UPLOADS_PATH + GeneralConstants.RENDERED_FILES_FOLDER,
        GeneralConstants.UPLOADS_PATH + GeneralConstants.TEMPLATES_TEMP_FOLDER,
    ]

    @classmethod
    def make_temp_folders(cls, timeout=True):
        for temp_folder in cls.TEMP_FOLDERS:
            if not os.path.exists(temp_folder):
                os.makedirs(temp_folder, exist_ok=True)

    @classmethod
    def remove_all_except_last_one(cls, temp_folder=None, timeout=None):
        if temp_folder is None:
            temp_folder = cls.TEMP_FOLDERS[0]
        args = ['ls', '-t1', temp_folder + "*", '|',
                'tail', '-n', '+2', '|', 'xargs', 'rm']
        process = subprocess.run(' '.join(args), shell=True, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, timeout=timeout)

    @classmethod
    def remove_temp(cls, remove_folder=False, temp_folder=None, timeout=None):
        if temp_folder is None:
            temp_folder = cls.TEMP_FOLDERS[1]
        if remove_folder:
            end_path = ""
        else:
            end_path = "*"
        args = ['rm', '-r', '-f', temp_folder + end_path]
        process = subprocess.run(' '.join(args), shell=True, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, timeout=timeout)


class ErrorUtils:

    @classmethod
    def process_jinja_undefined_var_error(cls, docx_template, error):
        """
                The function for processing jinja2.exceptions.UndefinedError. 
        """
        # import pdb
        # pdb.set_trace()
        undefined_value = re.findall(
            "'[a-zA-Z ]*'", error.args[0])
        undefined_value_item = 1 if len(undefined_value)>1 else 0
        undefined_value = undefined_value[undefined_value_item].replace("'", "")
        error_message = {
            "jinja_error": error.args[0],
            "possible_locations": docx_template.search(undefined_value)
        }
        raise UndefinedVariableJinja(error_message)


class Regex:

    @classmethod
    def replace_regex_list(cls, init_string, regex_list):
        for row in regex_list:
            init_string = re.sub(row[0], row[1], init_string)
        return init_string

    @classmethod
    def find_all_regexes_in_list(cls, regex_list, init_string):
        regex_to_extract = '|'.join(regex_list)
        regex = re.compile(regex_to_extract)
        result_list = re.findall(regex, init_string)
        result_list = [''.join(item) for item in result_list]
        return result_list

    @classmethod
    def does_strings_matches_regex(cls, regex_list, init_strings):
        is_included = 0
        if isinstance(init_strings, str):
            init_strings = [init_strings]
        for init_string in init_strings:
            resulted_list = cls.find_all_regexes_in_list(regex_list, init_string)
            if len(resulted_list):
                is_included += True
        return is_included > 0

    @classmethod
    def remove_prefix(cls, var_to_remove, string):
        regex_to_remove = "^"+str(var_to_remove)+"[._]{1}"
        string = re.sub(regex_to_remove, "", string)
        return string


# Context managers

@contextmanager
def file_decorator(file_path, file_options, exception_to_rise):
    try:
        template_file = open(file_path, file_options)
    except Exception as e:
        raise exception_to_rise()
    else:
        with template_file:
            yield


class GeneratorContextManager:

    def __init__(self, generator):
        self.end = False
        self.generator = generator
        self.has_next = False

    def __iter__(self):
        return self

    def __exit__(self, *args):
        end = True
        return False

    def __next__(self):
        self.current = next(self.generator)
        return self


class JSONListGeneratorContextManager(GeneratorContextManager):

    def __init__(self, generator):
        super().__init__(generator)
        self.FOR_LOOP_CONDITION = 0
        self.FOR_LOOP_VARIABLE = 1
        self.FOR_LOOP_ITERATED_LIST = 2
        self.ITERATOR = 0



def setdefaultattr(obj, name, value):
    if not hasattr(obj, name):
        setattr(obj, name, value)
    return getattr(obj, name)
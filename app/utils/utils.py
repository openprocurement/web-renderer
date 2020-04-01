import os
from os import path
import subprocess
from flask import Flask
from datetime import datetime
import re
from app import app
from app.constants import (
    TEMPLATE_UPLOAD_DIRECTORY_PATH,
    TEMPLATE_PREFIX,
    TEMPLATE_FILE_EXTENSION,
)
from app.exceptions import (
    DocumentConvertionError,
    TemplateNotFound,
    JSONNotFound,
    TemplateIsEmpty,
    FileNameIsCyrillic,
    UndefinedVariableJinja,
)


def generate_file_name(basename=TEMPLATE_PREFIX):
    suffix = datetime.now().strftime("%y%m%d_%H%M%S%f")
    file_name = "_".join([basename, suffix])
    return file_name


def make_path(file_name):
    return TEMPLATE_UPLOAD_DIRECTORY_PATH + file_name


def convert_to_pdf(full_file_path, timeout=None):
    args = ['libreoffice', '--headless', '--convert-to',
            'pdf', '--outdir', TEMPLATE_UPLOAD_DIRECTORY_PATH, full_file_path]
    try:
        process = subprocess.run(args, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, timeout=timeout)
    except FileNotFoundError as e:
        raise DocumentConvertionError()


def make_temp_folder(timeout=True):
    if not os.path.exists(TEMPLATE_UPLOAD_DIRECTORY_PATH):
        os.makedirs(TEMPLATE_UPLOAD_DIRECTORY_PATH)


def remove_temp(remove_folder=False, timeout=None):
    if remove_folder:
        end_path = ""
    else:
        end_path = "/*"
    args = ['rm', '-r', '-f', TEMPLATE_UPLOAD_DIRECTORY_PATH + end_path]
    process = subprocess.run(args, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, timeout=timeout)


def does_file_exists(file):
    if path.exists(file):
        return True
    return False


def is_file_attached(file):
    try:
        if file.filename == '':
            raise TemplateNotFound()
        is_file_name_cyrillic(file.filename)
    except AttributeError:
        raise TemplateNotFound()
    return True


def is_json_attached(json_data):
    try:
        if len(json_data) == 0:
            raise JSONNotFound()
    except TypeError:
        raise JSONNotFound()
    return True


def does_data_attached(file, json_data):
    is_file_attached(file)
    is_json_attached(json_data)
    return True


def is_file_empty(context):
    fullText = []
    for paragraph in context.paragraphs:
        fullText.append(paragraph.text)
    fullText = ''.join(fullText)
    if len(fullText) == 0:
        raise TemplateIsEmpty()
    return False


def is_file_name_cyrillic(file_name):
    if (re.match(r".*[а-яА-Я].*", file_name)):
        raise FileNameIsCyrillic()
    return False


def process_jinja_undefined_var_error(docx_template, error):
    """
        The function for processing jinja2.exceptions.UndefinedError. 
    """
    undefined_value = re.findall(
        "'[a-zA-Z ]*'", error.args[0])[1].replace("'", "")
    error_message = {
        "jinja_error": error.args[0],
        "possible_locations": docx_template.search(undefined_value)
    }
    raise UndefinedVariableJinja(error_message)

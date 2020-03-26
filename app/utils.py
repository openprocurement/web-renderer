import os
from os import path
import subprocess
from flask import Flask
from datetime import datetime
from app import app
from app.constants import (
    TEMPLATE_UPLOAD_DIRECTORY_PATH,
    TEMPLATE_PREFIX,
    TEMPLATE_FILE_EXTENSION)
from app.exceptions import (
    DocumentConvertionError,
    TemplateNotFound,
    JSONNotFound
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


def remove_temp_files(timeout=None):
    args = ['rm', '-r', '-f', TEMPLATE_UPLOAD_DIRECTORY_PATH]
    process = subprocess.run(args, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, timeout=timeout)


def does_file_exists(file):
    if path.exists(file):
        return True
    return False


def is_file_attached(file):
    try:
        file.filename
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

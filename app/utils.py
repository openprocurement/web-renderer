import os
import subprocess
from flask import Flask
from datetime import datetime
from app import app
from app.constants import TEMPLATE_UPLOAD_DIRECTORY_PATH, TEMPLATE_PREFIX, TEMPLATE_FILE_EXTENSION


def format_date(data):
    date_object = datetime.fromisoformat(data)
    str_date = date_object.strftime("%d.%m.%Y")
    return str_date


def generate_file_name(basename=TEMPLATE_PREFIX):
    suffix = datetime.now().strftime("%y%m%d_%H%M%S%f")
    file_name = "_".join([basename, suffix])
    return file_name


def make_path(file_name):
    return TEMPLATE_UPLOAD_DIRECTORY_PATH + "/" + file_name


def generate_file_path(basename=TEMPLATE_PREFIX, extension=TEMPLATE_FILE_EXTENSION):
    file_name = generate_file_name(basename)
    return make_path(file_name+"."+extension)


def convert_to_pdf(full_file_path, timeout=None):
    args = ['libreoffice', '--headless', '--convert-to',
            'pdf', '--outdir', TEMPLATE_UPLOAD_DIRECTORY_PATH, full_file_path]
    process = subprocess.run(args, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, timeout=timeout)
    

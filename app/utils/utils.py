import os
import re
import subprocess
from contextlib import contextmanager
import uuid
from datetime import datetime
from json import loads
from os import path
import uuid
from pprint import pprint

from flask import Flask

from app import app
from config import Config
from app.constants import GeneralConstants, RegexConstants
from app.exceptions import (FileNameIsCyrillic, JSONNotFound, TemplateIsEmpty, TemplateNotFound,)


# File utils:

TEMP_FOLDERS = [
    GeneralConstants.UPLOADS_PATH + Config.RENDERED_FILES_FOLDER,
    GeneralConstants.UPLOADS_PATH + Config.TEMPLATES_TEMP_FOLDER,
]


def does_file_exists(file):
    if path.exists(file):
        return True
    return False


def is_file_empty(context):
    fullText = []
    for paragraph in context.paragraphs:
        fullText.append(paragraph.text)
    fullText = ''.join(fullText)
    if len(fullText) == 0:
        raise TemplateIsEmpty()
    return False


def is_file_name_cyrillic(name):
    if (re.match(RegexConstants.CYRILLIC_TEXT, name)):
        raise FileNameIsCyrillic()
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


def is_data_attached(file, json_data):
    is_file_attached(file)
    is_json_attached(json_data)
    return True


def make_temp_folders(timeout=True):
    for temp_folder in TEMP_FOLDERS:
        if not os.path.exists(temp_folder):
            os.makedirs(temp_folder, exist_ok=True)


def remove_all_except_last(number_to_leave=4, temp_folder=None, timeout=None):
    if temp_folder is None:
        temp_folder = TEMP_FOLDERS[0]
    args = ['ls', '-t1', temp_folder + "*", '|',
            'tail', '-n', '+'+str(number_to_leave+1), '|', 'xargs', 'rm']
    process = subprocess.run(' '.join(args), shell=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, timeout=timeout)


def remove_temp(with_folder=False, temp_folder=None, timeout=None):
    temp_folder = TEMP_FOLDERS[1] if temp_folder is None else temp_folder
    end_path = "" if with_folder else "*"
    args = ['rm', '-r', '-f', temp_folder + end_path]
    process = subprocess.run(' '.join(args), shell=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, timeout=timeout)


def remove_file(file_name):
    args = ['rm', file_name]
    process = subprocess.run(' '.join(args), shell=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

# Regex utils

def replace_regex_list(init_string, regex_list):
    for row in regex_list:
        init_string = re.sub(row[0], row[1], init_string)
    return init_string


def find_all_regexes_in_list(regex_list, init_string):
    regex_to_extract = '|'.join(regex_list)
    regex = re.compile(regex_to_extract)
    result_list = re.findall(regex, init_string)
    result_list = [''.join(item) for item in result_list]
    return result_list


def does_strings_matches_regex(regex_list, init_strings):
    is_included = 0
    if isinstance(init_strings, str):
        init_strings = [init_strings]
    for init_string in init_strings:
        resulted_list = find_all_regexes_in_list(
            regex_list, init_string)
        if len(resulted_list):
            is_included += True
    return is_included > 0

def remove_prefix(var_to_remove, string):
    regex_to_remove = "^"+str(var_to_remove)+"[._]{1}"
    string = re.sub(regex_to_remove, "", string)
    return string

# getters

def getNow():
    return datetime.now().strftime("%y%m%d%H%M%S%f")

def getUUID():
    return uuid.uuid4().hex

# Object functions

def setdefaultattr(obj, name, value):
    if not hasattr(obj, name):
        setattr(obj, name, value)
    return getattr(obj, name)

# JSON utils

def read_json(filename):
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    project_dir = "/".join(curr_dir.split('/')[:-1])
    file_path = os.path.join(project_dir, filename)
    with open(file_path) as _file:
        data = _file.read()
    return loads(data)

# Form utils

def get_checkbox_value(value):
    if value.lower() == "true":
        return True
    else:
        return False
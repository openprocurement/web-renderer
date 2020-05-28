import json
import re
import inspect
import jinja2.exceptions
import docx.opc.exceptions
import werkzeug.exceptions

from flask import Flask
from app import app
from app.exceptions import(
    format_exception,
    InvalidDocumentFomat,
    DocumentConvertionError,
    DocumentRenderError,
    DocumentSavingError,
    CustomException,
    HTMLNotFoundError,
)

# Library exceptions handlers


@app.errorhandler(json.decoder.JSONDecodeError)
def json_decode_error_handler(error):
    return format_exception("json_data is not in valid JSON format ", 500)


@app.errorhandler(docx.opc.exceptions.PackageNotFoundError)
def docx_package_not_found_error(error):
    return format_exception("Template file is invalid.", 500)


@app.errorhandler(jinja2.exceptions.TemplateError)
def jinja2_undefined_error(error):
    return format_exception("Template values do not match data_json:"+str(*error.args), 500)


@app.errorhandler(jinja2.exceptions.UndefinedError)
def jinja_undefined_error(error):
    return format_exception("Template values do not match data_json:"+str(*error.args), 500)


@app.errorhandler(werkzeug.exceptions.MethodNotAllowed)
def method_not_allowed_handler(error):
    return format_exception("Method is not allowed.", 405)


@app.errorhandler(werkzeug.exceptions.BadRequestKeyError)
def bad_request_key_error(error):
    return format_exception(error.description, 500)


@app.errorhandler(re.error)
def regex_error(error):
    return format_exception(str(*error.args), 500)
# Custom exceptions handler


@app.errorhandler(Exception)
def custom_exceptions_error_handler(error):
    if isinstance(error, CustomException):
        return format_exception(error.description, error.code)


# Base exceptions handlers

@app.errorhandler(IndexError)
@app.errorhandler(ValueError)
@app.errorhandler(FileExistsError)
@app.errorhandler(RuntimeError)
@app.errorhandler(TypeError)
@app.errorhandler(AttributeError)
@app.errorhandler(NameError)
def base_exceptions_handler(error):
    return format_exception(str(*error.args), 500)


@app.errorhandler(FileNotFoundError)
def file_not_found_handler(error):
    return format_exception(str(*error.args), 404)

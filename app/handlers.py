from flask import Flask
from app import app
from app.exceptions import(
    format_exception,
    InvalidDocumentFomat,
    DocumentConvertionError,
    DocumentRenderError,
    DocumentSavingError,
    CustomException)
import json
import docx.opc.exceptions
import werkzeug.exceptions
import jinja2.exceptions
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
# Custom exceptions handler


@app.errorhandler(Exception)
def custom_exceptions_error_handler(error):
    if isinstance(error, CustomException):
        return format_exception(error.description, error.code)


# Base exceptions handlers


@app.errorhandler(werkzeug.exceptions.MethodNotAllowed)
def method_not_allowed_handler(error):
    return format_exception("Method is not allowed.", 405)


@app.errorhandler(TypeError)
def type_error_handler(error):
    return format_exception(str(*error.args), 500)


@app.errorhandler(FileNotFoundError)
def file_not_found_handler(error):
    return format_exception("File is not found.", 404)

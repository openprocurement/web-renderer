from flask import Flask
from app import app
from app.exceptions import(
    raise_exception,
    InvalidDocumentFomat,
    DocumentConvertionError,
    DocumentRenderError,
    DocumentSavingError)
import json
import docx.opc.exceptions
import werkzeug.exceptions

# Library exceptions handlers


@app.errorhandler(json.decoder.JSONDecodeError)
def json_decode_error_handler(error):
    return raise_exception("json_data is not in valid JSON format ", 404)


@app.errorhandler(docx.opc.exceptions.PackageNotFoundError)
def docx_package_not_found_error(error):
    return raise_exception("Template file is invalid.", 508)

# Custom exceptions handlers


@app.errorhandler(InvalidDocumentFomat)
def json_decode_error_handler(error):
    return raise_exception("Template file has an invalid document format.", 507)


@app.errorhandler(DocumentConvertionError)
def document_Convertion_error(error):
    return raise_exception("Document convertion error", 508)


@app.errorhandler(DocumentRenderError)
def document_Convertion_error(error):
    return raise_exception("Document rendering error", 509)


@app.errorhandler(DocumentSavingError)
def document_Convertion_error(error):
    return raise_exception("Document saving error", 510)

# Base exceptions handlers


@app.errorhandler(werkzeug.exceptions.MethodNotAllowed)
def method_not_allowed_handler(error):
    return raise_exception("Method is not allowed.", 405)

@app.errorhandler(FileNotFoundError)
def file_not_found_handler(error):
    return raise_exception("File is not found.", 404)

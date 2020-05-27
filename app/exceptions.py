from flask import Flask
import werkzeug
from app import app


def format_exception(error, error_code, location=None):
    app.logger.error(str(error) + " " + str(error_code))
    error_message = {
        "error": {
            "code": error_code,
            "message": error
        }
    }
    if location is not None:
        error_message["error"]["location"] =  location
    return error_message, error_code


class CustomException(werkzeug.exceptions.HTTPException):
    code = int


class CustomNotFound(CustomException, werkzeug.exceptions.NotFound):
    code = 404


class CustomInternalServerError(CustomException, werkzeug.exceptions.InternalServerError):
    code = 500


class CustomUnprocessableEntity(CustomException, werkzeug.exceptions.UnprocessableEntity):
    code = 422


class CustomUnsupportedMediaType(CustomException, werkzeug.exceptions.UnsupportedMediaType):
    code = 415


class JSONNotFound(CustomNotFound):
    description = "JSON data is not found"


class TemplateNotFound(CustomNotFound):
    description = "Template file is not found"


class HTMLNotFoundError(CustomUnsupportedMediaType):
    description = "HTML is not found"


class InvalidDocumentFomat(CustomInternalServerError):
    description = 'Invalid template document format.'


class DocumentConvertionError(CustomInternalServerError):
    description = 'Document convertion error.'


class DocumentRenderError(CustomInternalServerError):
    description = 'Document rendering error.'


class DocumentSavingError(CustomInternalServerError):
    description = 'Document saving error.'


class TemplateIsEmpty(CustomUnprocessableEntity):
    description = 'Template is empty'


class FileNameIsCyrillic(CustomUnprocessableEntity):
    description = 'Cyrrilic file names are not supported'


class UndefinedVariableJinja(CustomUnprocessableEntity):
    description = 'Undefined variable in the template'

from flask import Flask
import werkzeug
from app import app


def format_exception(error, error_code):
    app.logger.error(str(error) + " " + str(error_code))
    return {
        "error": {
            "code": error_code,
            "message": error
        }
    }, error_code


class CustomException(werkzeug.exceptions.HTTPException):
    code = int


class CustomNotFound(CustomException, werkzeug.exceptions.NotFound):
    code = 404


class CustomInternalServerError(CustomException, werkzeug.exceptions.InternalServerError):
    code = 500


class JSONNotFound(CustomNotFound):
    description = "json_data is not found"


class TemplateNotFound(CustomNotFound):
    description = "template data is not found"

class HTMLNotFoundError(CustomNotFound):
    description = "html is not found"

class InvalidDocumentFomat(CustomInternalServerError):
    description = 'Invalid template document format.'


class DocumentConvertionError(CustomInternalServerError):
    description = 'Document Convertion Error.'


class DocumentRenderError(CustomInternalServerError):
    description = 'Document rendering error.'


class DocumentSavingError(CustomInternalServerError):
    description = 'Document saving error.'


class TemplateIsEmpty(CustomInternalServerError):
    description = 'Template is empty'


class FileNameIsCyrillic(CustomInternalServerError):
    description = 'Cyrrilic file names are not supported'


class UndefinedVariableJinja(CustomInternalServerError):
    description = 'Undefined variable in the template'
from flask import Flask
import werkzeug
from app import app


def raise_exception(error, error_code):
    app.logger.error(error+" "+str(error_code))
    return {
        "error": {
            "code": error_code,
            "message": error
        }
    }, error_code


class InvalidDocumentFomat(werkzeug.exceptions.HTTPException):
    code = 507
    description = 'Invalid template document format.'


class DocumentConvertionError(werkzeug.exceptions.HTTPException):
    code = 508
    description = 'Document Convertion Error.'


class DocumentRenderError(werkzeug.exceptions.HTTPException):
    code = 509
    description = 'Document rendering error.'


class DocumentSavingError(werkzeug.exceptions.HTTPException):
    code = 510
    description = 'Document saving error.'

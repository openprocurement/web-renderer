import os
from os.path import join, dirname, realpath
from app import app

UPLOADS_PATH = dirname(realpath(__file__))+"/"
UPLOAD_FOLDER = os.path.join(app.config['UPLOAD_FOLDER'])
RENDERED_FILES_FOLDER = os.path.join(app.config['RENDERED_FILES_FOLDER'])
TEMPLATES_TEMP_FOLDER = os.path.join(app.config['TEMPLATES_TEMP_FOLDER'])
TEMP_FOLDER = os.path.join(app.config['TEMP_FOLDER'])
TEMPLATE_PREFIX = "doc_template"
GENERATED_DOC_PREFIX = "generated"
TEMPLATE_FILE_EXTENSION = "docx"
GENERATED_DOC_EXTENSION = "pdf"
HTML_EXTENSION = "html"
TEST_PREFIX = "test",
ALLOWED_EXTENSIONS = [TEMPLATE_FILE_EXTENSION, ]

import os


class Config(object):
    DEBUG = os.environ.get('DEBUG')
    SECRET_KEY = os.urandom(32)
    APP_FOLDER = 'app/'
    TEMPLATES_FOLDER = "templates/"
    TEMP_FOLDER = ".temp/"
    TEMPLATES_TEMP_FOLDER = TEMPLATES_FOLDER + TEMP_FOLDER
    RENDERED_FILES_FOLDER = TEMP_FOLDER + "files/"
    UPLOAD_FOLDER = APP_FOLDER + RENDERED_FILES_FOLDER
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
        os.mknod(UPLOAD_FOLDER+"__init__.py")
    # HEADERS
    CORS_HEADERS = 'Content-Type'

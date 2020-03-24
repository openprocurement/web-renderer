import os


class Config(object):
    APP_FOLDER = 'app/'
    TEMPLATES_FOLDER = '.templates/'
    UPLOAD_FOLDER = APP_FOLDER+TEMPLATES_FOLDER
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

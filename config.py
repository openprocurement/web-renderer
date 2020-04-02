import os


class Config(object):
    WTF_CSRF_SECRET_KEY = os.urandom(24)
    SECRET_KEY = os.urandom(24)
    SESSION_TYPE = 'filesystem'
    APP_FOLDER = 'app/'
    TEMPLATES_FOLDER = '.templates/'
    UPLOAD_FOLDER = APP_FOLDER+TEMPLATES_FOLDER
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
        os.mknod(UPLOAD_FOLDER+"__init__.py")

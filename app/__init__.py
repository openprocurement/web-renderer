from flask import Flask
from os import environ
from flask_cors import CORS, cross_origin

from config import Config
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration


sentry_sdk.init(
    integrations=[
        FlaskIntegration(),
    ],
    traces_sample_rate=1.0,
)

app = Flask(__name__)
app.config.from_object(Config)
cors = CORS(app)

from app import log

from app import constants
from app import views
from app import urls
from app import models
from app import handlers
from app import exceptions
from app import utils
from app import render_env
from app.render_env.env import JinjaEnvironment
app.jinja_env_obj = JinjaEnvironment()

@app.template_filter()
def slugify(string):
    """
        The filter for template to HTML form rendering. 
    """
    return string.lower().replace(' ', '_')

# make temp folders
from app.utils.utils import make_or_clear
make_or_clear(Config.UPLOAD_FOLDER)
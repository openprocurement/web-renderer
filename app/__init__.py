from flask import Flask
from os import environ
from flask_cors import CORS, cross_origin

from config import Config


app = Flask(__name__)
app.config.from_object(Config)
cors = CORS(app)

import logging
app.logger.setLevel(logging.INFO)

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
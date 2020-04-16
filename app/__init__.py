from flask import Flask
from os import environ

from config import Config


app = Flask(__name__)
app.config.from_object(Config)

import logging
app.logger.setLevel(logging.INFO)

from app import constants
from app import views
from app import models
from app import handlers
from app import exceptions
from app import utils
from app import render_environment
from app.render_environment.template_environment import JinjaEnvironment
app.jinja_env_obj = JinjaEnvironment()
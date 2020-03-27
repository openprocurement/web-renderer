from flask import Flask
from os import environ

from config import Config

import jinja2
jinja_env = jinja2.Environment()

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
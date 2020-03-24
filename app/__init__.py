from flask import Flask
from os import environ

from config import Config
import app.models
import app.views

app = Flask(__name__)
app.config.from_object(Config)
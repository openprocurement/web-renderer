from flask import Flask
from flask_wtf import FlaskForm
from wtforms import validators, StringField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from app import app
from app.constants import(
    ALLOWED_EXTENSIONS,
)


class UploadForm(FlaskForm):
    template = FileField('file', validators=[
        FileRequired(),
        FileAllowed(ALLOWED_EXTENSIONS, 'Images only!')
    ])
    json_data = StringField(
        u'Full Name', [validators.required(), validators.length(max=10000)])

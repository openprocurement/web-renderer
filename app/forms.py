from flask import Flask
from flask_wtf import FlaskForm
from wtforms import validators, StringField, SubmitField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from app import app
from app.constants import(
    ALLOWED_EXTENSIONS,
)


class UploadForm(FlaskForm):
    contract = FileField('file', validators=[
        FileRequired(),
        FileAllowed(ALLOWED_EXTENSIONS, str(ALLOWED_EXTENSIONS))
    ])
    json_data = StringField(
        u'JSON_DATA', [validators.length(max=10000)])
    sumbit_button = SubmitField(label='Submit')
    display_template_form = SubmitField(label='Display template form')

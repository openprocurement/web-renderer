from flask import Flask
from flask_wtf import FlaskForm
from wtforms import validators, StringField, SubmitField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from app import app
from app.constants import(
    GeneralConstants,
)


class UploadForm(FlaskForm):
    contract = FileField('file', validators=[
        FileRequired(),
        FileAllowed(GeneralConstants.ALLOWED_EXTENSIONS, str(GeneralConstants.ALLOWED_EXTENSIONS))
    ])
    json_data = StringField(
        u'JSON_DATA', [validators.length(max=10000)])
    sumbit_button = SubmitField(label='Submit')
    display_template_form = SubmitField(label='Display template form')
    get_template_json = SubmitField(label='Get template json')
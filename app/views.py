from flask import Flask, request, abort, jsonify, send_from_directory, send_file
import json
import logging

from app import app
from app.renderer import RenderDocxObject, File, TemplateFile
from app.constants import TEMPLATES_FOLDER
from app.utils import remove_temp_files, is_file_selected
from app.exceptions import raise_exception

@app.before_request
def before_request_func():
    app.logger.info('Request is started')


@app.route('/', methods=['POST'])
def post():
    json_data = request.form.get('json_data')
    if len(json_data)==0:
        return raise_exception("json_data is not found", 404)
    template_file = request.files.get('template')
    if not is_file_selected(template_file):
        return raise_exception("Template is not found", 404)
    content = json.loads(json_data)
    docx_file = TemplateFile(template_file)
    renderer = RenderDocxObject(content, docx_file)
    renderer.render()
    generated_file = TEMPLATES_FOLDER+renderer.generated_pdf_path.split("/")[-1]
    return send_file(generated_file,  as_attachment=True)


@app.after_request
def after_request_func(response):
    remove_temp_files()
    app.logger.info('Tempfiles are removed')
    app.logger.info('Request is finished')
    return response

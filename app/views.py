from flask import (
    Flask, request, abort, jsonify, send_from_directory, send_file, redirect, url_for,
    render_template)
import json
import logging
import os
from app import app
from config import Config
from app.renderers import (
    TemplateFile,
    DocxToPDFRenderer,
    DocxToHTMLRenderer,
    DocxToJSONSchemaRenderer,
    DocxToTagSchemaRenderer,
)
from app.constants import (
    GeneralConstants,
)
from app.utils.utils import (
    FileUtils,
    FileManager,
    get_checkbox_value,
)
from app.forms import(
    UploadForm,
)
from app.files import (
    JSONFile,
)



@app.before_request
def before_request_func():
    app.logger.info('Request is started')
    FileManager.make_temp_folders()
    app.logger.info('Tempfolder is created')


@app.route('/', methods=['GET'])
def upload_file():
    form = UploadForm(request.form)
    result = request.form
    return render_template('upload_form.html', result=result)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory((os.path.join(app.root_path), Config.TEMPLATES_FOLDER + 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/display_template_form', methods=["GET"])
def display_template_form():
    template_file = request.args.get('template')
    html_renderer = DocxToHTMLRenderer(template_file)
    html_file = html_renderer.html_file.path
    return render_template(html_file)


@app.route('/get_template_tag_schema', methods=["GET"])
def get_template_tag_schema():
    template_file = request.args.get('template')
    html_json = DocxToTagSchemaRenderer(template_file).json_schema
    return jsonify(html_json)

@app.route('/get_template_json_schema', methods=["GET"])
def get_template_json_schema():
    template_file = request.args.get('template')
    hide_empty_fields = int(request.args.get('hide_empty_fields'))
    html_json = DocxToJSONSchemaRenderer(template_file, hide_empty_fields).json_schema
    return jsonify(html_json)

@app.route('/', methods=['POST'])
def post():
    """
        requestBody:
            json_data:
                content: application/json:
            template:
                content: file
    """
    form_values = request.form.to_dict(flat=True)
    if "display_template_form" in form_values:
        template_file = request.files.get('template')
        FileUtils.is_file_attached(template_file)
        docx_file = TemplateFile(template_file)
        return redirect(url_for('display_template_form', template=docx_file.name))
    elif "get_template_tag_schema" in form_values:
        template_file = request.files.get('template')
        FileUtils.is_file_attached(template_file)
        docx_file = TemplateFile(template_file)
        return redirect(url_for('get_template_tag_schema', template=docx_file.name))
    elif "get_template_json_schema" in form_values:
        template_file = request.files.get('template')
        FileUtils.is_file_attached(template_file)
        docx_file = TemplateFile(template_file)
        hide_empty_fields = 1 if "hide_empty_fields" in form_values else 0
        return redirect(url_for('get_template_json_schema', template=docx_file.name, hide_empty_fields=hide_empty_fields))
    else:
        template_file = request.files.get('template')
        json_data = request.form.get('json_data')
        if "include_attachments" in form_values:
            include_attachments = get_checkbox_value(form_values['include_attachments'])
        else:
            include_attachments = False
        FileUtils.does_data_attached(template_file, json_data)
        content = JSONFile('w', json_data)
        renderer = DocxToPDFRenderer(content, template_file, include_attachments)
        generated_file = Config.RENDERED_FILES_FOLDER + \
            renderer.generated_pdf_path.split("/")[-1]
        return send_file(generated_file,  as_attachment=True)


@app.after_request
def after_request_func(response):
    FileManager.remove_all_except_last()
    FileManager.remove_temp()
    app.logger.info('Tempfiles are removed')
    app.logger.info('Request is finished')
    return response


@app.teardown_request
def after_all_requests(response):
    FileManager.remove_temp(True)
    app.logger.info('Tempfolder is removed')

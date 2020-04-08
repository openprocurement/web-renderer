from flask import (
    Flask, request, abort, jsonify, send_from_directory, send_file, redirect, url_for,
    render_template)
import json
import logging
from app import app
from app.renderers import (
    TemplateFile,
    DocxToPDFRenderer,
    DocxToHTMLRenderer,
)
from app.constants import (
    GeneralConstants,
)
from app.utils.utils import (
    FileUtils,
    FileManager,
)
from app.forms import(
    UploadForm,
)
import os


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
    return send_from_directory((os.path.join(app.root_path), GeneralConstants.TEMPLATES_FOLDER + 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/display_template_form', methods=["GET"])
def display_template_form():
    template_file = request.args.get('template')
    html_renderer = DocxToHTMLRenderer(template_file)
    html_file = GeneralConstants.TEMP_FOLDER + \
        html_renderer.html_file_name + "." + GeneralConstants.HTML_EXTENSION
    return render_template(html_file)


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
        return redirect(url_for('display_template_form', template=docx_file.file_name))
    else:
        template_file = request.files.get('template')
        json_data = request.form.get('json_data')
        FileUtils.does_data_attached(template_file, json_data)
        content = json.loads(json_data)
        renderer = DocxToPDFRenderer(content, template_file)
        generated_file = GeneralConstants.RENDERED_FILES_FOLDER + \
            renderer.generated_pdf_path.split("/")[-1]
        return send_file(generated_file,  as_attachment=True)


@app.after_request
def after_request_func(response):
    FileManager.remove_all_except_last_one()
    FileManager.remove_temp()
    app.logger.info('Tempfiles are removed')
    app.logger.info('Request is finished')
    return response


@app.teardown_request
def after_all_requests(response):
    FileManager.remove_temp(True)
    app.logger.info('Tempfolder is removed')

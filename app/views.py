from flask import (
    Flask, request, abort, jsonify, send_from_directory, send_file, redirect, url_for,
    render_template)
import json
import logging
from app import app
from app.renderer import RenderDocxObject, File, TemplateFile
from app.constants import (
    RENDERED_FILES_FOLDER,
    TEMP_FOLDER,
    HTML_EXTENSION,
)
from app.utils.utils import (
    does_data_attached,
    make_temp_folders,
    make_path,
    is_file_attached,
    remove_temp_files,
    remove_temp_templates,
)
from app.exceptions import (
    JSONNotFound,
    TemplateNotFound,
)
from app.forms import(
    UploadForm,
)
from app.html_renderer import(
    HTMLRenderer,
)


@app.route('/', methods=['GET'])
def upload_file():
    form = UploadForm(request.form)
    result = request.form
    return render_template('upload_form.html', result=result)


@app.route('/display_template_form', methods=["GET"])
def display_template_form():
    template_file = request.args.get('template')
    html_renderer = HTMLRenderer(template_file)
    html_file = TEMP_FOLDER + html_renderer.html_file_name + "." + HTML_EXTENSION
    return render_template(html_file)


@app.before_request
def before_request_func():
    app.logger.info('Request is started')
    make_temp_folders()
    app.logger.info('Tempfolder is created')


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
        is_file_attached(template_file)
        docx_file = TemplateFile(template_file)
        file_name = docx_file.file_name
        return redirect(url_for('display_template_form', template=file_name))
    else:
        template_file = request.files.get('template')
        json_data = request.form.get('json_data')
        does_data_attached(template_file, json_data)
        content = json.loads(json_data)
        docx_file = TemplateFile(template_file)
        renderer = RenderDocxObject(content, docx_file)
        renderer.render()
        generated_file = RENDERED_FILES_FOLDER + \
            renderer.generated_pdf_path.split("/")[-1]
        return send_file(generated_file,  as_attachment=True)


@app.after_request
def after_request_func(response):
    remove_temp_files()
    remove_temp_templates()
    app.logger.info('Tempfiles are removed')
    app.logger.info('Request is finished')
    return response


@app.teardown_request
def after_all_requests(response):
    app.logger.info('Tempfolder is removed')
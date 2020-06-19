import json
import logging
import os

from flask import (
    Flask, request, abort, jsonify, send_from_directory, send_file, redirect, url_for,
    render_template, session
)
from flask.views import(
    MethodView,
)
from config import Config
from app import app
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
    make_temp_folders,
    remove_temp,
    remove_session_files,
    remove_all_except_last,
    is_file_attached,
    is_data_attached,
    is_json_attached,
    get_checkbox_value,
)
from app.forms import(
    UploadForm,
)
from app.utils.utils import(
    getUUID,
)
from app.decorators import (form_data, )


@app.before_request
def before_request_func():
    app.logger.info('Request is started')
    make_temp_folders()
    app.logger.info('Tempfolder is created')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory((os.path.join(app.root_path), Config.TEMPLATES_FOLDER + 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@form_data
class DisplayFormView(MethodView):

    def get(self):
        cls = self.__class__
        template_file = request.args.get(cls.TEMPLATE)
        html_renderer = DocxToHTMLRenderer(
            template_file, session_id=session['id'])
        html_file = html_renderer.html_file.path
        return render_template(html_file)


@form_data
class GetTagSchemaView(MethodView):

    def get(self):
        cls = self.__class__
        template_file = request.args.get(cls.TEMPLATE)
        html_json = DocxToTagSchemaRenderer(
            template_file, session_id=session['id']).json_schema
        return jsonify(html_json)


@form_data
class GetJSONSchemaView(MethodView):

    def get(self):
        cls = self.__class__
        template_file = request.args.get(cls.TEMPLATE)
        hide_empty_fields = int(request.args.get(cls.HIDE_EMPTY_FIELDS))
        html_json = DocxToJSONSchemaRenderer(
            template_file, hide_empty_fields, session_id=session['id']).json_schema
        return jsonify(html_json)


@form_data
class RenderView(MethodView):

    def get(self):
        session['id'] = getUUID()
        form = UploadForm(request.form)
        result = request.form
        return render_template('upload_form.html', result=result)

    def form_document_names(self, request):
        cls = self.__class__
        document_names = request.form.get(cls.DOCUMENT_NAMES)
        file_name = str(request.files.get(cls.TEMPLATE).filename).split('.')[0]
        document_names = json.loads(document_names) if document_names is not None else \
            dict.fromkeys([cls.CONTRACT_DATA, cls.CONTRACT_TEMPLATE,
                           cls.CONTRACT_PROFORMA], file_name)
        return document_names

    def post(self):
        """
            requestBody:
                json_data:
                    content: application/json:
                template:
                    content: file
        """
        cls = self.__class__
        session['id'] = getUUID()
        form_values = request.form.to_dict(flat=True)

        template_file = request.files.get(cls.TEMPLATE)
        is_file_attached(template_file)

        if "display_template_form" in form_values:
            docx_file = TemplateFile(
                name=session['id'], storage_object=template_file)
            return redirect(url_for('display_template_form', template=docx_file.name))
        elif "get_template_tag_schema" in form_values:
            docx_file = TemplateFile(
                name=session['id'], storage_object=template_file)
            return redirect(url_for('get_template_tag_schema', template=docx_file.name))
        elif "get_template_json_schema" in form_values:
            docx_file = TemplateFile(
                name=session['id'], storage_object=template_file)
            hide_empty_fields = 1 if request.form.get(
                cls.HIDE_EMPTY_FIELDS) is not None else 0
            return redirect(url_for('get_template_json_schema', template=docx_file.name, hide_empty_fields=hide_empty_fields))
        else:
            json_data = request.form.get(cls.JSON_DATA)
            is_json_attached(json_data)
            include_attachments = get_checkbox_value(request.form.get(cls.INCLUDE_ATTACHMENTS)) \
                if request.form.get(cls.INCLUDE_ATTACHMENTS) is not None else False
            document_names = self.form_document_names(request)
            renderer = DocxToPDFRenderer(
                json_data, template_file, include_attachments, document_names=document_names, session_id=session['id'])
            return send_file(renderer.pdf_document.path,  as_attachment=True,
                             attachment_filename=renderer.pdf_document.output_full_name)


@app.after_request
def after_request_func(response):
    remove_temp(with_folder=False)
    if response.headers.get('Location') is None: 
        # Session files are being removed only after all redirections
        remove_session_files(session['id'])
        app.logger.info('Sessions files were removed')
    app.logger.info('Templates temp files were removed')
    return response


@app.teardown_request
def after_all_requests(response):
    remove_temp(with_folder=True)
    remove_all_except_last()
    app.logger.info('Template temp folder was removed')
    app.logger.info('Request completed')
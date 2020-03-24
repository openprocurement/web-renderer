from flask import Flask, request, jsonify, send_from_directory, send_file
from app import app
from app.renderer import RenderDocxObject, File, TemplateFile
from app.constants import TEMPLATES_FOLDER
import json

@app.route('/', methods=['POST'])
def post():
    content = json.loads(request.form.get('json_data'))
    template_file = request.files.get('template')
    docx_file = TemplateFile(template_file)
    renderer = RenderDocxObject(content, docx_file)
    renderer.render()
    result_file = TEMPLATES_FOLDER+renderer.generated_pdf_path.split("/")[-1]
    return send_file(result_file,  as_attachment=True )

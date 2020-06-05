import mammoth
import subprocess
from copy import deepcopy
from app.exceptions import (
    DocumentConvertionError,
)
from app.constants import (
    GeneralConstants,
)
from app.files import (
    PdfFile,
    TemplateFile,
)
from app.utils.utils import (
    replace_regex_list,
)
from config import Config


class DocxToHTMLConverter:

    def __init__(self, document):
        self.document = document
        self.convert()

    def convert(self):
        self.html = mammoth.convert_to_html(self.document)

    def replace_regexes(self, regexes):
        formatted_html = deepcopy(self.html.value)
        return replace_regex_list(formatted_html, regexes)

    @classmethod
    def convert_to_html(cls, template_file):
        document = mammoth.convert_to_html(template_file)
        return document


class DocxToPdfConverter:

    def __init__(self, document):
        self.document = document
        self.convert()

    def convert(self, timeout=None):
        full_path = self.document.full_path
        args = ['libreoffice', '--headless', '--convert-to',
                'pdf', '--outdir', Config.UPLOAD_FOLDER, full_path]
        try:
            process = subprocess.run(args, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, timeout=timeout)
        except FileNotFoundError as e:
            raise DocumentConvertionError()
        
        self.pdf_document = TemplateFile.get_obj_by_name(self.document.name)
        self.pdf_document.extension = GeneralConstants.GENERATED_DOC_EXTENSION
        self.generated_pdf_path = self.pdf_document.full_path
        self.document.template_file.close()
        self.pdf_document.close()

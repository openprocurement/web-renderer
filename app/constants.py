import os
from os.path import join, dirname, realpath
from app import app


class GeneralConstants:
    # Folders
    UPLOADS_PATH = dirname(realpath(__file__))+"/"
    # Prefixes
    TEMPLATE_PREFIX = "doc_template"
    GENERATED_DOC_PREFIX = "generated"
    TEST_PREFIX = "test"
    TEMP_PREFIX = "temp"
    # Extensions
    TEMPLATE_FILE_EXTENSION = "docx"
    GENERATED_DOC_EXTENSION = "pdf"
    HTML_EXTENSION = "html"
    JSON_EXTENSION = "json"
    ALLOWED_EXTENSIONS = [TEMPLATE_FILE_EXTENSION, ]


class RegexConstants:
    # General
    FIRST = r".\1"
    CYRILLIC_TEXT = r".*[а-яА-Я].*"
    # HTML regexes
    A_LINKS = r"<a id=.{0,50}<\/a>"
    ALL_TRS = r"<tr>.{0,30}{%tr.{0,100}<\/tr>"
    # Jinja template regexes
    ARRAY_FIELDS = r"\['(.{0,10})'\]"
    TEMPLATE_FORMULA = r"{{[\s\(]{0,2}([a-zA-Z\[\]\.]{1,50})[\}]{0,2}.{0,1}[\{]{0,2}.{0,30}}}"
    TEMPLATE_FILTER = r"{{.{0,50}[\-\+\*\|]{1}.{0,100}}}"
    FOR_LOOP_BEGIN_TAG = r"{%[a-z. \S ]{0,20} for [a-zA-Z . \S]{0,300}%}"
    TAG_EXTRACT = r"({%[a-z.  ]{0,20})"
    FOR_LOOP_END_TAG = r"{%.{0,10}endfor %}"
    FOR_LOOP_BODY = r"({%[a-z. \S]{0,20})(for)([a-zA-Z. \S]{0,300}%})"
    FOR_LOOP_CONDITION = r"[a-zA-Z.\s]{0,50}\s(for)\s([a-zA-Z. \S]{0,50})\sin\s([a-zA-Z.]{0,50})" #Order is importnant
    ALL_FOR_LOOP_BODY = r"({%[a-z. \S]{0,20}for[a-zA-Z .\S]{0,300}%})"
    TEXT_FIELD = r"{{ fields.TextField('\1') }}"


class HTMLConstants:
    # Jinja template constants
    IMPORT_FORM_FIELD_MACROS = '{% import "form_field_macros.html" as fields %}'
    BLOCK_TEMPLATE_CONTENT = '{% block template_content %}'
    END_BLOCK_TEMPLATE_CONTENT = '{% endblock template_content %}'

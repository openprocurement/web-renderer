import re
import mammoth
from flask import Flask
from app import app
from app.renderer import TemplateFile
from app.utils.utils import make_full_file_path, make_full_html_path, generate_file_name


class HTMLRenderer:

    def __init__(self, template_file):
        self.make_template_file(template_file)
        self.render_to_html()

    def make_template_file(self, template_file):
        file_name = make_full_file_path(template_file)
        with open(file_name, "rb") as file_object:
            self.template_file = file_object
            self.convert_to_html()

    def replace_regex(self):
        regex_to_replace_in_html = [
            [r"<a id=.{0,50}<\/a>", ""],
            [r"\['(.{0,10})'\]", r".\1"],
            [r"{{ {0,1}([a-zA-Z\[\]\.\']{1,50})(.{0,30})}}",
             r"{{ fields.TextField('\1') }}"],
            [r"<tr>.{0,30}{%tr.{0,100}<\/tr>", ""],
            [r"{% for.{0,300}{% endfor %}", ""],
            [r'{{.{0,50}[\-\+\*\|]{1}.{0,50}}}', ""]
        ]
        for row in regex_to_replace_in_html:
            self.formatted_html = re.sub(row[0], row[1], self.formatted_html)

    def add_header(self):
        html_header = """
        {% import "form_field_macros.html" as fields %}
        {% block template_content %}
        """
        html_footer = "{% endblock template_content %}"
        self.formatted_html = html_header + self.formatted_html + html_footer

    def convert_to_html(self):
        document = mammoth.convert_to_html(self.template_file)
        self.init_html = document.value
        self.formatted_html = self.init_html

    def encode_html(self):
        self.unicode_html = self.formatted_html.encode('utf8')

    def save_html(self):
        self.html_file_name = generate_file_name()
        self.html_file_full_path = make_full_html_path(self.html_file_name)
        with open(self.html_file_full_path, "wb") as fo:
            fo.write(self.unicode_html)

    def render_to_html(self):
        self.replace_regex()
        self.add_header()
        self.encode_html()
        self.save_html()

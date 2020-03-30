from flask import Flask
from app import app
import jinja2
from docxtpl import DocxTemplate
import re
from jinja2 import (
    Template,
    TemplateSyntaxError,
    TemplateError,
    meta,
    Environment,
    StrictUndefined,
)
from app.template_env.template_utils import(
    format_date,
    convert_amount_to_words,
    to_float,
)


class TemplateFormatter(object):

    @classmethod
    def format_date(cls, date):
        return format_date(date)

    @classmethod
    def convert_amount_to_words(cls, amount):
        return convert_amount_to_words(amount)

    @classmethod
    def to_float(cls, str_number):
        return to_float(str_number)

    def __get_method__(self, method_name):
        return getattr(self.__class__, method_name)


class JinjaEnvironment:

    def __init__(self, name="JinjaEnvironment"):
        self.name = name
        self.jinja_env = jinja2.Environment(undefined=StrictUndefined)
        self.get_formatter()
        self.get_all_functions()

    def get_formatter(self, name="TemplateFormatter"):
        formater_class = globals()[name]
        self.formatter = formater_class()

    def get_all_functions(self):
        all_funcs = [func for func in dir(TemplateFormatter) if callable(
            getattr(TemplateFormatter, func))]
        method_list = [func for func in all_funcs if not func.startswith("__")]
        for method in method_list:
            self.jinja_env.filters[method] = self.formatter.__get_method__(
                method)


class DocxTemplateLocal(DocxTemplate):

    def render_xml(self, src_xml, context, jinja_env=None):
        src_xml = src_xml.replace(r'<w:p>', '\n<w:p>')
        try:
            if jinja_env:
                template = jinja_env.from_string(src_xml)
            else:
                template = Template(src_xml)

            ast = jinja_env.parse(src_xml)
            unexpected = meta.find_undeclared_variables(ast)
            dst_xml = template.render(context)
        except TemplateError as exc:
            if hasattr(exc, 'lineno') and exc.lineno is not None:
                line_number = max(exc.lineno - 4, 0)
                exc.docx_context = map(lambda x: re.sub(r'<[^>]+>', '', x),
                                       src_xml.splitlines()[line_number:(line_number + 7)])

            raise exc
        dst_xml = dst_xml.replace('\n<w:p>', '<w:p>')
        dst_xml = (dst_xml
                   .replace('{_{', '{{')
                   .replace('}_}', '}}')
                   .replace('{_%', '{%')
                   .replace('%_}', '%}'))
        return dst_xml

    def search(self, regex):
        def search_paragraphs(regex):
            res_list = []
            for i in range(0, len(self.paragraphs)):
                if re.search(regex, self.paragraphs[i].text):
                    res_list.append(f"paragraph number={i} text={self.paragraphs[i].text}")
            return res_list
                 
        def search_cells(regex):
            res_list = []
            for table in self.tables:
                for row in table.rows:
                    for i in range(0, len(row.cells)):
                        if re.search(regex, row.cells[i].text):
                            res_list.append(f"cell number={i} text={row.cells[i].text}")
            return res_list
        
        result_list_p = search_paragraphs(regex)
        result_list_c = search_cells(regex)
        result_list = result_list_p + result_list_c
        print(result_list)

   
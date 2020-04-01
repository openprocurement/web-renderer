from flask import Flask
from docxtpl import DocxTemplate
import jinja2
from jinja2 import (
    Template,
    TemplateSyntaxError,
    TemplateError,
    meta,
    Environment,
    StrictUndefined,
)
import re
from app import app
from app.template_env.template_utils import(
    format_date,
    convert_amount_to_words,
    to_float,
)
from app.utils.utils import(
    process_jinja_undefined_var_error,
)


class TemplateFormatter(object):
    """
        The class that declare template functions.
    """
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
        self.set_template_formatter()
        self.set_template_functions()

    def set_template_formatter(self, name="TemplateFormatter"):
        formater_class = globals()[name]
        self.formatter = formater_class()

    def set_template_functions(self):
        all_funcs = [func for func in dir(TemplateFormatter) if callable(
            getattr(TemplateFormatter, func))]
        method_list = [func for func in all_funcs if not func.startswith("__")]
        for method in method_list:
            self.jinja_env.filters[method] = self.formatter.__get_method__(
                method)


class DocxTemplateLocal(DocxTemplate):

    def search(self, regex):
        """
            The method for searching a regex in the docx document.
        """
        def search_paragraphs(regex):
            res_list = []
            for i in range(0, len(self.paragraphs)):
                if re.search(regex, self.paragraphs[i].text):
                    res_list.append(
                        f'Paragraph #{i+1}:"{self.paragraphs[i].text}"')
            return res_list

        def search_cells(regex):
            res_list = set()
            for table in self.tables:
                for table_row in set(table.rows):
                    for cell_index in range(0, len(table_row.cells)):
                        if re.search(regex, table_row.cells[cell_index].text):
                            res_list.add(f"Table cell: {table_row.cells[cell_index].text}")
            return list(res_list)

        return search_paragraphs(regex) + search_cells(regex)

    def render_document(self, context):
        """
            Render docx document method with the special handling jinja2.exceptions.UndefinedError.
        """
        try:
            self.render(context, app.jinja_env_obj.jinja_env)
        except jinja2.exceptions.UndefinedError as error:
            process_jinja_undefined_var_error(self, error)

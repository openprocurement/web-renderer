import re
import jinja2
from docxtpl import DocxTemplate
from pathlib import Path

from flask import Flask
from app import app
from app.files import(
    TemplateFile,
)
from app.constants import (
    GeneralConstants,
)
from app.utils.utils import (
    is_file_empty,
)
from app.render_env.utils import (
    process_jinja_undefined_var_error,
)


class DocxTemplateLocal(DocxTemplate):

    def __init__(self, template_file :TemplateFile):
        self.template_file = TemplateFile.make_copy(template_file)
        filepath = Path(self.template_file.full_path)
        super().__init__(self.template_file.full_path)
        self.output_file_path = filepath.parent / f"output_{filepath.name}"

    def save(self, full_path=None):
        if full_path is None:
            super().save(self.output_file_path)

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
                            res_list.add(
                                f"Table cell: {table_row.cells[cell_index].text}")
            return list(res_list)

        return search_paragraphs(regex) + search_cells(regex)

    def render(self, context):
        """
            Render docx document method with the special handling jinja2.exceptions.UndefinedError.
        """
        for i in ["project_name", "number", "phase"]:
            if context.get(i):
                context[i] = f"<![CDATA[{context[i]}]]>"
        try:
            super().render(context, app.jinja_env_obj)
        except jinja2.exceptions.UndefinedError as error:
            process_jinja_undefined_var_error(self, error)

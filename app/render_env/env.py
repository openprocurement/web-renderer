import jinja2
from jinja2 import Environment, Template, TemplateError, TemplateSyntaxError, meta
from jinja2.runtime import Context, StrictUndefined

from flask import Flask
from app import app
from app.render_env.formatters import TemplateFormatter


class JinjaEnvironment (Environment):
    '''
    Our custom environment, which simply allows us to override the class-level
    valueues for the Template and Context classes used by jinja2 internally.
    '''
    
    def __init__(self):
        super().__init__(undefined=StrictUndefined)
        self.formatter = TemplateFormatter
        self.set_template_functions()
    
    def set_template_functions(self):
        """
            A function that sets all classmethods from the self.formatter as JinjaEnvironment filter. 
        """
        all_funcs = [func for func in dir(self.formatter) if callable(getattr(self.formatter, func))]
        method_list = [func for func in all_funcs if not func.startswith("__")]
        for method in method_list:
            self.filters[method] = self.formatter.__get_method__(method)
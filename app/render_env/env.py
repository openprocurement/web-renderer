import jinja2
from jinja2 import Environment, Template, TemplateError, TemplateSyntaxError, meta
from jinja2.runtime import Context, StrictUndefined

from flask import Flask
from app import app
from app.render_env.formatters import TemplateFormatter
from app.render_env.handlers import RenderUndefined, RenderMode


class RenderContext(Context):
    '''
    A custom context, which can be used for field filtering.
    It receives a value of each field in jinja template and checks.
    '''
    def __init__(self, *args, **kwargs):
        super(RenderContext, self).__init__(*args, **kwargs)
        self.skipped = False

    def _is_skipped(self, value):
        '''
            The function that check if value has '__skipped__' flag or not.
        '''
        if isinstance(value, dict):
            for key in value.keys():
                if self._is_skipped(value[key]):
                    return True
        elif isinstance(value, list):
            for item in value:
                if self._is_skipped(item):
                    return True
        elif isinstance(value, str) and hasattr(value, '__skipped__'):
            return True
        return False

    def _update_skipped(self, value):
        if value is not None and not self.skipped and self._is_skipped(value):
            self.skipped = True

    def resolve(self, key):
        '''
        The intercepted resolve(), which uses the helper above to set the
        internal flag whenever a skipped variable value is returned.
        '''
        value = super(RenderContext, self).resolve(key)
        self._update_skipped(value)
        return value

    def resolve_or_missing(self, key):
        value = super(RenderContext, self).resolve_or_missing(key)
        self._update_skipped(value)
        return value


class JinjaEnvironment (Environment):
    '''
    Our custom environment, which simply allows us to override the class-level
    values for the Template and Context classes used by jinja2 internally.
    '''
    context_class = RenderContext

    def __init__(self):
        self.undefined = RenderUndefined
        self.undefined.render_mode = RenderMode.SOFT # the error handling mode
        super().__init__(undefined=self.undefined)
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

    def getattr(self, obj, attribute):
        """
            Get an item or attribute of an object but prefer the attribute.
        """
        try:
            return getattr(obj, attribute)
        except AttributeError:
            pass
        try:
            return obj[attribute]
        except (TypeError, LookupError, AttributeError):
            return self.undefined(obj=obj, name=attribute)

import re
from jinja2.runtime import Undefined

from app.exceptions import UndefinedVariableJinja

# Error utils:

def process_jinja_undefined_var_error(docx_template, error):
    """
        The function for processing jinja2.exceptions.UndefinedError.
        It adds `possible_locations` ti
    """
    undefined_value = re.findall(
        "'[a-zA-Z ]*'", error.args[0])
    undefined_value_item = 1 if len(undefined_value) > 1 else 0
    undefined_value = undefined_value[undefined_value_item].replace(
        "'", "")
    error_message = {
        "jinja_error": error.args[0],
        "possible_locations": docx_template.search(undefined_value)
    }
    raise UndefinedVariableJinja(error_message)


def is_undefined(obj):
    """
    Check if the passed object is undefined.
    """
    return isinstance(obj, Undefined)


class Mock:
    default_value = ""

    def __call__(self, *args, **kwargs):
        return self.default_value

    def __repr__(self):
        return self.default_value

    def __str__(self):
        return self.default_value

    def __getattr__(self, attribute):
        # return self.default_value
        return self

    def __unicode__(self):
        return self.default_value

    def __nonzero__(self):
        return True

    def __len__(self):
        return 0

    def __iter__(self):
        yield self

    def __mul__(self, other):
        return self.default_value

    def __add__(self, other):
        return self.default_value

    def __sub__(self, other):
        return self.default_value

    def __div__(self, other):
        return self.default_value

    def __rmul__(self, other):
        return self.default_value

    def __radd__(self, other):
        return self.default_value

    def __rsub__(self, other):
        return self.default_value

    def __rdivmod__(self, other):
        return self.default_value

    def __rfloordiv__(self, other):
        return self.default_value

    def __rmod__(self, other):
        return self.default_value

    def __rdiv__(self, other):
        return self.default_value

    def __int__(self):
        return self.default_value

    def __float__(self):
        return self.default_value

    def __truediv__(self, other):
        return self.default_value

    def __rtruediv__(self, other):
        return self.default_value

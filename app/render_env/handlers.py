from jinja2.runtime import Context, StrictUndefined, Undefined
from jinja2.exceptions import UndefinedError
from jinja2.utils import internalcode
from enum import Enum
from app.render_env.utils import Mock


class RenderMode(Enum):
    """
        The mode specifies what the env should return when it is unable to look up a name or access an attribute.
        Modes:
        - STRICT:
            always return an Undefined object
        - SOFT:
            return the default value
    """
    STRICT = 1
    SOFT = 2

    def __str__(self):
        return self.name

    def apply(self, undefined):
        if self.name == str(self.STRICT):
            undefined.__call__ = undefined.raise_exception
            undefined.__getattr__ = undefined.raise_exception
        elif self.name == str(self.SOFT):
            undefined.__call__ = undefined._get_attr
            undefined.__getattr__ = undefined._get_attr
            undefined.__unicode__ = undefined.return_default
            undefined.__str__ = undefined.return_default


class RenderUndefined(StrictUndefined):
    '''
    A custom Undefined class, which returns further Undefined objects depending on the RenderMode specified.
    '''

    def __init__(self, hint=None, obj=None, name=None, exc=UndefinedError):
        super(StrictUndefined, self).__init__(hint, obj, name, exc)
        self.default_value = Mock() # the default value for the all template variables
        self.apply_mode()

    @internalcode
    def __repr__(self):
        return 'RenderUndefined'

    def _get_attr(self, attr):
        return self.default_value

    def return_default(self):
        """
            The method that handles an exception and returns the default value for the all template variables.
        """
        return str(self.default_value)

    def raise_exception(self):
        return self

    def apply_mode(self):
        self.render_mode.apply(self.__class__)

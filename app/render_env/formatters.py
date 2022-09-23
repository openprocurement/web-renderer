from app import app
from app.render_env.filters import (classification_filter, common_classification, common_classification_code,
                                    common_classification_description, convert_amount_to_words, default_filter,
                                    format_date, inline_image_filter, jmespath_filter, to_float,
                                    to_space_separated_float, to_space_separated_int, unit_shortcut_filter)
from docxtpl.inline_image import InlineImage


class TemplateFormatter:
    """
        The class that declare template functions.
    """
    @classmethod
    def format_date(cls, date):
        return format_date(date)

    @classmethod
    def to_money_numeral(cls, amount):
        return convert_amount_to_words(amount)

    @classmethod
    def to_float(cls, str_number):
        return to_float(str_number)

    @classmethod
    def to_space_separated_int(cls, number):
        return to_space_separated_int(number)

    @classmethod
    def to_money_number(cls, number):
        return to_space_separated_float(number)

    @classmethod
    def common_classification(cls, items):
        return common_classification(items)

    @classmethod
    def common_classification_code(cls, items):
        return common_classification_code(items)

    @classmethod
    def common_classification_description(cls, items):
        return common_classification_description(items)

    @classmethod
    def json_query(cls, data, search_string):
        return jmespath_filter(data, search_string)

    @classmethod
    def default(cls, data, default_value):
        return default_filter(data, default_value)

    @classmethod
    def __get_method__(cls, method_name):
        return getattr(cls, method_name)

    @classmethod
    def classification(cls, data):
        return classification_filter(data)

    @classmethod
    def unit_shortcut(cls, value):
        return unit_shortcut_filter(value)

    @classmethod
    def InlineImage(cls, value, width=None, height=None, ratio_size=None, unit='Mm'):
        result = inline_image_filter(value=value, width=width, height=height, ratio_size=ratio_size, unit=unit)
        if not isinstance(result, InlineImage):
            return ""
        return result

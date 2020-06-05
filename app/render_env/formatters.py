from app import app
from app.render_env.utils import (common_classification, common_classification_code,
                                            common_classification_description, convert_amount_to_words,
                                            format_date, to_float, to_space_separated_float,
                                            to_space_separated_int, jmespath_filter,
                                            )

class TemplateFormatter(object):
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
    def search(cls, data, search_string):
        return jmespath_filter(data, search_string)

    @classmethod
    def __get_method__(cls, method_name):
        return getattr(cls, method_name)

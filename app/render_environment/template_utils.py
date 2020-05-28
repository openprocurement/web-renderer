from datetime import datetime

import jmespath
from babel.dates import format_datetime
from flask import Flask
from num2words import num2words

from app import app
from app.utils.cpv import ClassificationTree

CPVTree = ClassificationTree()


class MoneyAmount:
    """
        class MoneyAmount:
            amount : unicode string, eg.: "12\xa0588\xa0575,00"
            float_amount: float value, eg.: 12588575.0
            amount_in words: string value, eg.: триста двадцять двi тисячi шiстсот шiстдесят дев'ять гривень 00 копійок
    """
    HRYVNIA_SUFFIX = 0
    KOPIYKA_SUFFIX = 1

    def __init__(self, amount):
        self.amount = amount
        self.amount_to_float()
        self.convert_amount_to_words()

    def amount_to_float(self):
        amount = self.amount
        amount = to_float(amount)
        self.float_amount = amount

    def get_str_currency(self, number, unit):
        suffixes = {
            0: ["гривень", "копійок"],
            1: ["гривня", "копійка"],
            2: ["гривні", "копійки"],
            2: ["гривні", "копійки"],
            5: ["гривень", "копійок"],
            6: ["гривень", "копійок"],
            7: ["гривень", "копійок"],
            8: ["гривень", "копійок"],
            9: ["гривень", "копійок"],
        }
        return suffixes[number][unit]

    def convert_fractial_part_to_words(self):
        fractial_part = int((self.float_amount % 1)*100)
        fractial_part_str = str(fractial_part) if len(
            str(fractial_part)) == 2 else "0" + str(fractial_part)
        unit_str = self.get_str_currency(
            fractial_part % 10, MoneyAmount.KOPIYKA_SUFFIX)
        return fractial_part_str + " " + unit_str

    def convert_integer_part_to_words(self):
        integer_part = int(self.float_amount)
        integer_part_str = num2words(integer_part, lang='uk')
        unit_str = self.get_str_currency(
            integer_part % 10, MoneyAmount.HRYVNIA_SUFFIX)
        return integer_part_str + " " + unit_str

    def convert_amount_to_words(self):
        integer_part = self.convert_integer_part_to_words()
        fractial_part = self.convert_fractial_part_to_words()
        self.amount_in_words = integer_part + " " + fractial_part


def convert_amount_to_words(amount):
    """
        The function for formatting an amount of money to the word string. 
    """
    money_amount = MoneyAmount(amount)
    return money_amount.amount_in_words


def format_date(data):
    """
        The function for formating an ISO date to the string one.
        input:
            date (ISO): 2019-08-22T13:35:00+03:00
        output:
            date (str): "22" серпня 2019 року
    """
    date_object = datetime.fromisoformat(data)
    str_date = format_datetime(date_object, '"d" MMMM Y року', locale='uk_UA')
    return str_date


def to_float(float_string):
    """
        A function for formatting comma float string to float.
        input: "12\xa0588\xa0575.00"
        output: 12588575.0
    """
    if (isinstance(float_string, int)):
        float_string=str(float_string)
    else:
        float_string = float_string.encode('ascii', 'ignore').decode("utf-8")
    float_string = float_string.replace(" ", "").replace(',', ".")
    float_string = float(float_string)
    return float_string


def to_space_separated(number, numbers_after_comma):
    """
        A function for formatting int or float number to the space separated one.
        input: 1234567.33
        output: 1 234 567.33
    """
    float_var = float(number)
    separated_number = '{:,.{}f}'.format(number, numbers_after_comma).replace(',', ' ').replace('.', ',')
    return separated_number


def to_space_separated_int(number):
    return to_space_separated(number, 0)

def to_space_separated_float(number):
    return to_space_separated(number, 2)


def _get_common_cpv(items):
    """
    An utility for getting common classification from list items with classification objects
    """
    ids = jmespath.search("[].classification.id", items)
    scheme = jmespath.search("[].classification.scheme", items)[0]
    scheme = f"{scheme}:2015" if scheme == "ДК021" else scheme
    cpv_id = CPVTree.get_common_cpv(ids)
    return scheme, CPVTree.get_cpv(cpv_id)


def common_classification(items):
    """
    An utility for formatting common classification in string format: [scheme] [id], [description], supported schema
    CPV and ДК021
    """
    scheme, cpv = _get_common_cpv(items)
    return f"{scheme} {cpv.cpv}, {cpv.description}" if cpv else ""


def common_classification_description(items):
    """
    An utility for getting common classification description
    """
    scheme, cpv = _get_common_cpv(items)
    return cpv.description if cpv else ""


def common_classification_code(items):
    """
    An utility for for formatting common classification code in format [scheme] [id], supported schema CPV and ДК021
    """
    scheme, cpv = _get_common_cpv(items)
    return f"{scheme} {cpv.cpv}" if cpv else ""

def jmespath_filter(data, search_string):
    """
    An utility for data filtering.
    Input:
        data - JSON data
        search_string - jmespath search string
    """
    return jmespath.search(search_string, data)
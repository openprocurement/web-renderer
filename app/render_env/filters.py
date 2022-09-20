from datetime import datetime

import jmespath
from app.constants import GeneralConstants
from app.decorators import ignore
from app.log import logger
from app.render_env.utils import Mock, download_image_by_url, is_undefined
from app.utils.cpv import ClassificationTree
from app.utils.utils import read_file
from babel.dates import format_datetime
from docx.shared import Cm, Emu, Inches, Mm, Pt
from docxtpl import InlineImage
from num2words import num2words
from num2words.lang_UK import Num2Word_UK
from PIL import Image  # https://pillow.readthedocs.io/en/4.3.x/

CPVTree = ClassificationTree()
units = read_file('data/all_units.yaml')
units.update(read_file('data/uk_pretty.yaml'))
converter = Num2Word_UK()

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
        self.amount_in_words = self.convert_amount_to_words()

    def amount_to_float(self):
        amount = self.amount
        amount = to_float(amount)
        self.float_amount = amount

    def get_str_currency(self, number, unit):
        suffixes = {
            0: ["гривень", "копійок"],
            1: ["гривня", "копійка"],
            11: ["гривень", "копійок"],
            2: ["гривні", "копійки"],
            3: ["гривні", "копійки"],
            4: ["гривні", "копійки"],
            5: ["гривень", "копійок"],
            6: ["гривень", "копійок"],
            7: ["гривень", "копійок"],
            8: ["гривень", "копійок"],
            9: ["гривень", "копійок"],
        }
        return suffixes[number][unit]

    def convert_fractial_part_to_words(self):
        fractial_part = int(round((self.float_amount % 1) * 100, 1))
        fractial_part_str = str(fractial_part) if len(str(fractial_part)) == 2 else "0" + str(fractial_part)
        if str(fractial_part)[-2:] == '11':
            unit_str = self.get_str_currency(11, MoneyAmount.KOPIYKA_SUFFIX)
        else:
            unit_str = self.get_str_currency(fractial_part % 10, MoneyAmount.KOPIYKA_SUFFIX)
        return f"{fractial_part_str} {unit_str}"

    def convert_integer_part_to_words(self):
        integer_part = int(self.float_amount)
        integer_part_str = converter._int2word(integer_part, feminine=True)
        if str(integer_part)[-2:] == '11':
            unit_str = self.get_str_currency(11, MoneyAmount.HRYVNIA_SUFFIX)
        else:
            unit_str = self.get_str_currency(integer_part % 10, MoneyAmount.HRYVNIA_SUFFIX)
        return f"{integer_part_str} {unit_str}"

    @ignore(exceptions=(ValueError,))
    def convert_amount_to_words(self):
        integer_part = self.convert_integer_part_to_words()
        fractial_part = self.convert_fractial_part_to_words()
        return integer_part + " " + fractial_part


def convert_amount_to_words(amount):
    """
        The function for formatting an amount of money to the word string.
    """
    money_amount = MoneyAmount(str(amount))
    return money_amount.amount_in_words


@ignore(exceptions=(ValueError, TypeError))
def format_date(data):
    """
        The function for formating an ISO date to the string one.
        input:
            date (ISO): 2019-08-22T13:35:00+03:00
        output:
            date (str): "22" серпня 2019 року
    """
    date_object = datetime.fromisoformat(data)
    return format_datetime(date_object, '"d" MMMM Y року', locale='uk_UA')


@ignore(exceptions=(ValueError,))
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


@ignore()
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


@ignore(exceptions=(TypeError), default_value=("", ""))
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

def jmespath_filter(data, json_query_string):
    """
    An utility for data filtering.
    Input:
        data - JSON data
        json_query_string - jmespath search string
    """
    return jmespath.search(json_query_string, data)

def default_filter(var, default=''):
    """
    An utility for returning the default value.
    """
    if is_undefined(var) or var == "" or isinstance(var, Mock):
        return default
    return var

@ignore()
def classification_filter(cpv_data):
    cpv_id = cpv_data.get('id', '')
    if not cpv_id:
        return ""

    cpv = CPVTree.get_cpv(cpv_id)
    return f"{cpv.description}"


def unit_shortcut_filter(value):
    """
    An utility for getting shortcut for measurement units
    """
    result = units.get(value, {}).get('symbol', '') or units.get(value, {}).get('name', '')
    if not result:
        logger.warning(f"Received unknown unit code: {value}",
        extra={'MESSAGE_ID': 'unknown_unit_code', 'unit_code': value})
    return result


def inline_image_filter(value, width, height, ratio_size, unit):
    units = {
        "mm": Mm,
        "cm": Cm,
        "pt": Pt,
        "emu": Emu,
        "inches": Inches,
    }

    path_to_image, image_name, side = download_image_by_url(value, ratio_size)

    if side and ratio_size:
        if side == 'width':
            width = ratio_size
            height = None
        else:
            height = ratio_size
            width = None

    unit_klass = units.get(unit.lower(), Mm)
    try:
        if isinstance(width, str):
            width = width.replace(',', '.')
        unit_w = unit_klass(float(width))
    except TypeError:
        unit_w = None
    try:
        if isinstance(height, str):
            height = height.replace(',', '.')
        unit_h = unit_klass(float(height))
    except TypeError:
        unit_h = None

    if path_to_image:
        value = InlineImage(GeneralConstants.DOCX_TEMPLATE, path_to_image, width=unit_w, height=unit_h)
    return value

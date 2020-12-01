import json
from unittest.mock import patch

import io
from PIL import Image
from docxtpl import InlineImage

from app.render_env.filters import (classification_filter, common_classification, common_classification_code,
                                    common_classification_description, convert_amount_to_words, unit_shortcut_filter,
                                    inline_image_filter)
from tests.utils import create_one_pargraph_docx, process_response_document
from .base import test_json_data
from .conftest import BaseTest


class TestCommonClassification:

    def test_common_classification_code(self, items):
        result = common_classification_code(items)
        assert result == 'ДК021:2015 22400000-4'

    def test_common_classification_description(self, items):
        result = common_classification_description(items)
        assert result == "Марки, чекові бланки, банкноти, сертифікати акцій, рекламні матеріали, каталоги та посібники"

    def test_common_classification(self, items):
        result = common_classification(items)
        assert result == "ДК021:2015 22400000-4, Марки, чекові бланки, банкноти, сертифікати акцій, рекламні " \
            "матеріали, каталоги та посібники"

    def test_common_classification_code_invalid_items(self, items):
        items.append({
            "id": "1b5d73b21cdb483494d68d09ccf5199a",
            "description": "Сільськогосподарська, фермерська продукція,",
            "classification": {
                "id": "03000000-1",
                "scheme": "ДК021",
                "description": "Сільськогосподарська, фермерська продукція, продукція рибальства, лісівництва та "
                "супутня продукція"
            },
            "quantity": 1
        })
        result = common_classification_code(items)
        assert result == ""

    def test_common_classification_description_invalid_items(self, items):
        items.append({
            "id": "1b5d73b21cdb483494d68d09ccf5199a",
            "description": "Сільськогосподарська, фермерська продукція,",
            "classification": {
                "id": "03000000-1",
                "scheme": "ДК021",
                "description": "Сільськогосподарська, фермерська продукція, продукція рибальства, лісівництва та "
                "супутня продукція"
            },
            "quantity": 1
        })
        result = common_classification_description(items)
        assert result == ""

    def test_common_classification_invalid_items(self, items):
        items.append({
            "id": "1b5d73b21cdb483494d68d09ccf5199a",
            "description": "Сільськогосподарська, фермерська продукція,",
            "classification": {
                "id": "03000000-1",
                "scheme": "ДК021",
                "description": "Сільськогосподарська, фермерська продукція, продукція рибальства, лісівництва та "
                "супутня продукція"
            },
            "quantity": 1
        })
        result = common_classification(items)
        assert result == ""

    def test_classification(self):
        classification_data = {
            'id': '72212411-3',
            'description': 'Послуги з розробки програмного забезпечення для управління інвестиціями',
            'scheme': 'ДК021'
        }

        result = classification_filter({})
        assert result == ''

        result = classification_filter(classification_data)
        assert result == classification_data["description"]

        description = classification_data.pop('description')
        classification_data['description'] = 'Invalid description'
        result = classification_filter(classification_data)
        assert result == description


class TestDataFilters(BaseTest):

    def test_jmespath_filter(self):
        # Form data
        contract_supplier_id = test_json_data['contract']['supplier']['id']
        docx_document, docx_storage_object = create_one_pargraph_docx(
            "{{ contract.supplier | json_query ('id')}}")
        # Post data
        response = self.app.post(
            "/",
            data={"template": docx_storage_object,
                  'json_data': json.dumps(test_json_data)},
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/pdf")

        # Process response pdf document and extract the content
        response_document_path, response_document_content = process_response_document(response)

        # Check  results
        self.assertEqual(contract_supplier_id, response_document_content)


    def test_default_filter(self):
        # Form data
        default_value = "new"
        docx_document, docx_storage_object = create_one_pargraph_docx(f'{{{{ contract.supplier.new | default ("{default_value}")}}}}')
        # Post data
        response = self.app.post(
            "/",
            data={"template": docx_storage_object,
                  'json_data': json.dumps(test_json_data)},
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/pdf")

        # Process response pdf document and extract the content
        response_document_path, response_document_content = process_response_document(
            response)

        # Check  results
        self.assertEqual(default_value, response_document_content)


class TestMoneyAmount:

    def test_convert_amount_to_words(self):
        test_values = {
            111.11: 'сто одинадцять гривень 11 копійок',
            1.01: 'одна гривня 01 копійка',
            10011.00: 'десять тисяч одинадцять гривень 00 копійок',
            '0.09': 'нуль гривень 09 копійок',
            '3': 'три гривні 00 копійок'
        }
        for amount, result in test_values.items():
            assert result == convert_amount_to_words(amount)


class TestUnits:

    def test_unit_shortcut(self):
        result = unit_shortcut_filter('MLT')
        assert result == 'мл.'

        result = unit_shortcut_filter('RO')
        assert result == 'Рулон'

        result = unit_shortcut_filter('2R')
        assert result == 'kCi'

        result = unit_shortcut_filter('2W')
        assert result == 'bin'

        result = unit_shortcut_filter(None)
        assert result == ''


class TestInlineImageFilter:
    @patch('app.render_env.utils.requests.get')
    def test_inline_image_filter(self, mock_get):
        mock_get.return_value.status_code = 200
        headers = {'Content-Type': 'image/png'}
        mock_get.return_value.headers = headers

        byte_img_io = io.BytesIO()
        byte_img = Image.open("tests/assets/test.png")
        byte_img.save(byte_img_io, "PNG")
        byte_img_io.seek(0)
        byte_img = byte_img_io.read()
        mock_get.return_value.content = byte_img
        
        image_url = "https://openthread.google.cn/images/ot-contrib-google.png"

        result = inline_image_filter(image_url, 50, 50, 'Inches')
        assert True == isinstance(result, InlineImage)
        assert 45720000 == result.width
        assert 45720000 == result.height

        result = inline_image_filter(image_url, 50, 50, 'Cm')
        assert True == isinstance(result, InlineImage)
        assert 18000000 == result.width
        assert 18000000 == result.height

        result = inline_image_filter(image_url, 50, 50, 'Mm')
        assert True == isinstance(result, InlineImage)
        assert 1800000 == result.width
        assert 1800000 == result.height

        result = inline_image_filter(image_url, 50, 50, 'Pt')
        assert True == isinstance(result, InlineImage)
        assert 635000 == result.width
        assert 635000 == result.height

        result = inline_image_filter(image_url, 50, 50, 'Emu')
        assert True == isinstance(result, InlineImage)
        assert 50 == result.width
        assert 50 == result.height

        result = inline_image_filter(image_url, "50", "60", 'Emu')
        assert True == isinstance(result, InlineImage)
        assert 50 == result.width
        assert 60 == result.height

        result = inline_image_filter(image_url, None, "60", 'Emu')
        assert True == isinstance(result, InlineImage)
        assert 60 == result.height
        assert None == result.width

        image_url = "https://openthread.google.cn/images/oaaaaaaaaaaa"
        mock_get.return_value.status_code = 400
        result = inline_image_filter(image_url, None, None, 'Mm')
        assert result == image_url

        image_url = 123
        result = inline_image_filter(image_url, 50, 50, 'Mm')
        assert result == image_url

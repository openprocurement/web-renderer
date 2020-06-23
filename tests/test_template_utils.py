import json

from tests.utils import create_one_pargraph_docx, process_response_document

import pdfplumber
from app.files import DocxFile, FileStorageObject
from app.render_env.filters import (convert_amount_to_words, common_classification, common_classification_code,
                                    common_classification_description)
from app.utils.utils import remove_file
from config import Config

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
            111.11: 'сто одинадцять гривень одинадцять копійок',
            1.01: 'одна гривня одна копійка',
            10011.00: 'десять тисяч одинадцять гривень нуль копійок',
            '0.09': 'нуль гривень дев\'ять копійок'
        }
        for amount, result in test_values.items():
            assert result == convert_amount_to_words(amount)

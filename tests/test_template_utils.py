import json
import pdfplumber

from .conftest import BaseTest
from config import Config
from .base import (
    test_json_data,
)
from app.render_environment.template_utils import (common_classification, common_classification_code,
                                                   common_classification_description)
from app.files import (
    FileStorageObject,
    DocxFile,
)
from app.utils.utils import(
    FileManager,
)

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
        # Creating the docx file with the content
        docx_document = DocxFile(folder=Config.TESTS_TEMP_FOLDER)
        docx_document.add_paragraph("{{ contract.supplier | search ('id')}}")
        docx_document.save()
        contract_supplier_id = test_json_data['contract']['supplier']['id']

        # Form data and post it 
        docx_storage_object = FileStorageObject(docx_document.path, docx_document.full_name, "application/msword")
        response = self.app.post(
            "/",
            data={"template": docx_storage_object, 'json_data': json.dumps(test_json_data)},
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        # self.assertEqual(response.json, {})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/pdf")
        
        # Save generated pdf document
        pdf_document_path = docx_document.name +".pdf"
        stream = response.get_data()
        f = open(pdf_document_path, 'wb')
        f.write(stream)
        f.close()

        # Read pdf document and extract the content
        pdf = pdfplumber.open(pdf_document_path)
        page = pdf.pages[0]
        text = page.extract_text()
        pdf.close()

        # Check  results
        result = repr(text).replace("'","")
        self.assertEqual(contract_supplier_id, result)
        
        # Remove all files
        FileManager.remove_file(docx_document.path)
        FileManager.remove_file(pdf_document_path)

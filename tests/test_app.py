
import json

from .conftest import BaseTest
from config import Config
from .base import (
    test_json_data,
)
from app.files import (
    FileStorageObject,
    DocxFile,
)
from app.utils.utils import(
    remove_file,
)

class TestDataFilters(BaseTest):

    def test_root(self):
        response = self.app.get('/')
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "text/html; charset=utf-8")

    def test_not_found(self):
        response = self.app.post(
            "/",
            data={"json_data": {}},
            content_type="multipart/form-data"
        )
        self.assertEqual(response.status, "404 NOT FOUND")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json, {'error': {'code': 404, 'message': 'Template file is not found'}})
        
        docx_document = DocxFile(folder=Config.TESTS_TEMP_FOLDER)
        docx_document.save()
        docx_storage_object = FileStorageObject(docx_document.path, docx_document.name, "application/msword")
        response = self.app.post(
            "/",
            data={"template": docx_storage_object},
            content_type="multipart/form-data"
        )
        self.assertEqual(response.status, "404 NOT FOUND")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json, {'error': {'code': 404, 'message': 'JSON data is not found'}})

    def test_empties(self):
        docx_document = DocxFile(folder=Config.TESTS_TEMP_FOLDER)
        docx_document.save()
        docx_storage_object = FileStorageObject(docx_document.path, docx_document.full_name, "application/msword")
        response = self.app.post(
            "/",
            data={"template": docx_storage_object, 'json_data': json.dumps(test_json_data)},
            content_type="multipart/form-data"
        )
        self.assertEqual(response.status, "422 UNPROCESSABLE ENTITY")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json, {'error': {'code': 422, 'message': 'Template is empty'}})


    def test_response_format(self):
        docx_document = DocxFile(folder=Config.TESTS_TEMP_FOLDER)
        docx_document.add_paragraph('hello')
        docx_document.save()
        docx_storage_object = FileStorageObject(docx_document.path, docx_document.full_name, "application/msword")
        response = self.app.post(
            "/",
            data={"template": docx_storage_object, 'json_data': json.dumps(test_json_data)},
            content_type="multipart/form-data"
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/pdf")

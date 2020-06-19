import pytest
import unittest
from os.path import join, dirname, realpath

from app import app
from app.utils.utils import remove_temp
from config import Config

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def items():
    data = [
        {
            "id": "e9d1078e651f4fb1822d5735bf70c4bd",
            "description": "Папір із водяними знаками",
            "classification": {
                "id": "22420000-0",
                "description": "Папір із водяними знаками",
                "scheme": "ДК021"
            },
            "quantity": 5
        },
        {
            "id": "b59025d16c02417baad247da44093572",
            "description": "Банкноти номіналом 1000 грн.",
            "classification": {
                "id": "22430000-3",
                "description": "Банкноти",
                "scheme": "ДК021"
            },
            "quantity": 1000000
        },
        {
            "id": "b59025d16c02417baad247da44093572",
            "description": "Банкноти номіналом 1000 грн.",
            "classification": {
                "id": "22412000-1",
                "description": "Нові марки",
                "scheme": "ДК021"
            },
            "quantity": 1000
        }
    ]
    return data


class BaseTest(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()


    def tearDown(self):
        temp_folder = dirname(realpath(__file__))+"/"+Config.TEMP_FOLDER
        remove_temp(temp_folder=temp_folder)
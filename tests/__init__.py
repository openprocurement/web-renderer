import os
from config import Config

if not os.path.exists(Config.TESTS_TEMP_FOLDER):
        os.makedirs(Config.TESTS_TEMP_FOLDER, exist_ok=True)
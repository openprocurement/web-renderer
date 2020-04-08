from bs4 import ResultSet, element as Element, BeautifulSoup, NavigableString
import re
import mammoth
import subprocess
from copy import deepcopy
from app.exceptions import (
	DocumentConvertionError,
)
from app.constants import (
	GeneralConstants,
)
from app.constants import RegexConstants


class GeneralConverter:

	@classmethod
	def convert_to_pdf(cls, full_file_path, timeout=None):
		args = ['libreoffice', '--headless', '--convert-to',
				'pdf', '--outdir', GeneralConstants.UPLOAD_FOLDER, full_file_path]
		try:
			process = subprocess.run(args, stdout=subprocess.PIPE,
									 stderr=subprocess.PIPE, timeout=timeout)
		except FileNotFoundError as e:
			raise DocumentConvertionError()

	@classmethod
	def convert_to_html(cls, template_file):
		document = mammoth.convert_to_html(template_file)
		return document
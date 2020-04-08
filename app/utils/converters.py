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


class BSToJSONConverter:
	"""
	A class that converts beautiful soup object to json schema.
	"""

	def make_json(self, tags, L=None):
		"""
				Input:
						tags - beautiful soup result set
				Ouptut:
						converted_list - jsonified set
		"""
		converted_list = []
		if type(tags) == ResultSet:
			for element_object in tags:
				converted_list.append(self.jsonify(element_object))
			return converted_list

	def form_json_tree(self, json, tag_keys, tags):
		"""
				Function for structuring tags by group.
		"""
		for key in set(tag_keys):
			grouped_tags = []
			for element in tags:
				for element_key, element_value in element.items():
					if element_key == key and element_value:
						grouped_tags.append(element_value)
			if grouped_tags:
				if len(grouped_tags) > 1:
					json[key] = grouped_tags
				else:
					json[key] = grouped_tags[0]
		return json

	def jsonify(self, element_object=None, json={}):
		"""
				Function that jsonify a tag.
				Input: tag
				Output: {'attributes': # all tag atributes,
								 #tag_name: { # the same structure}}
		"""
		if isinstance(element_object, Element.Tag):
			json[element_object.name] = {'attributes': element_object.attrs}
			if len(element_object.contents):
				json[element_object.name] = self.jsonify(
					element_object.contents, json[element_object.name])
			return json[element_object.name]

		elif len(element_object):
			tags = []
			tag_keys = []
			for element in element_object:
				if type(element) == Element.Tag:
					value = self.jsonify(element, json)
					tags.append({element.name: value})
					tag_keys.append(element.name)
				else:
					json['text'] = element.strip()
			if len(tag_keys) > 0:
				return self.form_json_tree(json, tag_keys, tags)
			return json
		else:
			return


class HTMLToJSONConverter(BSToJSONConverter):

	TO_INPUT_FIELDS = {"p": RegexConstants.TEMPLATE_FORMULA}
	INPUT_FIELD = "input"

	def replace_tags_to_new(self, soup, tags_to_replace_dict, new_tag_name):
		"""
				Function that find all tags that match regex and replace them with new tags.
				Input:
						soup: Beautiful soup object
						tags_to_replace_dict: dict with the format {"tag_name": tag_regex}
						new_tag_name: tag name that will be assigned
				Output:
						soup: Dynamically changed soup
		"""
		for tag, tag_text_regex in tags_to_replace_dict.items():
			tags_to_replace = soup.find_all(
				tag, text=re.compile(tag_text_regex))
			# Replacing tags
			for tag in tags_to_replace:
				tag_text = tag.find_next(string=True)
				id_list = re.findall(re.compile(tag_text_regex), tag_text)
				# Merge all new tags into temp tag
				new_tag_list = soup.new_tag(GeneralConstants.TEMP_PREFIX)
				for id in id_list:
					new_tag = soup.new_tag(new_tag_name, id=id, label=id)
					new_tag_list.append(new_tag)
				tag.replace_with(new_tag_list)
			# Removing temp tag
			temps = soup.find_all(GeneralConstants.TEMP_PREFIX)
			for temp in temps:
				temp.unwrap()
			return soup

	def create_for_loop_structure(self, current_tag, end_tag, tags, json=None):
		"""
				Recursive function for creating jinja template 'for' loop structure.
				It processes all tags in for loops and create these tags inheritance, 
				they are represented with the new form tag.
				Input: all_tags
				Output: 
				{"for_loop_name": {
						"name": for_loop_name,
						"old_tag": old_tag,
						"new_tag": generated_form,
						"tag_in_form 1": tag 1 in for loop body
						"tag_in_form 2..N": tag in for loop body
				}
		"""
		while current_tag != end_tag:
			if current_tag is None:
				return
			current_tag = current_tag.find_next("p")
			if current_tag.contents == [end_tag]:
				break
			if isinstance(current_tag, Element.Tag):
				current_tag_str = str(current_tag)
				current_text = current_tag.contents[0]
				tags.append(current_tag)
				if (re.match(RegexConstants.FOR_LOOP_END_TAG, str(current_text))):
					return current_tag
				elif (re.match(RegexConstants.FOR_LOOP_BEGIN_TAG, str(current_text))):
					new_tag = self.soup.new_tag("form", id=current_text)
					if "new_tag" in json:
						json["new_tag"].append(new_tag)
					json[current_tag_str] = {
						"name": current_text,
						"tag": current_tag,
						"new_tag": new_tag
					}
					current_tag = self.create_for_loop_structure(
						current_tag, end_tag, tags, json[current_tag_str])
				else:
					cur_tag = deepcopy(current_tag)
					json[current_tag_str] = {"tag": cur_tag}
					json["new_tag"].append(cur_tag)
		return

	def replace_template_loops_with_form(self, soup):
		"""
				Function for replacing jinja template 'for' loops with 'for' forms.
		"""
		for_tags = soup.find_all(
			"p", text=re.compile(RegexConstants.FOR_LOOP_BODY))
		if len(for_tags):
			end_tag = for_tags[-1].next_element
			current_tag = for_tags[0].previous_element
			loop_json_dict = {}
			tags = [end_tag]
			self.create_for_loop_structure(current_tag, end_tag, tags, loop_json_dict)
			for key, value in loop_json_dict.items():
				value["tag"].previous_element.replace_with(
					value["new_tag"])
			for tag in tags:
				tag.previous_element.extract()

	def remove_empty_tags(self, soup):
		"""
				Function for removing tags that have no content.
		"""
		for x in soup.find_all():
			if len(x.get_text(strip=True)) == 0:
				x.extract()

	def convert(self, formatted_html):
		"""
			Function that converts HTML to JSON schema.
		"""
		self.soup = BeautifulSoup(formatted_html, "html.parser")
		self.replace_template_loops_with_form(self.soup)
		self.remove_empty_tags(self.soup)
		self.soup = self.replace_tags_to_new(
			self.soup, HTMLToJSONConverter.TO_INPUT_FIELDS, HTMLToJSONConverter.INPUT_FIELD)
		root_tags = self.soup.find_all(recursive=False)
		json = self.make_json(root_tags)
		return json

import json
from bs4 import BeautifulSoup
import re
from copy import deepcopy
from app.constants import (
    RegexConstants,
)
from app.utils.utils import (
    Regex,
    JSONSchemaGeneratorContextManager,
    JSONListGeneratorContextManager,
)


class HTMLToJSONSchemaConverter:

    TEMPLATE_FORMULAS = [("p", '|'.join([RegexConstants.TEMPLATE_FORMULA, RegexConstants.FOR_LOOP_BODY, ]))
                         ]
    BLACK_LIST_VARIABLES = [r'loop.*']

    def find_all_fields(self, tags_to_find):
        """
            The function for finding all tags that match regex.
            Input:
                - tags_to_find - list of touples: [("tag","tag_regex"), ...]
            Output:
                - found_tag_list - found tags
        """
        found_tag_list = []
        for tag, tag_text_regex in tags_to_find:
            found_tags = self.soup.find_all(tag, text=re.compile(tag_text_regex))
            for tag in found_tags:
                tag_text = tag.find_next(string=True)
                id_list = [''.join(id) for id in re.findall(re.compile(tag_text_regex), tag_text)]
                found_tag_list.extend((id_list))
        return found_tag_list

    def make_tag_trees(self, found_tag_list):
        self.make_tag_list_tree(found_tag_list)
        self.make_tag_json_tree(found_tag_list)  # it depends on the list tree

    def make_tag_list_tree(self, found_tag_list):
        """
            The function for making a list tree from the list of tags.
            Input: [list of tags]
            Output: structurized list, eg.:["tag",["tag1","tag2"]].
        """
        generator = (tag for tag in found_tag_list)
        list_tree = []
        self.list_tree = self.make_list_tree(generator, list_tree)

    def make_tag_json_tree(self, found_tag_list):
        """
            The function for making a json tree from the list tree.
            Input: ["tag",["tag1","tag2"]]
            Output: structurized json:
            {
            "title": "tree",
            "type": "object",
            "properties": {
                # content
                }
            }
        """
        generator = (tag for tag in self.list_tree)
        json_tree = JSONSchemaObject("tree")
        self.json_tree_object = self.make_json_tree(generator, json_tree)
        self.json_tree = json.loads(repr(self.json_tree_object))

    def make_list_tree(self, generator, tree):
        """
            The recursive function that iterates a generator and creates a list structure depending on conditions.
            Here the conditions are as follows:
                - if a loop found, the function makes a body of it nested.
            Input:
                - [list of tags] as generator object,
                - tree - object that stores a list.
            Output:
                - structurized list, eg.:["tag",["tag1","tag2"]].
                For the for loop, it returns the following structure:
                    [("for", "for_loop_variable", "loop_iterated_list"), "tag1", ...]
        """
        for decorator in JSONListGeneratorContextManager(generator):
            current = decorator.current
            if re.match(RegexConstants.FOR_LOOP_BEGIN_TAG, current):
                # returns ("for", "loop_variable", "loop_iterated_list"):
                for_loop = [re.findall(RegexConstants.FOR_LOOP_CONDITION, current)[0]]
                tree.append(for_loop)
                self.make_list_tree(generator, for_loop)
            elif re.match(RegexConstants.FOR_LOOP_END_TAG, current):
                return
            else:
                if len(tree) and isinstance(tree[decorator.FOR_LOOP_CONDITION], tuple):
                    current = Regex.remove_prefix(tree[decorator.FOR_LOOP_CONDITION][decorator.ITERATOR], current)
                if not Regex.does_strings_matches_regex(HTMLToJSONSchemaConverter.BLACK_LIST_VARIABLES, current):
                    tree.append(current)
        return tree

    def make_json_tree(self, generator, tree):
        """
            The recursive function that iterates a generator and creates a JSON schema object structure depending on conditions.
            Here the conditions are as follows:
                - if the loop found, the function makes a body of it nested - JSONSchemaArray Object.
                - if the string object found, it creates a StringField.
            Input:
                - structurized list, eg.:["tag",["tag1","tag2"]] as generator object.
                - tree that stores a JSONSchemaObject object.
            Ouput:
                - JSONSchemaObject (BaseJSONSchemaField, ..., JSONSchemaArray)
        """
        for decorator in JSONSchemaGeneratorContextManager(generator):
            current = decorator.current
            if isinstance(current, str):
                # TODO Add field classifier that returns a BaseJSONSchemaField nested object based on current type.
                object_json = StringField(current)
                tree.properties[current] = object_json
            elif isinstance(current, list):
                # extracts FOR_LOOP_ITERATED_LIST from ("for", "for_loop_variable", "loop_iterated_list") tuple:
                name = current[decorator.FOR_LOOP_CONDITION][decorator.FOR_LOOP_ITERATED_LIST]
                tree.properties[name] = JSONSchemaArray(name)
                object_generator = (tag for tag in current[decorator.FOR_LOOP_CONDITION + 1:])
                self.make_json_tree(object_generator, tree.properties[name].items)
        return tree

    def convert(self, formatted_html):
        """
            A function that converts HTML to JSON schema.
        """
        self.soup = BeautifulSoup(formatted_html, "html.parser")
        found_tags = self.find_all_fields(HTMLToJSONSchemaConverter.TEMPLATE_FORMULAS)
        self.make_tag_trees(found_tags)
        return self.json_tree


# JSON Schema Wrappers:

class BaseJSONSchemaWrapper:

    def __init__(self, name, wrapper_type, title=None):
        self.name = name
        self.title = title if title is not None else name
        self.type = wrapper_type

    def __repr__(self):
        """
            A function that reprs objects to desired structure.
        """
        dictionary = deepcopy(self.__dict__)
        dictionary.pop('name')
        for key, value in dictionary.items():
            if not isinstance(value, (str, int, bool)):
                dictionary[key] = self.repr_elements(dictionary[key])
        return json.dumps(dictionary)

    def repr_elements(self, elements):
        """
            A function that reprs complex nested elemtnts.
        """
        json_elements = {}
        if isinstance(elements, list):
            for element in elements:
                json_element = json.loads(repr(element))
                for key, value in json_element.items():
                    json_elements[key] = json_element[key]
        elif isinstance(elements, BaseJSONSchemaWrapper):
            json_element = json.dumps(repr(elements))
            # json.loads has a bug that returns a str object after the first calling of the function.
            json_element = json.loads(json.loads(json_element))
            for key, value in json_element.items():
                json_elements = json_element[key]
        else:
            # for JSON compatibility, converts from the str dict as "{'key':"name"}"" with simple quotes to str dict with double quotes.
            current_element = repr(elements).replace("'", '"')
            json_elements = json.loads(current_element)
        return json_elements


# JSON Schema Objects:


class JSONSchemaObject(BaseJSONSchemaWrapper):

    def __init__(self, name, title=None, properties=None):
        super().__init__(name, "object", title)
        self.properties = properties if properties is not None else {}


class JSONSchemaArray(BaseJSONSchemaWrapper):

    def __init__(self, name, title=None, items=None):
        super().__init__(name, "array", title)
        self.items = JSONSchemaObject("items", name, items)


# JSON Schema Fields

class BaseJSONSchemaField:

    def __init__(self, name, field_type, title=None, description=None, required=False):
        self.name = name
        self.type = field_type
        self.title = title if title is not None else name
        self.description = description if description is not None else ""

    def __repr__(self):
        dictionary = deepcopy(self.__dict__)
        dictionary.pop('name')
        return json.dumps(dictionary)


class StringField(BaseJSONSchemaField):

    def __init__(self, name, title=None, description=None, min_length=5, max_length=100, required=False):
        super().__init__(name, "string", title, description, required)
        self.minLength = min_length
        self.maxLength = max_length


class DateField(BaseJSONSchemaField):

    def __init__(self, name, title=None, description=None, required=False):
        super().__init__(name, "string", title, description, required)
        self.format = "date"


class BooleanField(BaseJSONSchemaField):

    def __init__(self, name, title=None, description=None, required=False):
        super().__init__(name, "boolean", title, description, required)


class IntegerField(BaseJSONSchemaField):

    def __init__(self, name, title=None, description=None, minimum=1, maximum=30, required=False):
        super().__init__(name, "integer", title, description, required)
        self.minimum = minimum
        self.maximum = maximum

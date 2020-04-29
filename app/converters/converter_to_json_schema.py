import app
import json
from bs4 import BeautifulSoup
import re
from copy import deepcopy
from app.constants import (
    RegexConstants,
)
from app.utils.utils import (
    Regex,
    JSONListGeneratorContextManager,
    setdefaultattr,
)

HIDE_EMPTY_FIELDS = 0


class HTMLToJSONSchemaConverter:

    # regex that finds all tags <p> with the template formula: {{ name }} or the for loop body content {% for name in list %}
    TEMPLATE_FORMULAS = [("p", '|'.join([RegexConstants.TEMPLATE_FORMULA, RegexConstants.FOR_LOOP_BODY, ]))
                         ]
    BLACK_LIST_VARIABLES = [r'loop.*']

    def __init__(self, hide_empty_fields):
        self.hide_empty_fields = hide_empty_fields
        global HIDE_EMPTY_FIELDS
        HIDE_EMPTY_FIELDS = self.hide_empty_fields

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
            found_tags = self.soup.find_all(
                tag, text=re.compile(tag_text_regex))
            for tag in found_tags:
                tag_text = tag.find_next(string=True)
                id_list = [''.join(id) for id in re.findall(
                    re.compile(tag_text_regex), tag_text)]
                found_tag_list.extend((id_list))
        return found_tag_list

    def make_tag_list_tree(self, found_tag_list):
        """
            The function for making a list tree from the list of tags.
            Input: [list of tags]
            Output: structurized list, eg.:["tag",["tag1","tag2"]].
        """
        generator = (tag for tag in found_tag_list)
        list_tree = []
        json_tree = JSONSchemaObject("tree")
        self.list_tree, self.json_tree_object = self.make_list_tree(
            generator, list_tree, json_tree)
        self.json_tree = json.loads(repr(self.json_tree_object))["properties"]

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
        self.json_tree = json.loads(repr(self.json_tree_object))["properties"]

    def make_list_tree(self, generator, tree, json_tree):
        """
            The recursive function that iterates a generator and creates a list structure depending on conditions.
            Here the conditions are as follows:
                - if a loop found, the function makes a body of it nested.
            Input:
                - [list of tags] as a generator object,
                - tree - an object that stores a list.
                - json_tree - a resulted json_tree object.
            Output:
                - structurized list, eg.:["field1",["field2","field2"]].
                    For the for loop, it returns the following structure:
                        [("for", "for_loop_variable", "loop_iterated_list"), #fields]
                - structurized json:
                    {
                    "title": "tree",
                    "type": "object",
                    "properties": {
                        # content
                        }
                    }
        """
        for decorator in JSONListGeneratorContextManager(generator):
            current = decorator.current
            if re.match(RegexConstants.FOR_LOOP_BEGIN_TAG, current):
                tree, json_tree, for_loop = self.create_for_loop_nesting(decorator, current, tree, json_tree)
                self.make_list_tree(generator, for_loop, json_tree)
            elif re.match(RegexConstants.FOR_LOOP_END_TAG, current):
                return
            else:
                current = self.change_loop_items_name(decorator, current, tree)
                if not Regex.does_strings_matches_regex(HTMLToJSONSchemaConverter.BLACK_LIST_VARIABLES, current):
                    tree.append(current)
                    #TODO add compatibility to other fields except String.
                    self.set_json_value(json_tree, current, StringField)
        return tree, json_tree

    def create_for_loop_nesting(self, decorator, current, tree, json_tree):
        """
            The function for creating Array object for the loop holding.
            It creates:
            - a for_loop object, e.g: [("for", "for_loop_variable", "loop_iterated_list"), #fields ];
            - JSONSchemaArray object.

        """
        for_loop_condition = list(re.findall(
            RegexConstants.FOR_LOOP_CONDITION, current)[0])
        for_loop_condition[decorator.FOR_LOOP_ITERATED_LIST] = \
            self.change_loop_items_name( decorator, for_loop_condition[decorator.FOR_LOOP_ITERATED_LIST], tree)
        for_loop = [tuple(for_loop_condition)]
        tree.append(for_loop)
        self.set_json_value(json_tree, for_loop_condition[2], JSONSchemaArray)
        return tree, json_tree, for_loop

    def change_loop_items_name(self, decorator, current, tree):
        """
            The function for changing the loop item names.
            For example: a value "classification.scheme" from the list below will be changed to "item.additional.scheme".
            List: [("for","classification", "item.additional"),"classification.scheme",classification.id"] 
        """
        if len(tree) and isinstance(tree[decorator.FOR_LOOP_CONDITION], tuple):
            current = tree[decorator.FOR_LOOP_CONDITION][decorator.FOR_LOOP_ITERATED_LIST]+"." + \
                Regex.remove_prefix(
                    tree[decorator.FOR_LOOP_CONDITION][decorator.FOR_LOOP_VARIABLE], current)
        return current

    def set_json_value(self, json_tree, current, field_type):
        current_values = current.split(".")
        generator = (tag for tag in current_values[:-1]+[None])
        self.set_nested_value(json_tree, generator, field_type, current_values[-1])

    def set_nested_value(self, obj, keys, object_type, value):
        """
            The recursive function that iterates a generator and assigns nested object values depending on conditions.
            Input:
                - ["tag1","tag2", "tag3"]
            Ouput:
                - object of tag1 (object of tag2 (object of tag3))
        """
        for decorator in JSONListGeneratorContextManager(keys):
            key = decorator.current
            if isinstance(obj, JSONSchemaArray):
                obj = obj.__dict__["items"]
            current_properties = setdefaultattr(obj, "properties", {})
            if key is not None:
                next_object = JSONSchemaObject(key)
                if key not in current_properties:
                    current_properties[key] = JSONSchemaObject(key)
                self.set_nested_value(
                    current_properties[key], keys, object_type, value)
            else:
                next_item = object_type(value)
                current_properties[value] = next_item

    def convert(self, formatted_html):
        """
            A function that converts HTML to JSON schema.
        """
        self.soup = BeautifulSoup(formatted_html, "html.parser")
        found_tags = self.find_all_fields(
            HTMLToJSONSchemaConverter.TEMPLATE_FORMULAS)
        print(found_tags)
        self.make_tag_list_tree(found_tags)
        return self.json_tree


# JSON Schema Wrappers:

class BaseJSONSchemaWrapper:

    def __init__(self, name, title=None):
        self.name = name

    def __repr__(self):
        """
            A function that reprs objects to desired structure.
        """
        dictionary = deepcopy(self.__dict__)
        dictionary.pop('name')
        # changing from quotes to the double quotes for JSON compatibilty
        str_dict = json.dumps(repr(dictionary)).replace("'", '\\"')
        # json.loads has a bug and after the first call it still returns still.
        json_object = json.loads(json.loads(str_dict))
        return json.dumps(json_object)


class ObjectJSONSchemaWrapper(BaseJSONSchemaWrapper):

    def __init__(self, name, wrapper_type, title=None, required=[]):
        super().__init__(name, title)
        self.title = title if title is not None else name
        self.type = wrapper_type
        self.required = required


# JSON Schema Objects:


class JSONSchemaObject(ObjectJSONSchemaWrapper):

    def __init__(self, name, title=None, properties=None):
        super().__init__(name, "object", title)
        self.properties = properties if properties is not None else {}


class JSONSchemaArray(ObjectJSONSchemaWrapper):

    def __init__(self, name, title=None, items=None):
        super().__init__(name, "array", title)
        self.items = JSONSchemaObject("items", name, items)

# JSON Schema Fields


class BaseJSONSchemaField:

    def __init__(self, name, field_type, title=None, description=None, required=False):
        self.name = name
        self.type = field_type
        self.title = title
        self.description = description

    def __repr__(self):
        dictionary = deepcopy(self.__dict__)
        dictionary.pop('name')
        dictionary = {k: v for k, v in dictionary.items() if v is not None}
        if HIDE_EMPTY_FIELDS == 1:
            dictionary = {k: v for k, v in dictionary.items() if not (isinstance(
                v, str) and len(v) == 0) and not (isinstance(v, int) and v == 0)}
        return json.dumps(dictionary)


class StringField(BaseJSONSchemaField):

    def __init__(self, name, title="", description="", min_length=0, max_length=0, pattern="", required=False):
        super().__init__(name, "string", title, description, required)
        self.minLength = min_length
        self.maxLength = max_length
        self.pattern = pattern


class DateField(BaseJSONSchemaField):

    def __init__(self, name, title=None, description=None, required=False):
        super().__init__(name, "string", title, description, required)
        self.format = "date"


class BooleanField(BaseJSONSchemaField):

    def __init__(self, name, title=None, description=None, required=False):
        super().__init__(name, "boolean", title, description, required)


class IntegerField(BaseJSONSchemaField):

    def __init__(self, name, title="", description="", minimum=0, maximum=0, required=False):
        super().__init__(name, "integer", title, description, required)
        self.minimum = minimum
        self.maximum = maximum

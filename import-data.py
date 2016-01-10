try: import simplejson as json
except ImportError: import json

from lxml import etree
import io
import sys
import re
import requests

def parse_xml(path):
    f = open(path)
    tree = etree.parse(path)
    return tree

def strip_html(string):
    return re.sub('<[^<]+?>', '', string)

def get_element_id(e):
    return e.attrib.get('Id')

def index_element(e):
    json_obj = tojson(e)
    id = get_element_id(e)
    index_on_elasticsearch(id, json_obj)

def index_on_elasticsearch(id, json_obj):
    resp = requests.put('http://localhost:9200/stackexchange/post/' + id, data = json_obj)

def tojson(e):
    d = etree_to_dict(e)
    return json.dumps(d)

def parse_funcs():
    return {
            'body' : strip_html,
            'id' : int,
            'lasteditoruserid' : int,
            'posttypeid' : int,
            'tags' : str,
            'acceptanswerid' : int,
            'answercount' : int,
            'owneruserid' : int,
            'score' : int,
            'viewcount': int,
            'commentcount' : int,
            'favoritecount' : int
            }

def parse_value(key, value):
    func = parse_funcs().get(key)
    return value if func is None else func(value)

def etree_to_dict(tree):
    d = dict()
    for k in tree.attrib:
        raw_value = tree.get(k)
        dict_key = k.lower()
        value = parse_value(dict_key, raw_value)
        d[dict_key] = value 

    return d

def main(path):
    try:
        tree = parse_xml('./stackexchange/Posts.xml')
    except IOError as e:
        print(e)
        sys.exit(1)

    for el in tree.getroot():
        index_element(el)

if __name__ == '__main__':
    print('Importing posts...')
    main('./stackexchnage/Posts.xml')
    print('Done!')


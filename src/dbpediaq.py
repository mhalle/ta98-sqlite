import sys
import requests
from pprint import pprint
import sqlite3

prefixes = {
    'rdf': "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    'rdfs': "http://www.w3.org/2000/01/rdf-schema#",
    'xsd': "http://www.w3.org/2001/XMLSchema#",
    'owl': "http://www.w3.org/2002/07/owl#",
    'dc': "http://purl.org/dc/terms/",
    'foaf': "http://xmlns.com/foaf/0.1/",
    'vcard': "http://www.w3.org/2006/vcard/ns#",
    'dbp': "http://dbpedia.org/property/",
    'dbo': "http://dbpedia.org/ontology/",
    'dpr': "http://dbpedia.org/resource/",
    'geo': "http://www.geonames.org/ontology#",
    'wgs': "http://www.w3.org/2003/01/geo/wgs84_pos#",
    "prov": "http://www.w3.org/ns/prov#"
  }

lang_capture = {
    'dbo:abstract': 'abstract',
    'rdfs:label': 'name'
}

image_capture = {
    'dbo:thumbnail': 'thumbnail_url',
    'foaf:depiction': 'image_url'
}

gray_capture = {
    'dbo:grayPage': 'gray_page',
    'dbo:graySubject': 'gray_subject'
}


def create_table(conn):
    conn.execute('''create table if not exists dbpedia_info 
                (dbpedia_id text, attr_name text, attr_value text, lang text)''')
    
def lang_accessor(m):
    try:
        val = m['@value']
        lang = m['@language']
        return (val, lang)
    except (KeyError, TypeError):
        pass
    return [(x['@value'], x['@language']) for x in m]

def get_image_fields(d):
    return get_fields(d, image_capture, lambda x: x['@id'])


def get_gray_fields(d):
    return get_fields(d, gray_capture, lambda x: x['@value'])


def get_lang_fields(d):
    return get_fields(d, lang_capture, lang_accessor)


def get_fields(d, fields, accessor=None):
    if not accessor:
        accessor = lambda x: x

    dprime = {}
    for k, v in fields.items():
        try:
            field_val = d[k]
        except KeyError:
            continue
        dprime[v] = accessor(d[k])

    return dprime

def sub_prefixes(s):
    for k, v in prefixes.items():
        if s.startswith(v):
            s = s.replace(v, '{}:'.format(k))
            break
    return s

def simplify(d):
    ret = {}
    for field_name, field_value_list in d.items():
        k = sub_prefixes(field_name)
        v = field_value_list
        ret[k] = v

    return ret


if __name__ == '__main__':
    title = '_'.join(sys.argv[1:])

    url = 'http://dbpedia.org/sparql/'
    resource = 'http://dbpedia.org/resource/{}'.format(title)
    query = 'DESCRIBE <{}>'.format(resource)
    data = {
        'query': query,
        'format': 'application/x-json+ld'
        # 'format': 'application/rdf+json'
    }
    ret = requests.post(url, data=data).json()

    graph = ret['@graph']

    for e in graph:
        if e['@id'] == resource:
            break
    raw_fields = e

    ns_fields = simplify(raw_fields)

    print(get_gray_fields(ns_fields))
    print(get_lang_fields(ns_fields))
    print(get_image_fields(ns_fields))

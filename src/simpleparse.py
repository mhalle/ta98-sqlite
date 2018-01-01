import ta98
import sys
from pprint import pprint

field_replacement = {
    "FMA_identifier":   "fma_id",
    "FMA_parent":       "fma_parent",
    "FMA_ancestors":    "fma_ancestors",
    'FMA_name':         "fma_name",
    "TA98_redirection_note":    "redirection_note",
    "TA98_Latin_preferred_term": "latin_preferred_term",
    "TA98_English_equivalent":  "english_equivalent",
    "TA98_English_synonym":     "english_synonym",
    "TA98_footnote":            "footnote",
    "Entity_ID_number":         "entity_id_number",
    "TA98_Latin_official_synonym": "latin_official_synonym",
    "TA98_ancestors":            "ancestors",
    "Type_of_entity":            "type_of_entity",
    "TA98_correction_note":      "correction_note",
    "TA98_English_source_term":  "english_source_term",
    "TA_code":                   "id",
    "TA98_parent":               "parent",
    "TA98_Latin_precursor_term": "latin_precursor_term",
    "TA98_RAT_note":             "rat_note",
    "Properties":                 "properties",
    "Female_gender": "female_gender",
    "Male_gender": "male_gender",
    "Immaterial": "immaterial",
    "Non_physical": "non_physical",
    "Bilaterality": "bilaterality",
    "Variant": "variant",
    "Composite_property": "composite_property"
}

import sqlite3


def createDbTables(conn):
    cur = conn.cursor()
    cur.execute('''create table if not exists ta98 
        (id text primary key, 
        english_equivalent text, latin_preferred_term text,
        english_synonym text,
        latin_official_synonym text, 
        english_source_term text,
        latin_precursor_term text,
        parent_id text, parent_name text,
        fma_id text, fma_name text, fma_parent_id text, fma_parent_name text, 
        entity_id_number text,        
        type_of_entity text,
        redirection_note text, 
        footnote text, 
        correction_note text,
        problem_note text,
        rat_note text,
        female_gender boolean,
        male_gender boolean,
        immaterial boolean,
        variant boolean,
        composite_property boolean
          )''')
    return conn


def convertParsedOutput(indict):
    outdict = {}
    for k, v in indict.items():
        outdict[field_replacement[k]] = v

    outdict['properties'] = [field_replacement[x]
                             for x in outdict['properties']]
    return outdict


def main():
    filenames = sys.argv[1:]
    for filename in filenames:
        with open(filename) as fp:
            results = ta98.parse(fp)
            pprint(results)
            # pprint(convertParsedOutput(results))

if __name__ == '__main__':
    main()

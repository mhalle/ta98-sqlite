import ta98
import sys
import sqlite3


# more convenient names
field_replacement = {
    "FMA_identifier":   "fma_id",
    "FMA_parent":       "fma_parent",
    "FMA_ancestors":    "fma_ancestors",
    'FMA_name':         "fma_name",
    "TA98_redirection_note":    "redirection_note",
    "TA98_Latin_preferred_term": "name_la",
    "TA98_English_equivalent":  "name_en",
    "TA98_English_synonym":     "english_synonym",
    "TA98_footnote":            "footnote",
    "Entity_ID_number":         "entity_id_number",
    "TA98_Latin_official_synonym": "latin_official_synonym",
    "TA98_ancestors":            "ancestors",
    "Type_of_entity":            "type_of_entity",
    "TA98_correction_note":      "correction_note",
    "TA98_problem_note":         "problem_note",
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

def createDbTables(conn):
    cur = conn.cursor()
    cur.execute('pragma foreign_keys=1;')
    cur.execute('''create table if not exists ta98 
        (id text primary key, 
        name_en text,
        name_la text,
        parent_id text, parent_name text,
        fma_id text, fma_parent_id text,  
        entity_id_number text,        
        type_of_entity text,
        female_gender boolean,
        male_gender boolean,
        immaterial boolean,
        bilaterality boolean,
        variant boolean,
        composite_property boolean
          )''')

    cur.execute('''create table if not exists synonyms
        (id text, 
        synonym text, 
        synonym_type text, 
        lang text,
        foreign key(id) references ta98(id)
        )''')

    cur.execute('''create table if not exists hierarchy
        (id text,
        ancestor_id text,
        ancestor_name text,
        hierarchy_level integer,
        foreign key(id) references ta98(id)
        )''')

    cur.execute('''create table if not exists fma_names
        (fma_id text primary key,
        fma_name text)''')

    cur.execute('''create table if not exists fma_hierarchy
        (id text,
        ancestor_id text,
        ancestor_name text,
        hierarchy_level integer,
        foreign key(id) references ta98(id)
        )''')

    cur.execute('''create table if not exists notes
        (id text,
        note_text text,
        note_type text,
        foreign key(id) references ta98(id)
    )''')

    return conn

def convertParsedOutput(indict):
    outdict = {}
    for k, v in indict.iteritems():
        outdict[field_replacement[k]] = v

    outdict['properties'] = [field_replacement[x]
                             for x in outdict['properties']]

    outdict['type_of_entity'] = outdict['type_of_entity'].lower()
    return outdict

def pcheck(r, propname):
    return propname in r['properties']

def acheck(r, field):
    try:
        return r[field]
    except KeyError:
        return None

def aicheck(r, field, idx):
    try:
        return r[field][idx]
    except KeyError:
        return None

def dbmain():
    conn = sqlite3.connect(sys.argv[1])
    createDbTables(conn)
    cur = conn.cursor()
    filenames = sys.argv[2:]
    for filename in filenames:
        with open(filename) as fp:
            r = convertParsedOutput(ta98.parse(fp))
            values = (r['id'],
                      acheck(r, 'name_en'),
                      acheck(r, 'name_la'),
                      aicheck(r, 'parent', 0),
                      aicheck(r, 'parent', 1),
                      acheck(r, 'fma_id'),
                      aicheck(r, 'fma_parent', 0),
                      acheck(r, 'entity_id_number'),
                      acheck(r, 'type_of_entity'),
                      pcheck(r, 'female_gender'),
                      pcheck(r, 'male_gender'),
                      pcheck(r, 'immaterial'),
                      pcheck(r, 'bilaterality'),
                      pcheck(r, 'variant'),
                      pcheck(r, 'composite_property'))
            cur.execute('''insert or ignore into ta98
                (id, 
                name_en, name_la,
                parent_id, parent_name,
                fma_id, fma_parent_id,  
                entity_id_number,        
                type_of_entity,
                female_gender,
                male_gender,
                immaterial,
                bilaterality,
                variant,
                composite_property) values 
                (?,?,?, ?,?,?, ?,?,?, ?,?,?, ?,?,?);''', values)

            # HIERARCHY
            ancestors = r.get('ancestors', [])
            if len(ancestors) > 1:
                for i, ancestor in enumerate(ancestors[1:]):
                    cur.execute('''insert or ignore into hierarchy
                        (id, ancestor_id, ancestor_name, hierarchy_level) values (?,?,?,?);''',
                                [r['id'], ancestor[0], ancestor[1], i+1])

            # FMA ANCESTORS
            ancestors = r.get('fma_ancestors', [])
            cur.executemany('''insert or ignore into fma_names (fma_id, fma_name) values (?, ?)''',
                            ancestors)

            if len(ancestors) > 1:
                for i, ancestor in enumerate(ancestors[1:]):
                    cur.execute('''insert or ignore into fma_hierarchy
                        (id, ancestor_id, ancestor_name, hierarchy_level) values (?,?,?,?);''',
                                [r['id'], ancestor[0], ancestor[1], i+1])

            for note_type in ('footnote', 'problem_note', 'correction_note',
                              'rat_note', 'redirection_note'):
                if r.has_key(note_type):
                    field_val = r[note_type]
                    if not isinstance(field_val, list):
                        field_val = [field_val]
                    cur.executemany('''insert or ignore into notes (id, note_type, note_text)
                                values (?, ?, ?);''',
                                    [(r['id'], note_type, x) for x in field_val])

            for synonym_field, synonym_lang in (('name_en', 'en'),
                                                ('name_la', 'la'),
                                                ('latin_official_synonym', 'la'),
                                                ('english_source_term', 'en'),
                                                ('latin_precursor_term', 'la'),
                                                ('english_synonym', 'en')):
                if r.has_key(synonym_field):
                    field_val = r[synonym_field]
                    if not isinstance(field_val, list):
                        field_val = [field_val]
                    cur.executemany('''insert or ignore into synonyms
                                    (id, synonym, synonym_type,lang) values 
                                    (?,?,?,?)''',
                                    [(r['id'], x, synonym_field, synonym_lang) for x in field_val])


            conn.commit()
    conn.close()


def getAllAttrs():
    filenames = sys.argv[1:]
    allAttrs = set()
    for filename in filenames:
        with open(filename) as fp:
            results = ta98.parse(fp)
            allAttrs.update(results.keys())
    print allAttrs

def getAllProps():
    filenames = sys.argv[1:]
    allProps = set()
    for filename in filenames:
        with open(filename) as fp:
            results = ta98.parse(fp)
            try:
                p = set(results['Properties'])
            except KeyError:
                continue
            allProps.update(p)
    print allProps

if __name__ == '__main__':
    dbmain()

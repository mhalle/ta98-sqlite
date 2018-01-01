import sys
import sqlite3

"""fix parent_id's in ta98 and the hierarchy table to deal with the
   gender-specific suffixes. """

def fix_gender_parents(dbname):
    db = sqlite3.connect(dbname)
    db.row_factory = sqlite3.Row

    qres = db.execute('''select id, name_en, parent_id, 
                      male_gender, female_gender from ta98''')

    structures = {}
    for r in qres:
        structures[r['id']] = r
    

    fixes = []
    for s in structures.values():
        if not s['parent_id']:
            continue
        if s['parent_id'] in structures:
            continue

        parent_id = s['parent_id']
        if s['male_gender']:
            new_parent_id = parent_id + 'M'
        elif s['female_gender']:
            new_parent_id = parent_id + 'F'
        else:
            if parent_id + 'F' in structures:
                new_parent_id = parent_id + 'F'
            else:
                new_parent_id = parent_id + 'M'
        fixes.append((new_parent_id, s['id']))

    db.executemany('''update ta98 set parent_id = ? where id = ?''', fixes)
    db.commit()


    # rebuild hierarchy
    qres = db.execute('''select id, name_en, parent_id, 
                      male_gender, female_gender from ta98''')

    structures = {}
    hierarchies = {}
    for r in qres:
        structures[r['id']] = r

    for s in structures.values():
        sid = s['id']
        hierarchies[sid] = this_hierarchy = []

        parent_id = s['parent_id']
        level = 1
        while parent_id:
            parent = structures[parent_id]
            this_hierarchy.append((parent_id, parent['name_en'], level))
            parent_id = parent['parent_id']
            level += 1

    statements = []
    for sid,hier_level_list in hierarchies.items():  
        structure_name = structures[sid]['name_en']
        for ancestor_id, ancestor_name, level in hier_level_list:
            statements.append((sid, ancestor_id, ancestor_name, level))
    
    db.execute('delete from hierarchy')

    db.executemany('''insert into hierarchy 
                    (id, ancestor_id, ancestor_name, hierarchy_level)
                    values (?,?,?,?)''', statements)
    db.commit()






     



if __name__ == '__main__':
    dbname = sys.argv[1]
    fix_gender_parents(dbname)
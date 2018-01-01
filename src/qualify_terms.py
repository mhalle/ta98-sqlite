import sys
import sqlite3
import re
from collections import namedtuple
import operator


def getHierarchy(cur, id):
    hierarchy = cur.execute("""select ancestor_name from hierarchy join ta98
             on hierarchy.id = ta98.id where ta98.id = ?
             order by hierarchy_level""", [id])
    hierarchy = [h[0] for h in hierarchy]
    return hierarchy


class StructureInfo(object):

    def __init__(self, name, id, parent_id, count):
        self.name = name
        self.id = id
        self.parent_id = parent_id
        self.count = count
        self.needs_parent = False
        self.hstring = None


def uniqify(dbname):
    db = sqlite3.connect(dbname)
    db.row_factory = sqlite3.Row

    structures = {}
    for e in db.execute('''select ta98.name_en as name, ta98.id as id, parent_id, count
                                from ta98 join 
                                (select name_en, count(1) as count from ta98
                                 group by name_en) dups on ta98.name_en = dups.name_en
                                order by ta98.name_en
                                '''):
        structures[e['id']] = StructureInfo(e['name'],
                                            e['id'],
                                            e['parent_id'],
                                            e['count'])

    # first pass: identify need for parents
    for s in structures.values():
        if s.count > 1:
            s.needs_parent = True
            continue

        last_word = s.name.split()[-1]
        if last_word in set(['shaft',
                             'branch',
                             'part',
                             'layer',
                             'surface',
                             'substance',
                             'constructor',
                             'head',
                             'horn',
                             'ala',
                             'base',
                             'alveus',
                             'angle',
                             'branches',
                             'divisions',
                             'extremity',
                             'node',
                             'root',
                             'segment',
                             'belly',
                             'chamber',
                             'lip',
                             'hook',
                             'zone',
                             'stripe',
                             'ridge',
                             'ridges',
                             'lobe']):
            s.needs_parent = True

    # second pass: assemble
    for s in structures.values():
        uname = s.name
        needs = s.needs_parent
        parent_id = s.parent_id
        while needs and parent_id != None:
            try:
                pstruct = structures[parent_id]
            except KeyError:
                uname = '%s (GENDER ERROR)' % (uname,)
                break

            parent_name = pstruct.name
            if (parent_name.endswith('human body') or
                    parent_name == 'regional lymph nodes'):
                break
            uname = '%s OF %s' % (uname, parent_name)
            needs = pstruct.needs_parent
            parent_id = pstruct.parent_id
        s.hstring = uname

    sorted_structures = sorted(
        list(structures.values()), key=operator.attrgetter('hstring'))

    fully_qualified_names = []
    for s in sorted_structures:
        fully_qualified_names.append((s.id, s.hstring))

    db.execute("delete from synonyms where synonym_type = 'nac:qualified_name'")
    db.executemany("""insert or ignore into synonyms 
                           (id, synonym, synonym_type, lang) 
                           values (?, ?, 'nac:qualified_name', 'en')""",
                           fully_qualified_names)
    db.commit()

if __name__ == '__main__':
    dbname = sys.argv[1]
    uniqify(dbname)

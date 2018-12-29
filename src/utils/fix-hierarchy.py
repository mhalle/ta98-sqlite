import sqlite3
import sys


def fix_hierarchy(dbfilename):
    with sqlite3.connect(dbfilename) as conn:
        cur = conn.cursor()

        rows = cur.execute('select id, parent_id, name_en from ta98')


        index = {}

        for r in rows:
            index[r[0]] = {'id': r[0], 'parent_id': r[1], 'name': r[2]}

        for n in index.values():
            parent_id = n['parent_id']
            if parent_id:
                n['parent'] = index[n['parent_id']]
                n['parent_name'] = n['parent']['name']
            else:
                n['parent'] = None
            

        hierarchy_rows = []
        for n in index.values():
            p = n['parent']
            level = 1
            while p:
                hierarchy_rows.append((n['id'], p['id'], p['name'], level, 0))
                p = p['parent']
                level += 1



        cur.execute('drop table if exists hierarchy_new')
        cur.execute("""create table hierarchy_new 
            (id text,
            ancestor_id text,
            ancestor_name text,
            hierarchy_level integer,
            hierarchy_depth integer,
            foreign key(id) references ta98(id)
            )
            """)

        cur.executemany('''insert into hierarchy_new
        (id, ancestor_id, ancestor_name, hierarchy_level, hierarchy_depth)
        values (?, ?, ?, ?, ?)''', hierarchy_rows)


if __name__ == '__main__':
    fix_hierarchy(sys.argv[1])

                

            
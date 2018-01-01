import sqlite3
import sys

def add_hierarchy_depth(dbfilename):

    with sqlite3.connect(dbfilename) as conn:
        cur = conn.cursor()

        cur.execute('''create table if not exists hierarchy_new
            (id text,
            ancestor_id text,
            ancestor_name text,
            hierarchy_level integer,
            hierarchy_depth integer,
            foreign key(id) references ta98(id)
        )''')

        cur.execute('''insert into  hierarchy_new
            (id, ancestor_id, ancestor_name, hierarchy_level, hierarchy_depth)
            select hierarchy.id, ancestor_id, ancestor_name, hierarchy_level, 
            (max_depth - hierarchy_level) from
            hierarchy join 
            (select id, max(hierarchy_level) 
            as max_depth from hierarchy group by id) m on hierarchy.id = m.id;
         ''')
        cur.execute('alter table hierarchy rename to hierarchy_prev')
        cur.execute('alter table hierarchy_new rename to hierarchy')




if __name__ == '__main__':
    add_hierarchy_depth(sys.argv[1])
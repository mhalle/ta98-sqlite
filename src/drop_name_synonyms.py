import sqlite3
import sys


def drop_name_synonyms(dbfilename):
    with sqlite3.connect(dbfilename) as conn:
        cur = conn.cursor()
        cur.execute("""delete from synonyms 
            where synonym_type in ('name_en', 'name_la')""")
        cur.execute('vacuum')


if __name__ == '__main__':
    drop_name_synonyms(sys.argv[1])
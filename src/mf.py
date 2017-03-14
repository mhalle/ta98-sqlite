import sqlite3
import sys
import wikipedia


if __name__ == '__main__':
    conn = sqlite3.connect(sys.argv[1])
    cur = conn.cursor()

    cur.execute('pragma foreign_keys = OFF')
    idlist = list(cur.execute('''select distinct id, source_id, name_en from ta98 
               where male_gender or female_gender'''))

    for i,o,n in idlist:
        r = wikipedia.search(i)
        if not len(r):
            r = wikipedia.search(n)


        if len(r):
            cur.execute('insert or ignore into wikipedia (id, name_en, wp_title) values (?,?,?)',
            [i, n, r[0]])

            print i, n, r[0]
        else:
            print 'no match', i, n
        conn.commit()

    conn.close()
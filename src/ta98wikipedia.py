import sqlite3
import wikipedia
import sys

# do a wikipedia query on all TA98 terms.
# NOTE that there will be a handful of spurious query results
# (most having to with athletic team results) that will have to
# be manually removed.
# hint: delete terms that match years (20??), ones that include
# "olympic", "grant prix" "season", "cycling", "Turkish".

if __name__ == '__main__':
    ta98 = sqlite3.connect(sys.argv[1])
    wpedia = ta98  # used to be separate DBs

    wpedia.execute('''create table if not exists wikipedia
                    (id text,
                    name_en text,
                    wp_title text)''')

    ta_info = list(ta98.execute('select id,name_en from ta98'))

    for ta_id, ta_name in ta_info:
        already_done = list(wpedia.execute('''select * from wikipedia where id=?''', (ta_id,)))
        if already_done:
            print("done:", already_done)
            continue
        try:
            search_results = wikipedia.search(ta_id)
        except ValueError:  # sometimes we have spurious errors
            continue
        for s in search_results:
            wpedia.execute('''insert or ignore into wikipedia
                (id, name_en, wp_title) values 
                (?,?,?)''', (ta_id, ta_name, s))
            print((ta_id, ta_name, s))
            wpedia.commit()

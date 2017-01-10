import sqlite3
import wikipedia
import sys

# add wikipedia page info for all existing mappings in the main db table
if __name__ == '__main__':
    wpedia = sqlite3.connect(sys.argv[1])

    wpedia.execute('''create table if not exists images
                    (wikipedia_title text,
                    image_url text)''')

    wpedia.execute('''create table if not exists page_info
                    (wikipedia_title text primary key,
                    summary text,
                    page_url text,
                    parent_id numeric,
                    revision_id numeric)''')

    titles = list(wpedia.execute('''select distinct wikipedia_title from _'''))

    for tv in titles:
        t = tv[0]
        print t
        already_done = list(wpedia.execute('''select count(1)
                            from page_info where wikipedia_title=?''', (t,)))[0][0]
        if already_done:
            continue
        try:
            page = wikipedia.page(t)
        except:  # catch everything and ignore
            continue

        values = (t, page.summary, page.url, int(page.parent_id), int(page.revision_id))
        wpedia.execute('''insert or ignore into page_info
                        (wikipedia_title, summary, page_url, parent_id, revision_id) values
        (?,?,?,?,?)''', values)


        wpedia.executemany('''insert or ignore into images
                (wikipedia_title, image_url) values (?,?)''', [(t, i) for i in page.images])
        wpedia.commit()


    wpedia.close()




    
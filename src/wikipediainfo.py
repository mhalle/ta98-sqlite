import sqlite3
import wikipedia
import sys

# add wikipedia page info for all existing mappings in the main db table
if __name__ == '__main__':
    wpedia = sqlite3.connect(sys.argv[1])

    wpedia.execute('''create table if not exists wp_images
                    (wp_title text,
                    image_url text)''')

    wpedia.execute('''create table if not exists wp_page_info
                    (wp_title text primary key,
                    page_url text,
                    summary text,
                    parent_id integer,
                    revision_id integer)''')

    titles = set(x[0] for x in wpedia.execute('select distinct wp_title from wikipedia'))
    titles_done = set(x[0] for x in wpedia.execute('select wp_title from wp_page_info'))
    for t in (titles - titles_done):
        print(t)
        page = None
        try:
            page = wikipedia.page(t)
        except Exception as e:  # catch everything and ignore
            print(e, file=sys.stderr)
            try:
                page = wikipedia.page(t.replace(' ', '_'), auto_suggest=False)
            except Exception as e:
                print(e, file=sys.stderr)
        if not page:
            continue

        values = (t, page.summary, page.url, int(page.parent_id), int(page.revision_id))
        wpedia.execute('''insert or ignore into wp_page_info
                        (wp_title, summary, page_url, parent_id, revision_id) values
        (?,?,?,?,?)''', values)


        wpedia.executemany('''insert or ignore into wp_images
                (wp_title, image_url) values (?,?)''', [(t, i) for i in page.images])
        wpedia.commit()


    wpedia.close()




    

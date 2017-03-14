import apsw
import sys




def addFTS(dbfile):
    db = apsw.Connection(dbfile)
    cur = db.cursor()
    cur.execute('''drop table synonyms_fts''')
    cur.execute('''create virtual table if not exists
        synonyms_fts 
        using fts5(name_en, name_la, synonym, wp_title, 
        summary, id unindexed, prefix=2, prefix=3)'''
               )

    cur.execute('''insert into
            synonyms_fts (name_en, name_la, synonym, wp_title, summary, id)
            select distinct 
                ta98.name_en, ta98.name_la, 
                synonyms.synonym, wikipedia.wp_title, wp_page_info.summary, synonyms.id
                from synonyms 
                join ta98 on synonyms.id=ta98.id
                left join wikipedia on synonyms.id=wikipedia.id
                inner join wp_page_info on wikipedia.wp_title=wp_page_info.wp_title''')

def query(dbfile, q):
    db = apsw.Connection(dbfile)
    cur = db.cursor()
    rows = cur.execute("""select ta98.name_en, ta98.id, synonyms_fts.rank
                    from synonyms_fts join ta98 
                    on synonyms_fts.id=ta98.id
                    where synonyms_fts match ? 
                    order by bm25(synonyms_fts, 40.0, 40.0, 5.0, 5.0, 1.0)""", [q])
    for row in rows:
        print row
if __name__ == '__main__':
    addFTS(sys.argv[1])
    query(sys.argv[1], sys.argv[2])



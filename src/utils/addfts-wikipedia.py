import apsw
import sys




def addFTS(dbfile):
    db = apsw.Connection(dbfile)
    cur = db.cursor()
    cur.execute('''drop view if exists ta98_search''')
    cur.execute('''drop table if exists synonyms_fts''')
    cur.execute('''create virtual table
        synonyms_fts 
        using fts5(name_en, name_la, synonym, wp_title, 
        summary, id unindexed, prefix=4)'''
               )

    #cur.execute('''insert into
    #        synonyms_fts (name_en, name_la, synonym, wp_title, summary, id)
    #        select distinct 
    #            ta98.name_en, ta98.name_la, 
    #           synonyms.synonym, wikipedia.wp_title, wp_page_info.summary, synonyms.id
    #           from synonyms 
    #            join ta98 on synonyms.id=ta98.id
    #            left join wikipedia on synonyms.id=wikipedia.id
    #            inner join wp_page_info on wikipedia.wp_title=wp_page_info.wp_title''')

#     cur.execute('''insert into
#             synonyms_fts (name_en, name_la, synonym, wp_title, summary, id)
#             select distinct 
#                 ta98.name_en, ta98.name_la, 
#                 group_concat(distinct synonyms.synonym), wikipedia.wp_title, wp_page_info.summary, synonyms.id
#                 from synonyms 
#                 join ta98 on synonyms.id=ta98.id
#                 left join wikipedia on synonyms.id=wikipedia.id
#                 inner join wp_page_info on wikipedia.wp_title=wp_page_info.wp_title 
#                 group by ta98.id''')


    cur.execute('''insert into
              synonyms_fts (name_en, name_la, synonym, wp_title, summary, id)
              select distinct
                ta98.name_en, ta98.name_la,
                group_concat(distinct synonyms.synonym), wikipedia.wp_title, wp_page_info.summary, synonyms.id
                from synonyms
                left join ta98 on synonyms.id=ta98.id
                left join wikipedia on synonyms.id=wikipedia.id
                left join wp_page_info on wikipedia.wp_title=wp_page_info.wp_title
                group by ta98.id''')

def query(dbfile, q):
    db = apsw.Connection(dbfile)
    cur = db.cursor()
    rows = cur.execute("""select distinct ta98.name_en, ta98.id, synonym, wp_title, rank
                    from synonyms_fts join ta98 
                    on synonyms_fts.id=ta98.id
                    where synonyms_fts match ?
                    order by bm25(synonyms_fts, 100.0, 100.0, 5.0, 5.0, 1.0)""", [q])
    for row in rows:
        print(row)
if __name__ == '__main__':
    addFTS(sys.argv[1])
    query(sys.argv[1], sys.argv[2])



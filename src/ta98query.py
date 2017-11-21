import sqlite3
import sys
from collections import namedtuple


Synonym = namedtuple('Synonym', 'id synonym synonym_type lang')

EntryBase = namedtuple('Entry', ['id', 'source_id', 'name_en', 'name_la',
                                 'parent_id', 'parent_name', 'fma_id',
                                 'fma_parent_id', 'entity_id_number',
                                 'type_of_entity', 'female_gender',
                                 'male_gender', 'immaterial', 'bilaterality',
                                 'variant', 'composite_property'])

WikipediaInfo = namedtuple('WikipediaInfo', 'wp_title page_url summary image_urls')


class Entry(EntryBase):
    __slots__ = ()
    @property
    def gender_specific(self):
        return self.male_gender or self.female_gender


class TA98(object):
    def __init__(self, dbfilename):
        self.dbfilename = dbfilename
        self.dbconn = sqlite3.connect(dbfilename)
        self.dbconn.row_factory = sqlite3.Row

    def getSynonym(self, term=None, ta_id=None, regex=False, like=False):
        ret = self.getSynonyms(term, ta_id, regex, like)
        return ret[0] if ret and len(ret) else None

    def getSynonyms(self, term=None, ta_id=None, regex=False, like=False):
        if term != None:
            if regex:
                matcher = 'glob'
            elif like:
                matcher = 'like'
            else:
                matcher = '='
            q = 'select * from synonyms where synonym {0} ?'.format(matcher)
            arg = term
        elif ta_id != None:
            arg = ta_id
            q = 'select * from synonyms where id = ?'
        else:
            # raise Exception
            return None
        qresults = [Synonym(*x) for x in self.dbconn.execute(q, [arg])]
        return qresults

    def getEntry(self, term=None, ta_id=None, regex=False, like=False):
        ret = self.getEntries(term, ta_id, regex, like)
        return ret[0] if ret and len(ret) else None

    def getEntries(self, term=None, ta_id=None, regex = False, like = False):
        if term != None:
            if regex:
                matcher = 'glob'
            elif like:
                matcher = 'like'
            else:
                matcher = '='
            q = 'select distinct * from ta98 where name_en {0} ? or name_la {0} ?'.format(matcher)
            arg = [term, term]
        elif ta_id != None:
            arg = [ta_id]
            q = 'select distinct * from ta98 where id = ?'
        else:
            # raise Exception
            return None
        qresults = [Entry(*x) for x  in self.dbconn.execute(q, arg)]
        return qresults

    def getWikipediaInfo(self, id):
        q = 'select wp_title from wikipedia where id = ?'
        title = self.dbconn.execute(q, [id]).fetchone()
        if not title: 
            return None
        title = title[0]
        q = 'select * from wp_page_info where wp_title = ?'
        page_info = self.dbconn.execute(q, [title]).fetchone()
        if not page_info:
            return None
        q = 'select image_url from wp_images where wp_title = ?'
        image_urls = [x[0] for x in self.dbconn.execute(q, [title])]
        w = WikipediaInfo(title, page_info['page_url'], page_info['summary'], image_urls)
        return w

if __name__ == '__main__':
    ta = TA98(sys.argv[1])
    term = ' '.join(sys.argv[2:])

    t = ta.getSynonyms(term, regex=True)
    ids = set([x.id for x in t])
    for b in ids:
        ee = ta.getEntry(ta_id=b)
        print(ee.name_en)

    sys.exit(0)
    i = ta.getSynonyms(ta_id=t.id)
    print(i)

    e = ta.getEntry(ta_id = t.id)
    print(e)

    print(ta.getWikipediaInfo(t.id))
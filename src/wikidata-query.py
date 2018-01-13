import sqlite3
import sys
from SPARQLWrapper import SPARQLWrapper, JSON


def write_entities(dbfilename, entities):
    with sqlite3.connect(dbfilename) as conn:
        cur = conn.cursor()

        cur.execute("""drop table if exists wikidata""")

        cur.execute("""create table wikidata 
            (id text,
            wd_entity text,
            foreign key(id) references ta98(id))"""
        )

        cur.executemany("""insert into wikidata (id, wd_entity) 
                          values (?, ?)""", entities)
    

def get_labels(entities):

    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

    for id, entity in entities:
        query = """SELECT ?entity ?label WHERE {
            SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
            <http://www.wikidata.org/entity/""" + entity + "> rdfs:label ?label.}"
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        labels = []
        for r in results['results']['bindings']:
            yield (entity, r['label']['value'], r['label']['xml:lang'])

        

def wikidata_query():
    query = """SELECT ?concept ?taid WHERE {
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
  ?concept wdt:P1323 ?taid.
  MINUS {?concept wdt:P31/wdt:P279* wd:Q11266439.
  ?concept wdt:P1323 ?taid.}}"""

    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return [[x['taid']['value'],
            x['concept']['value'].replace('http://www.wikidata.org/entity/', '')]
            for x in results['results']['bindings']]
            


if __name__ == '__main__':
    entities = wikidata_query()
    write_entities(sys.argv[1], entities)

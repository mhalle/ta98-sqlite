# TA98 (plus wikipedia) to sqlite parser

This repository contains python scripts to parse the HTML representation of the 
English tree view of Terminologia Anatomica 1998 on-line version found at 
http://www.unifr.ch/ifaa/Public/EntryPage/TA98%20Tree/Alpha/All%20KWIC%20EN.htm

Terminologia Anatomica is a standard for naming anatomical structures in the human body. 
It was ratified by the International Federation of Associations of Anatomists and 
maintained by the University of Fribourg (Switzerland). Please see their site 
(http://www.unifr.ch/ifaa/) for more information.

The respository contains the following subdirectories:
 - `src`: python parsing and database creation code
  * `ta98.py`: HTML parser for TA98 web pages based on BeautifulSoup 4
  * `buildta98db.py`: uses ta98.py to build main sqlite db given a list of HTML pages.  
  You may have to break up the pages into groups to deal with UNIX shell/command line
  limitations (do 0* files and [1-9]* files separately with the same database file).
  * `ta98wikipedia.py`: builds the TA98 to wikipedia table
  * `wikipediainfo.py`: looks up all the table entries generated by ta98wikipedia.py and
  stores wikipedia page info for those pages. 
 - `ta98-web-src`: crawled copy of the TA98 web site
 - `db`: precompiled sqlite databases
 
 In the `db` directory, the following databases and tables are interesting:
 - `ta98.sqlite`: contains these tables describing TA98 structures
  * `_`: information about each TA98 entry (one row per entry)
  * `synonyms`: all synonyms for each TA98 entry (one row per synonym)
  * `notes`:  notes for each TA98 entry.
  * `hierarchy`: the ancestors of each TA98 entry (one row per ancestor)
  * `fma_names`: mapping of FMA IDs to FMA names
 - `ta98wikipedia.sqlite`: wikipedia information about TA98 terms
  * `_`: mapping from TA IDs to wikipedia titles (one row per title)
  * `page_info`: Information about wikipedia pages, including title, URL, images, and summary.

## Databases and tables
All files are sqlite3 databases that can be accessed using the sqlite3 command line 
program or any number of sqlite3 language bindings.  The tables are designed primarily
for convenience;  they are not fully denormalized in order to make some common queries
possible with a minimal number of joins.

### `ta98.sqlite`
```sql
sqlite> .schema
CREATE TABLE _
        (id text primary key,
        name_en text,
        name_la text,
        parent_id text, parent_name text,
        fma_id text, fma_parent_id text,
        entity_id_number text,
        type_of_entity text,
        female_gender boolean,
        male_gender boolean,
        immaterial boolean,
        bilaterality boolean,
        variant boolean,
        composite_property boolean
          );
CREATE TABLE synonyms
        (id text, 
        synonym text, 
        synonym_type text, 
        lang text);
CREATE TABLE hierarchy
        (id text,
        ancestor_id text,
        ancestor_name text,
        hierarchy_level numeric);
CREATE TABLE fma_names
        (fma_id text primary key,
        fma_name text);
CREATE TABLE fma_hierarchy
        (id text,
        ancestor_id text,
        ancestor_name text,
        hierarchy_level numeric);
CREATE TABLE notes
        (id text,
        note_text text,
        note_type text);

```
### `ta98wikipedia.sqlite`
```sql
sqlite> .schema
-- contains additional wikipedia tables
CREATE TABLE _
        (id text primary key,
        name_en text,
        name_la text,
        parent_id text, parent_name text,
        fma_id text, fma_parent_id text,
        entity_id_number text,
        type_of_entity text,
        female_gender boolean,
        male_gender boolean,
        immaterial boolean,
        bilaterality boolean,
        variant boolean,
        composite_property boolean
      );
CREATE TABLE synonyms
        (id text, 
        synonym text, 
        synonym_type text, 
        lang text);
CREATE TABLE hierarchy
        (id text,
        ancestor_id text,
        ancestor_name text,
        hierarchy_level numeric);
CREATE TABLE fma_names
        (fma_id text primary key,
        fma_name text);
CREATE TABLE fma_hierarchy
        (id text,
        ancestor_id text,
        ancestor_name text,
        hierarchy_level numeric);
CREATE TABLE notes
        (id text,
        note_text text,
        note_type text);

CREATE TABLE wikipedia
        (id text, 
        name_en text, 
        wp_title text);
CREATE TABLE wp_images 
        (wp_title text, 
        image_url text);
CREATE TABLE wp_page_info 
        (wp_title text primary key, 
        page_url text, 
        summary text, 
        parent_id numeric, 
        revision_id numeric);
```
# Example queries
```sql

% sqlite3 ta98.sqlite
sqlite> .header on
-- get all records for 'brain'
sqlite> select id,name_en,name_la,parent_name from _ where name_en like 'brain';

id|name_en|name_la|parent_name
A14.1.03.001|brain|encephalon|central nervous system

-- get all synonyms and parent for ID A16.0.02.007
sqlite> select synonyms.*,_.parent_name 
        from _ join synonyms on _.id=synonyms.id 
        where _.id='A16.0.02.007';

id|synonym|synonym_type|lang|parent_name
A16.0.02.007|axillary process|name_en|en|mammary gland
A16.0.02.007|processus axillaris|name_la|la|mammary gland
A16.0.02.007|processus lateralis|latin_official_synonym|la|mammary gland
A16.0.02.007|axillary tail|english_synonym|en|mammary gland

-- find all terms with english names that contain "ventricle" that are descendants of "brain"
sqlite> select _.name_en,_.name_la,hierarchy.ancestor_name,hierarchy.hierarchy_level 
    from _ join hierarchy on _.id=hierarchy.id 
    where hierarchy.ancestor_name='brain' and name_en like '%ventricle%';

name_en|name_la|ancestor_name|hierarchy_level
medullary striae of fourth ventricle|striae medullares ventriculi quarti|brain|6
fourth ventricle|ventriculus quartus|brain|2
medullary striae of fourth ventricle|striae medullares ventriculi quarti|brain|4
roof of fourth ventricle|tegmen ventriculi quarti|brain|3
third ventricle|ventriculus tertius|brain|3
lateral ventricle|ventriculus lateralis|brain|3
```
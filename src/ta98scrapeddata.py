import sys
import zipfile
import os, os.path

class TA98ScrapedData(object):
    def __init__(self, scraped_zipfile):
        self.scraped_zipfile = scraped_zipfile

    def __enter__(self):
        self.zfile = zipfile.ZipFile(self.scraped_zipfile)
        self.ids = ['A'+y for y in 
                (x[3:].split(' ')[0] for x in self.zfile.namelist() if x.startswith('en')) if y]
        self.ids.remove('A02.5.00.000')  # bug: this isn't the latin version

        return self

    def get_html(self, id, lang='en'):
        idx = id[1:]
        if lang == 'en':
            filename = f'en/{idx} Entity TA98 EN.htm'
        elif lang == 'la':
            filename = f'la/{idx} Latin TA98.htm'
        else:
            raise ValueError("en or la")

        ret = None
        with self.zfile.open(filename, 'r') as fp:
            ret = fp.read()
        return ret

    def items_en(self):
        for i in self.ids:
            yield (i, self.get_html(i, 'en'))

    def items_la(self):
        for i in self.ids:
                yield (i, self.get_html(i, 'la'))


    def keys(self):
        yield from self.ids

    def __exit__(self, type, value, traceback):
        self.zfile.close()



if __name__ == '__main__':
    def main(scraped_zipfile):
        with TAScrapedData(scraped_zipfile) as sinfo:
            list(sinfo.items_la())
            list(sinfo.items_en())


    scraped_zipfile = sys.argv[1]
    main(scraped_zipfile)
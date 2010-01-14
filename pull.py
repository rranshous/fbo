# try + scrape https://www.fbo.gov/index?mode=list&s=opportunity

from BeautifulSoup import BeautifulSoup as BS
from urllib2 import urlopen
import re
from datetime import datetime
from urlparse import parse_qs,urljoin,urlsplit
from mako.template import Template
import pickle
from urllib import quote_plus
from weblog.html_to_xhtml import html_to_xhtml
from weblog.rfc3339 import rfc3339

TITLE = 'FBO.gov listing'
DESCRIPTION = 'A feed for the opportunities on fbo.gov'
VERSION = '1.1'
URL = 'http://mypubliccode.com/fbo/fbo.atom'

def strip_tags(s):
    return re.sub(r'<[^>]*?>','',s)

def concat_content(el):
    return ' '.join([unicode(x).strip() for x in el.contents])

def get_rows(url):
    url_info = urlsplit(url)
    action_url = "%s://%s%s" % (url_info.scheme,
                              url_info.netloc,
                              url_info.path)
    try:
        soup = BS(''.join(urlopen(url).readlines()))
    except Exception, ex:
        print 'soup exception'
        raise

    row_class = 'lst-rw'
    td_items = [
        'Opportunity','Agency/Office/Location','Type/Set-aside','Posted On'
    ]
    rows = []
    for row_el in soup.findAll('tr',{'class':re.compile('^lst-rw.*')}):
        row = {}
        for i,data_el in enumerate(row_el.findAll('td')):
            if i == 0:
                # we want to grab the link
                link = data_el.find('a').get('href','')
                id = parse_qs(link).get('id',[''])[0]
                row['id'] = id
                row['url'] = urljoin(action_url,link)

            row[td_items[i]] = strip_tags(concat_content(data_el))
        rows.append(row)
    return rows

def items_from_rows(rows):
    # items have a little more data to them
    now = rfc3339(datetime.now())
    items = []
    for row in rows:
        item = {'updated_at':now}
        item['data'] = row
        item['id'] = row.get('id','')
        item['url'] = row.get('url','')
        item['title'] = row.get('Opportunity','')
        items.append(item)
    return items

def append_archive(items):
    # pickle data is going to be a list of dicts w/ unicodes
    # we are going to add these items to the pickle 
    # first read in pickle
    try:
        with file('archive.data','r') as fh:
            data = pickle.load(fh)
    except (IOError,EOFError):
        data = []
    
    # we probably have overlapping data, don't want that
    for item in items:
        if item.get('id') not in [x.get('id') for x in data]:
            data.insert(0,item)

    with file('archive.data','w') as fh:
        pickle.dump(data,fh)

    return data

def read_feed_archive():
    # return back the list of items
    try:
        with file('archive.data','r') as fh:
            data = pickle.load(fh)
    except (IOError,EOFError):
        data = []
    return data

def update_atom(items):
    # we are going to re-generate the atom feed file from the items
    data = {
        'items':items,
        'id':VERSION,
        'title':TITLE,
        'description':DESCRIPTION,
        'updated_at':rfc3339(datetime.now()),
        'url':URL,
        'xhtmlify':html_to_xhtml
    }

    from mako import exceptions
    try:
        template = Template(filename='atom.mako')
        atom_string = template.render(**data).replace('&','&amp;')
    except:
        print exceptions.text_error_template().render()

    with file('fbo.atom','w') as fh:
        fh.write(atom_string)

    return True


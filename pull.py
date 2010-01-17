# try + scrape https://www.fbo.gov/index?mode=list&s=opportunity

from BeautifulSoup import BeautifulSoup as BS
from urllib2 import urlopen
import re
from datetime import datetime
from urlparse import parse_qs,urljoin,urlsplit
from mako.template import Template
import pickle
from urllib import quote_plus
from django.utils.feedgenerator import Atom1Feed as _Atom1Feed
from functools import partial
from cStringIO import StringIO

ITEM_TITLE_TEMPLATE = "${data.get('Opportunity')}"
ITEM_AUTHOR_NAME = ''
ITEM_AUTHOR_EMAIL = ''
ITEM_AUTHOR_LINK = ''
ITEM_DESCRIPTION_TEMPLATE = """
<div>
    <ul>
    % for k,v in data.iteritems():
    <li style="margin-bottom:1em"><b>${k}:</b><br/>${v}</li>
    % endfor
    </ul>
</div>
"""
ITEM_COPYRIGHT = ''
FEED_TITLE = 'unofficial FBO.gov Oppertunity listing'
FEED_LINK = 'http://mypubliccode.com/fbo/fbo.atom'
FEED_DESCRIPTION = ''
FEED_AUTHOR_EMAIL = ''
FEED_AUTHOR_NAME = ''
FEED_AUTHOR_LINK = ''
FEED_SUBTITLE = ''
FEED_CATEGORIES = ''
FEED_URL = 'http://mypubliccode.com/fbo/fbo.atom'
FEED_COPYRIGHT = ''
FEED_ID = ''
FEED_TTL = ''
URL = 'https://www.fbo.gov/index?mode=list&s=opportuniry'

class EasyAtom1Feed(_Atom1Feed):
    def add_item(self,**kwargs):
        # add item on the feed makes u feed it the title link
        # and description, this is annoying
        title = kwargs.get('title')
        link = kwargs.get('link')
        description = kwargs.get('description')
        del kwargs['link']
        del kwargs['title']
        del kwargs['description']
        return _Atom1Feed.add_item(self,title,link,description,**kwargs)
Atom1Feed = EasyAtom1Feed

def render_template(s,d):
    return Template(s).render(**d)

def strip_tags(s):
    return re.sub(r'<[^>]*?>','',s)

def concat_content(el):
    return ' '.join([unicode(x).strip() for x in el.contents])

def get_rows(url=None):
    url_info = urlsplit(url or URL)
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

            row[td_items[i]] = strip_tags(concat_content(data_el)).strip()
        rows.append(row)
    return rows

def items_from_rows(rows):
    # items have a little more data to them
    now = datetime.now()
    items = []
    for row in rows:
        item = {}
        item['title'] = render_template(ITEM_TITLE_TEMPLATE,{'data':row})
        item['link'] = row.get('url')
        item['pubdate'] = now
        item['author_name'] = ITEM_AUTHOR_NAME
        item['author_email'] = ITEM_AUTHOR_EMAIL
        item['author_link'] = ITEM_AUTHOR_LINK
        item['unique_id'] = row.get('id')
        item['description'] = render_template(ITEM_DESCRIPTION_TEMPLATE,
                                              {'data':row})
        #item['enclosure'] =
        #item['categories'] = 
        item['item_copyright'] = ITEM_COPYRIGHT
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
    unique_new = []
    for item in items:
        if item.get('id') not in [x.get('id') for x in data]:
            unique_new.append(item)

    with file('archive.data','w') as fh:
        pickle.dump(data+unique_new,fh)

    return unique_new

def read_feed_archive():
    # return back the list of items
    try:
        with file('archive.data','r') as fh:
            data = pickle.load(fh)
    except (IOError,EOFError):
        data = []
    return data

def update_atom(items,file_path='fbo.atom'):
    # we are going to re-generate the atom feed file from the items

    # fields that the django feed obj expects for feed details
    feed_data = {
        'title':FEED_TITLE,
        'link':FEED_LINK,
        'description':FEED_DESCRIPTION,
        'language':'EN-us',
        'author_email':FEED_AUTHOR_EMAIL,
        'author_name':FEED_AUTHOR_NAME,
        'author_link':FEED_AUTHOR_LINK,
        'subtitle':FEED_SUBTITLE,
        'categories':FEED_CATEGORIES,
        'feed_url':FEED_URL,
        'feed_copyright':FEED_COPYRIGHT,
        'id':FEED_ID,
        'ttl':FEED_TTL
    }

    # create our Atom feed and give it some items
    feed = Atom1Feed(**feed_data)
    for item in items:
        feed.add_item(**item)
    buffer = StringIO()
    feed.write(buffer,'UTF-8')
    atom_string = buffer.getvalue()

    # write it out to the file
    with file(file_path,'w') as fh:
        fh.write(atom_string)

    return atom_string

